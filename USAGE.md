# Claude Panel - 使用指南

## 📋 目录

1. [快速开始](#快速开始)
2. [功能说明](#功能说明)
3. [SSH 终端使用](#ssh-终端使用)
4. [Vue 前端开发](#vue-前端开发)
5. [API 文档](#api-文档)
6. [常见问题](#常见问题)

## 快速开始

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

> **注意**: 如果安装 paramiko 时出错,请确保系统已安装:
> - macOS: `brew install libffi openssl`
> - Ubuntu: `sudo apt-get install libffi-dev libssl-dev`

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:10015` 启动

### 3. 访问控制面板

打开浏览器访问: `http://localhost:10015`

## 功能说明

### 🎹 键盘控制

- **Mic 键**: 模拟语音输入
- **YES 键**: 确认操作
- **NO 键**: 拒绝操作  
- **Enter 键**: 提交/执行

### 💡 LED 流水灯

7 个 LED 灯显示任务运行状态:
- ⚫ **灰色**: 关闭
- 🟡 **黄色**: 开启
- 🔵 **蓝色**: 运行中(动画)

### 📺 LCD 显示

- 显示当前状态信息
- 支持自定义文本输入(最多 32 字符)

### 🔄 模式切换

- **Mode 0**: Claude/Cursor 模式
- **Mode 1**: 自定义快捷键
- **Mode 2**: 宏定义小键盘

### 🔌 自动批准拨杆

开启/关闭自动批准功能

## SSH 终端使用

### 方式一: 使用静态页面(基础版)

1. 访问 `http://localhost:10015`
2. 点击右上角 **SSH** 按钮
3. 将跳转到 SSH 终端页面

### 方式二: 使用 Vue 前端(完整版)

参考 [Vue 前端开发](#vue-前端开发) 章节

### SSH 连接步骤

1. **填写连接信息**:
   - 主机地址(必填): SSH 服务器地址
   - 端口(默认 22): SSH 端口号
   - 用户名(必填): 登录用户名

2. **选择认证方式**:
   - **密码认证**: 输入密码
   - **SSH 密钥**: 提供私钥文件路径(如 `~/.ssh/id_rsa`)

3. **点击连接**

4. **使用终端**:
   - 在输入框中输入命令
   - 按回车或点击"执行"按钮
   - 查看命令输出

### SSH API 使用示例

#### 1. 连接 SSH

```bash
curl -X POST http://localhost:10015/api/ssh/connect \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "192.168.1.100",
    "port": 22,
    "username": "root",
    "password": "your_password"
  }'
```

#### 2. 执行命令

```bash
curl -X POST http://localhost:10015/api/ssh/command \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls -la"
  }'
```

#### 3. 断开连接

```bash
curl -X POST http://localhost:10015/api/ssh/disconnect
```

#### 4. 查看状态

```bash
curl http://localhost:10015/api/ssh/status
```

## Vue 前端开发

### 安装前端依赖

```bash
cd frontend
npm install
```

### 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:3000` 启动

### 功能特性

- ✅ 完整的控制面板功能
- ✅ 专业 SSH 终端(xterm.js)
- ✅ 实时 WebSocket 通信
- ✅ 响应式设计
- ✅ 现代化 UI

### 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录

## API 文档

### REST API

#### 键盘控制

- `POST /api/key/{key_name}` - 模拟按键(mic/yes/no/enter)
- `POST /api/toggle_auto_approve` - 切换自动批准
- `POST /api/mode/{mode_id}` - 切换模式(0/1/2)
- `POST /api/lcd` - 设置 LCD 文本

#### SSH 功能

- `GET /api/ssh/status` - 获取 SSH 状态
- `POST /api/ssh/connect` - 连接 SSH
- `POST /api/ssh/command` - 执行命令
- `POST /api/ssh/disconnect` - 断开连接

#### 状态查询

- `GET /api/state` - 获取面板状态

### WebSocket

#### 主 WebSocket (`/ws`)

用于控制面板实时通信

**发送消息**:
```json
{ "type": "keypress", "key": "mic" }
{ "type": "toggle_auto_approve" }
{ "type": "set_mode", "mode": 1 }
{ "type": "ping" }
```

**接收消息**:
```json
{
  "type": "state",
  "auto_approve": false,
  "led_status": [0,0,0,0,0,0,0],
  "lcd_message": "Ready",
  "current_mode": 0,
  "task_running": false,
  "logs": []
}
```

#### SSH WebSocket (`/ws/ssh`)

用于 SSH 终端交互

**发送消息**:
```json
{ "type": "connect", "hostname": "...", "port": 22, "username": "..." }
{ "type": "command", "command": "ls -la" }
{ "type": "disconnect" }
{ "type": "status" }
{ "type": "ping" }
```

**接收消息**:
```json
{ "type": "connect_result", "success": true, "message": "..." }
{ "type": "command_result", "success": true, "output": "..." }
{ "type": "disconnect_result", "success": true }
{ "type": "pong" }
```

## 常见问题

### Q1: paramiko 安装失败

**问题**: `ModuleNotFoundError: No module named 'paramiko'`

**解决方案**:
```bash
# macOS
brew install libffi openssl
pip install paramiko

# Ubuntu/Debian
sudo apt-get install libffi-dev libssl-dev
pip install paramiko
```

### Q2: 端口被占用

**问题**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -ti:10015

# 杀掉进程
kill -9 <PID>

# 重新启动
python main.py
```

### Q3: WebSocket 连接失败

**问题**: 前端无法连接 WebSocket

**解决方案**:
1. 确保后端服务正在运行
2. 检查浏览器控制台是否有错误
3. 确认防火墙没有阻止 10015 端口
4. 如果使用 HTTPS,WebSocket 应使用 `wss://`

### Q4: SSH 连接失败

**问题**: 无法连接到 SSH 服务器

**排查步骤**:
1. 确认 SSH 服务器正在运行
2. 检查防火墙设置
3. 验证用户名和密码/密钥
4. 查看后端日志获取详细错误信息

### Q5: Vue 前端无法连接后端

**问题**: Vue 开发服务器代理失败

**解决方案**:
1. 确保后端在 10015 端口运行
2. 检查 `frontend/vite.config.js` 中的代理配置
3. 重启前端开发服务器

### Q6: tmux 相关功能不工作

**问题**: tmux 会话管理功能无效

**解决方案**:
1. 安装 tmux: `brew install tmux` (macOS)
2. 安装 tmux-logging 插件(参考 README.md)
3. 确保 tmux 在 PATH 中

## 技术支持

- 查看 `CHANGELOG.md` 了解版本更新
- 查看 `README.md` 了解项目概况
- 访问 `http://localhost:10015/docs` 查看完整 API 文档

## 许可证

MIT License
