# tmux-ai-coder-panel

Claude 键盘控制面板 — **单端口整体服务**（FastAPI 后端 + Vue3 前端 + WebSocket 实时通信 + tmux 会话管理）。

`pip install` 之后 **一行命令同时启动后端与前端**：一个端口同时提供网页界面、`/api` 接口与 `/ws` 实时通道，无需单独部署 Node 或配置代理。

## 快速开始

### 1. 安装

```bash
pip install tmux-ai-coder-panel
```

需要 tmux 会话管理功能时，请确保系统已安装 [tmux](https://github.com/tmux/tmux/wiki)（可选，不影响面板本身运行）。

### 2. 一行命令启动（后端 + 前端）

```bash
tmux-ai-coder-panel
```

等价命令：`python -m tmux_ai_coder_panel`。

启动后浏览器访问：

```
http://127.0.0.1:20016
```

**一个命令、一个端口，同时服务前端页面、API 与 WebSocket。**（默认仅监听本机，需要局域网/公网访问时加 `--host 0.0.0.0`，见下）

### 3. 登录

- 首次启动会自动生成随机账号密码，写入**当前目录**的 `.env`，并在终端打印：

  ```
  [首次启动] 账号: a844ef3a
  [首次启动] 密码: e2-mWOAB8dooxSu4   (可编辑该文件修改)
  ```

- 编辑 `.env` 可修改账号密码，重启后生效：

  ```ini
  PANEL_ACCOUNT=你的账号
  PANEL_SECERT=你的密码
  ```

## 常用参数

| 参数 / 环境变量 | 说明 |
|---|---|
| `--host 0.0.0.0` | 监听所有网卡（默认 `127.0.0.1`，仅本机可访问） |
| `--port 3000` | 从指定端口启动 |
| `PORT=3000 tmux-ai-coder-panel` | 等价于 `--port`，适合容器/脚本 |
| `HOST=0.0.0.0 tmux-ai-coder-panel` | 等价于 `--host` |
| （默认 20016） | 端口被占用时**自动 +1** 直到空闲，无需手动处理 |

启动横幅会显示最终端口与访问地址（监听 `0.0.0.0` 时额外显示局域网地址）：

```
============================================================
  tmux-ai-coder-panel 已启动
  本机访问:  http://127.0.0.1:20016
  API 文档:  http://127.0.0.1:20016/docs
  按 Ctrl+C 停止服务
============================================================
```

## 功能特性

- 🎹 虚拟键盘控制（Mic / YES / NO / Enter，默认折叠）
- 💡 LED 流水灯动画
- 📺 LCD 信息显示
- 🔄 WebSocket 实时状态推送
- 📦 **tmux 会话管理**：查看 / 切换 / 创建 / 发送命令 / 查看日志
- 🔐 HMAC 签名无状态登录（7 天会话，cookie + token 双通道）
- 📝 内置 Swagger API 文档（`/docs`）

## 后台运行（可选）

```bash
nohup tmux-ai-coder-panel --host 0.0.0.0 > panel.log 2>&1 &
```

或使用 systemd：

```ini
# /etc/systemd/system/tmux-ai-coder-panel.service
[Unit]
Description=tmux-ai-coder-panel
After=network.target

[Service]
ExecStart=/usr/local/bin/tmux-ai-coder-panel --host 0.0.0.0
WorkingDirectory=/root
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now tmux-ai-coder-panel
```

## 开发模式（源码运行）

```bash
git clone <仓库地址> && cd <仓库>
pip install -r requirements.txt

# 构建前端产物到 Python 包目录
cd frontend && npm install && npm run build && cd ..

# 启动（后端 + 前端静态资源 + API + WS，单端口）
python main.py          # 或: uvicorn main:app --port 10015 --reload
```

## 项目结构

```
tmux-ai-coder-panel/
├── tmux_ai_coder_panel/        # Python 包
│   ├── main.py              # FastAPI 应用(API + WS + 前端静态资源)
│   ├── cli.py               # 命令行入口(端口探测/自动+1/.env 生成)
│   └── frontend_dist/       # 构建后的前端产物(打进 wheel)
├── frontend/                # Vue3 前端源码
├── pyproject.toml           # 打包配置(console scripts: tmux-ai-coder-panel)
└── main.py                  # 源码运行薄壳(兼容旧启动方式)
```

## 技术栈

- **后端**: FastAPI + Uvicorn + python-dotenv
- **前端**: Vue 3 + Vite（构建产物内置，无 Node 依赖）
- **通信**: WebSocket + REST API
- **会话管理**: tmux（自动探测 socket，兼容 systemd / SSH 环境）

## License

MIT
