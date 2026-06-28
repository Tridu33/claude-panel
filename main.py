"""
Claude 键盘控制面板 - FastAPI 服务器
支持按键事件、WebSocket 实时通信、LED 状态管理
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import Optional
from datetime import datetime
import uvicorn

app = FastAPI(title="Claude 键盘控制面板", version="1.0.0")

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
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

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
    key_name: mic | yes | no | enter
    """
    key_name = key_name.lower()
    if key_name not in ("mic", "yes", "no", "enter"):
        return JSONResponse({"error": "未知按键"}, status_code=400)

    actions = {
        "mic":   ("麦克风", "开始语音输入"),
        "yes":   ("YES",    "确认操作"),
        "no":    ("NO",     "拒绝操作"),
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

# ── 挂载静态文件 ─────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── 启动入口 ─────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10015, reload=True)
