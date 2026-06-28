"""
Claude 键盘控制面板 - FastAPI 服务器
支持按键事件、WebSocket 实时通信、LED 状态管理
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import subprocess
import os
from typing import Optional
from datetime import datetime
import uvicorn
from ssh_manager import ssh_manager

app = FastAPI(title="Claude控制面板", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 状态存储 ──────────────────────────────────────────────
class KeyboardState:
    def __init__(self):
        self.auto_approve: bool = False          # 自动批准拨杆
        self.led_status: list[int] = [0] * 7    # 7 个 LED，0=off 1=on 2=running
        self.lcd_message: str = "Ready"         # LCD 显示消息
        self.current_mode: int = 0              # Mode 0/1/2
        self.task_running: bool = False         # 是否有 Task 在运行
        self.logs: list[dict] = []              # 事件日志

    def add_log(self, action: str, detail: str = ""):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "action": action,
            "detail": detail,
        }
        self.logs.append(entry)
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]
        return entry

state = KeyboardState()

# ── Tmux 会话管理 ──────────────────────────────────────────────
class TmuxManager:
    """Tmux 会话管理器"""
    
    @staticmethod
    def list_sessions() -> list[dict]:
        """列出所有活跃的 tmux 会话"""
        try:
            result = subprocess.run(
                ['tmux', 'list-sessions', '-F', '#{session_name}:#{session_path}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return []
            
            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    parts = line.split(':', 1)
                    session_name = parts[0]
                    session_path = parts[1] if len(parts) > 1 else ''
                    sessions.append({
                        'name': session_name,
                        'path': session_path
                    })
            
            return sessions
        except Exception as e:
            print(f"列出 tmux 会话失败: {e}")
            return []
    
    @staticmethod
    def path_to_session_name(path: str) -> str:
        """将路径转换为反向域名会话名称"""
        # 移除末尾的斜杠
        path = path.rstrip('/')
        # 分割路径
        parts = path.split('/')
        # 过滤空字符串并反转
        parts = [p for p in parts if p]
        parts.reverse()
        # 用点连接
        return '.'.join(parts)
    
    @staticmethod
    def validate_path(path: str) -> tuple[bool, str]:
        """验证路径是否合法"""
        # 检查是否以 / 开头
        if not path.startswith('/'):
            return False, "路径必须是绝对路径"
        
        # 检查是否是根路径
        if path == '/':
            return False, "不允许使用根路径 /"
        
        # 检查路径是否存在
        if not os.path.exists(path):
            return False, f"路径不存在: {path}"
        
        # 检查是否是目录
        if not os.path.isdir(path):
            return False, f"路径不是目录: {path}"
        
        return True, "路径合法"
    
    @staticmethod
    def create_session(path: str) -> dict:
        """创建新的 tmux 会话并激活 Claude"""
        # 验证路径
        is_valid, message = TmuxManager.validate_path(path)
        if not is_valid:
            return {'success': False, 'error': message}
        
        # 生成会话名称
        session_name = TmuxManager.path_to_session_name(path)
        
        try:
            # 检查会话是否已存在
            result = subprocess.run(
                ['tmux', 'has-session', '-t', session_name],
                capture_output=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return {
                    'success': False,
                    'error': f'会话已存在: {session_name}'
                }
            
            # 创建日志目录
            log_dir = os.path.expanduser('~/.claude-server')
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'tmux-{session_name}.log')
            
            # 创建新会话（分离模式）
            subprocess.run(
                ['tmux', 'new-session', '-d', '-s', session_name, '-c', path],
                capture_output=True,
                timeout=10
            )
            
            # 启动 pipe-pane 实时导出日志
            pipe_command = f"cat >> {log_file}"
            subprocess.run(
                ['tmux', 'pipe-pane', '-t', session_name, pipe_command],
                capture_output=True,
                timeout=5
            )
            
            # 发送 Claude 命令
            claude_command = f"cd {path} && claude\n"
            subprocess.run(
                ['tmux', 'send-keys', '-t', session_name, claude_command],
                capture_output=True,
                timeout=5
            )
            
            state.add_log("创建会话", f"{session_name} -> {path}")
            
            return {
                'success': True,
                'session_name': session_name,
                'path': path,
                'log_file': log_file,
                'message': f'已创建会话: {session_name}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'创建会话失败: {str(e)}'
            }
    
    @staticmethod
    def attach_session(session_name: str) -> dict:
        """附加到指定会话"""
        try:
            result = subprocess.run(
                ['tmux', 'has-session', '-t', session_name],
                capture_output=True,
                timeout=3
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'会话不存在: {session_name}'
                }
            
            state.add_log("切换会话", session_name)
            
            return {
                'success': True,
                'message': f'已切换到会话: {session_name}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'切换会话失败: {str(e)}'
            }

tmux_manager = TmuxManager()

# ── WebSocket 连接管理 ──────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        msg = json.dumps(data, ensure_ascii=False)
        dead = []
        for ws in self.active:
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

manager = ConnectionManager()

async def push_state(extra: Optional[dict] = None):
    payload = {
        "type": "state",
        "auto_approve": state.auto_approve,
        "led_status": state.led_status,
        "lcd_message": state.lcd_message,
        "current_mode": state.current_mode,
        "task_running": state.task_running,
        "logs": state.logs[-10:],
    }
    if extra:
        payload.update(extra)
    await manager.broadcast(payload)

# ── LED 流水灯动画 ──────────────────────────────────────────
async def led_chase_animation(duration: float = 3.0):
    """流水灯效果，模拟 Task 运行中"""
    state.task_running = True
    end_time = asyncio.get_event_loop().time() + duration
    pos = 0
    while asyncio.get_event_loop().time() < end_time:
        state.led_status = [0] * 7
        state.led_status[pos % 7] = 2
        state.led_status[(pos + 1) % 7] = 1
        await push_state()
        pos += 1
        await asyncio.sleep(0.12)
    # 动画结束，全灭
    state.led_status = [0] * 7
    state.task_running = False
    await push_state()

# ── REST 接口 ────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    """根页面 - 返回 Vue 前端入口"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Claude Panel</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #0f172a;
                color: #e2e8f0;
                font-family: 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .welcome {
                text-align: center;
                padding: 3rem;
            }
            h1 {
                color: #10b981;
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            p {
                color: #94a3b8;
                font-size: 1.2rem;
                margin-bottom: 2rem;
            }
            .steps {
                background: #1e293b;
                padding: 2rem;
                border-radius: 12px;
                text-align: left;
                margin: 2rem 0;
            }
            code {
                background: #334155;
                padding: 0.25rem 0.5rem;
                border-radius: 4px;
                font-family: 'Menlo', 'Monaco', monospace;
                color: #10b981;
            }
            .btn {
                display: inline-block;
                margin-top: 2rem;
                color: #10b981;
                text-decoration: none;
                padding: 0.75rem 1.5rem;
                border: 2px solid #10b981;
                border-radius: 8px;
                transition: all 0.2s;
            }
            .btn:hover {
                background: #10b981;
                color: white;
            }
        </style>
    </head>
    <body>
        <div class="welcome">
            <h1>🎹 Claude Panel</h1>
            <p>键盘控制面板 + SSH 终端</p>
            <div class="steps">
                <h3 style="color: #e2e8f0; margin-bottom: 1rem;">📦 启动前端开发服务器:</h3>
                <p style="color: #94a3b8; margin: 0.5rem 0;">
                    <code>cd frontend && npm install && npm run dev</code>
                </p>
                <p style="color: #64748b; font-size: 0.9rem; margin-top: 1rem;">
                    前端将在 <code>http://localhost:3000</code> 运行
                </p>
            </div>
            <div style="margin-top: 2rem; color: #475569; font-size: 0.9rem;">
                <p>API 文档: <a href="/docs" style="color: #10b981;">http://localhost:10015/docs</a></p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/ssh", response_class=HTMLResponse)
async def ssh_page():
    """SSH 终端页面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>SSH 终端 - Claude Panel</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: #0f172a;
                color: #e2e8f0;
                font-family: 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
            }
            #app {
                min-height: 100vh;
            }
        </style>
    </head>
    <body>
        <div id="app">
            <div style="display: flex; justify-content: center; align-items: center; min-height: 100vh;">
                <div style="text-align: center;">
                    <h1 style="color: #10b981; margin-bottom: 1rem;">🔗 SSH 终端</h1>
                    <p style="color: #94a3b8; margin-bottom: 2rem;">Vue 版本开发中...</p>
                    <p style="color: #64748b;">请使用 Vue 开发服务器访问完整功能</p>
                    <p style="color: #475569; margin-top: 1rem; font-size: 0.9rem;">
                        运行: <code style="background: #1e293b; padding: 4px 8px; border-radius: 4px;">cd frontend && npm install && npm run dev</code>
                    </p>
                    <a href="/" style="display: inline-block; margin-top: 2rem; color: #10b981; text-decoration: none; padding: 0.75rem 1.5rem; border: 2px solid #10b981; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.background='#10b981'; this.style.color='white'" onmouseout="this.style.background='transparent'; this.style.color='#10b981'">
                        ← 返回控制面板
                    </a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/state")
async def get_state():
    return {
        "auto_approve": state.auto_approve,
        "led_status": state.led_status,
        "lcd_message": state.lcd_message,
        "current_mode": state.current_mode,
        "task_running": state.task_running,
    }

@app.post("/api/key/{key_name}")
async def press_key(key_name: str):
    """
    模拟按键触发
    key_name: mic | yes | no | up | down | enter
    """
    key_name = key_name.lower()
    if key_name not in ("mic", "yes", "no", "up", "down", "enter"):
        return JSONResponse({"error": "未知按键"}, status_code=400)

    actions = {
        "mic":   ("麦克风", "开始语音输入"),
        "yes":   ("YES",    "确认操作"),
        "no":    ("NO",     "拒绝操作"),
        "up":    ("上键",   "向上导航"),
        "down":  ("下键",   "向下导航"),
        "enter": ("ENTER",  "提交/执行"),
    }
    label, detail = actions[key_name]
    entry = state.add_log(label, detail)

    # 模拟 Task 运行动画
    state.lcd_message = f"{label} pressed"
    asyncio.create_task(led_chase_animation(2.5))
    await push_state({"event": "keypress", "key": key_name, "log": entry})
    return {"status": "ok", "key": key_name}

@app.post("/api/toggle_auto_approve")
async def toggle_auto_approve():
    state.auto_approve = not state.auto_approve
    msg = "自动批准 ON" if state.auto_approve else "自动批准 OFF"
    state.lcd_message = msg
    entry = state.add_log("拨杆", msg)
    await push_state({"event": "toggle", "log": entry})
    return {"auto_approve": state.auto_approve}

@app.post("/api/mode/{mode_id}")
async def set_mode(mode_id: int):
    if mode_id not in (0, 1, 2):
        return JSONResponse({"error": "模式须为 0/1/2"}, status_code=400)
    state.current_mode = mode_id
    labels = {0: "Claude/Cursor", 1: "自定义快捷键", 2: "宏定义小键盘"}
    state.lcd_message = f"Mode{mode_id}: {labels[mode_id]}"
    entry = state.add_log("切换模式", labels[mode_id])
    await push_state({"event": "mode_change", "log": entry})
    return {"mode": mode_id}

@app.post("/api/lcd")
async def set_lcd(body: dict):
    msg = body.get("message", "")[:32]
    state.lcd_message = msg
    entry = state.add_log("LCD", msg)
    await push_state({"event": "lcd_update", "log": entry})
    return {"lcd_message": msg}

# ── SSH 接口 ─────────────────────────────────────────────────

@app.get("/api/ssh/status")
async def ssh_status():
    """获取 SSH 连接状态"""
    return ssh_manager.get_status()

@app.post("/api/ssh/connect")
async def ssh_connect(body: dict):
    """
    建立 SSH 连接
    
    body: {
        "hostname": "服务器地址",
        "port": 22,
        "username": "用户名",
        "password": "密码（可选）",
        "key_filename": "私钥路径（可选）"
    }
    """
    hostname = body.get("hostname", "")
    port = body.get("port", 22)
    username = body.get("username", "")
    password = body.get("password")
    key_filename = body.get("key_filename")
    
    if not hostname or not username:
        return JSONResponse(
            {"error": "hostname 和 username 为必填项"},
            status_code=400
        )
    
    result = ssh_manager.connect(hostname, port, username, password, key_filename)
    return result

@app.post("/api/ssh/command")
async def ssh_command(body: dict):
    """
    执行 SSH 命令
    
    body: {
        "command": "要执行的命令"
    }
    """
    command = body.get("command", "")
    if not command:
        return JSONResponse(
            {"error": "command 为必填项"},
            status_code=400
        )
    
    result = ssh_manager.execute_command(command)
    return result

@app.post("/api/ssh/disconnect")
async def ssh_disconnect():
    """断开 SSH 连接"""
    return ssh_manager.disconnect()

# ── Tmux 接口 ─────────────────────────────────────────────────

@app.get("/api/tmux/sessions")
async def list_tmux_sessions():
    """列出所有活跃的 tmux 会话"""
    sessions = tmux_manager.list_sessions()
    return {"success": True, "sessions": sessions}

@app.post("/api/tmux/create")
async def create_tmux_session(body: dict):
    """
    创建新的 tmux 会话
    
    body: {
        "path": "/Users/mac/codes"
    }
    """
    path = body.get("path", "")
    if not path:
        return JSONResponse(
            {"error": "path 为必填项"},
            status_code=400
        )
    
    result = tmux_manager.create_session(path)
    return result

@app.post("/api/tmux/attach")
async def attach_tmux_session(body: dict):
    """
    附加到指定 tmux 会话
    
    body: {
        "session_name": "codes.mac.Users"
    }
    """
    session_name = body.get("session_name", "")
    if not session_name:
        return JSONResponse(
            {"error": "session_name 为必填项"},
            status_code=400
        )
    
    result = tmux_manager.attach_session(session_name)
    return result

@app.get("/api/tmux/logs")
async def get_tmux_logs(session: str, lines: int = 200):
    """
    获取 tmux 会话的日志输出
    
    session: 会话名称
    lines: 获取最后多少行(默认 200)
    """
    try:
        # 检查会话是否存在
        result = subprocess.run(
            ['tmux', 'has-session', '-t', session],
            capture_output=True,
            timeout=3
        )
        
        if result.returncode != 0:
            return JSONResponse(
                {"error": f"会话不存在: {session}"},
                status_code=404
            )
        
        # 使用 capture-pane 获取会话内容
        result = subprocess.run(
            ['tmux', 'capture-pane', '-t', session, '-p', '-S', f'-{lines}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "session": session,
                "logs": result.stdout,
                "lines": lines
            }
        else:
            return JSONResponse(
                {"error": "获取日志失败"},
                status_code=500
            )
            
    except Exception as e:
        return JSONResponse(
            {"error": f"获取日志失败: {str(e)}"},
            status_code=500
        )

@app.post("/api/tmux/send-command")
async def send_tmux_command(body: dict):
    """
    发送命令到 tmux 会话
    
    body: {
        "session": "main",
        "command": "ls -la"
    }
    """
    session = body.get("session", "")
    command = body.get("command", "")
    
    if not session or not command:
        return JSONResponse(
            {"error": "session 和 command 为必填项"},
            status_code=400
        )
    
    try:
        # 使用 send-keys 发送命令
        subprocess.run(
            ['tmux', 'send-keys', '-t', session, command],
            capture_output=True,
            timeout=5
        )
        
        # 发送 Enter 键
        subprocess.run(
            ['tmux', 'send-keys', '-t', session, 'Enter'],
            capture_output=True,
            timeout=5
        )
        
        return {
            "success": True,
            "message": f"命令已发送到会话 {session}"
        }
        
    except Exception as e:
        return JSONResponse(
            {"error": f"发送命令失败: {str(e)}"},
            status_code=500
        )

@app.post("/api/tmux/delete-session")
async def delete_tmux_session(body: dict):
    """
    删除 tmux 会话
    
    body: {
        "session": "main"
    }
    """
    session = body.get("session", "")
    
    if not session:
        return JSONResponse(
            {"error": "session 为必填项"},
            status_code=400
        )
    
    try:
        # 检查会话是否存在
        result = subprocess.run(
            ['tmux', 'has-session', '-t', session],
            capture_output=True,
            timeout=3
        )
        
        if result.returncode != 0:
            return JSONResponse(
                {"error": f"会话不存在: {session}"},
                status_code=404
            )
        
        # 停止 pipe-pane (如果有的话)
        subprocess.run(
            ['tmux', 'pipe-pane', '-t', session],
            capture_output=True,
            timeout=3
        )
        
        # 删除会话
        subprocess.run(
            ['tmux', 'kill-session', '-t', session],
            capture_output=True,
            timeout=5
        )
        
        state.add_log("删除会话", session)
        
        return {
            "success": True,
            "message": f"会话 {session} 已删除"
        }
        
    except Exception as e:
        return JSONResponse(
            {"error": f"删除会话失败: {str(e)}"},
            status_code=500
        )

@app.websocket("/ws/ssh")
async def ssh_websocket(ws: WebSocket):
    """
    SSH WebSocket 终端
    通过 WebSocket 实现交互式 SSH 终端
    """
    await ws.accept()
    
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            
            msg_type = data.get("type", "")
            
            if msg_type == "connect":
                # 建立连接
                result = ssh_manager.connect(
                    data.get("hostname", ""),
                    data.get("port", 22),
                    data.get("username", ""),
                    data.get("password"),
                    data.get("key_filename")
                )
                await ws.send_text(json.dumps({
                    "type": "connect_result",
                    **result
                }))
            
            elif msg_type == "command":
                # 执行命令
                command = data.get("command", "")
                result = ssh_manager.execute_command(command)
                await ws.send_text(json.dumps({
                    "type": "command_result",
                    **result
                }))
            
            elif msg_type == "disconnect":
                # 断开连接
                result = ssh_manager.disconnect()
                await ws.send_text(json.dumps({
                    "type": "disconnect_result",
                    **result
                }))
                break
            
            elif msg_type == "status":
                # 查询状态
                status = ssh_manager.get_status()
                await ws.send_text(json.dumps({
                    "type": "status",
                    **status
                }))
            
            elif msg_type == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
                
    except WebSocketDisconnect:
        # 连接断开时清理 SSH 连接
        if ssh_manager.connected:
            ssh_manager.disconnect()

# ── WebSocket 端点 ───────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    # 连接时推送当前状态
    await push_state()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type", "")
            if msg_type == "keypress":
                key = data.get("key", "")
                await press_key(key)
            elif msg_type == "toggle_auto_approve":
                await toggle_auto_approve()
            elif msg_type == "set_mode":
                await set_mode(int(data.get("mode", 0)))
            elif msg_type == "ping":
                await ws.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(ws)

# ── 启动入口 ─────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10015, reload=True)
