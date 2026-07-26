# Claude Panel - 键盘控制面板

一个基于 FastAPI 的 Claude 键盘控制面板，支持按键事件、WebSocket 实时通信、LED 状态管理和 SSH 远程连接。

## 功能特性

- 🎹 虚拟键盘控制（Mic/YES/NO/Enter）
- 💡 LED 流水灯动画效果
- 📺 LCD 信息显示
- 🔄 WebSocket 实时通信
- 🖥️ SSH 远程连接（可选）
- 🎯 多种工作模式切换
- 📦 **Tmux 会话管理**（新增）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:10016` 启动。

### 3. 启动前端（开发模式）

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:10014` 启动，并自动代理 API 请求到后端。

## 环境配置（可选）

### 安装 tmux 和 tmux-logging 插件

如果你想使用 tmux 会话管理功能，需要安装以下工具：

#### 安装 tmux

**macOS:**
```bash
brew install tmux
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tmux
```

**CentOS/RHEL:**
```bash
sudo yum install tmux
```

#### 安装 tmux-logging 插件

1. 安装 TPM (Tmux Plugin Manager):
```bash
git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
```

2. 在 `~/.tmux.conf` 中添加插件:
```bash
set -g @plugin 'tmux-plugins/tpm'
set -g @plugin 'tmux-plugins/tmux-logging'
```

3. 重新加载 tmux 配置:
```bash
tmux source ~/.tmux.conf
```

4. 在 tmux 中按 `prefix + I` 安装插件。

### 安装 OpenLess（可选依赖）

OpenLess 是一个强大的终端会话管理工具：

```bash
# 查看安装说明
https://github.com/Open-Less/openless

# 按照官方文档进行安装
```

> **注意**: OpenLess 是可选的，不影响核心功能的使用。

### Tmux 会话管理（新增）

系统已集成 tmux 会话管理功能，可以方便地创建和切换项目会话：

1. **查看会话**: 顶部下拉菜单显示所有活跃的 tmux 会话
2. **创建会话**: 点击“新增”按钮，输入项目绝对路径
3. **切换会话**: 从下拉菜单选择要切换的会话
4. **自动激活**: 创建会话时自动启动 Claude

会话名称采用反向域名格式，例如 `/Users/mac/codes` → `codes.mac.Users`

详细使用说明请参考 [TMUX_GUIDE.md](TMUX_GUIDE.md)

## 项目结构

```
claude-panel/
├── main.py              # FastAPI 主程序
├── requirements.txt     # Python 依赖
├── README.md           # 项目文档
├── static/             # 前端静态资源
│   ├── index.html      # 主页面
│   ├── app.js          # 前端逻辑
│   └── style.css       # 样式文件
└── frontend/           # Vue 前端项目（开发中）
    ├── package.json
    ├── src/
    └── ...
```

## API 文档

启动服务后访问 `http://localhost:10016/docs` 查看完整的 API 文档。

## 技术栈

- **后端**: FastAPI + Uvicorn
- **前端**: 原生 HTML/CSS/JS + Vue 3（迁移中）
- **通信**: WebSocket + REST API
- **SSH**: Paramiko（可选）

## License

MIT