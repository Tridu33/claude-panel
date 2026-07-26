# Claude Panel - Vue 前端

这是 Claude Panel 的 Vue 3 前端项目，提供现代化的用户界面和完整的 SSH 终端功能。

## 功能特性

- 🎹 完整的键盘控制面板
- 🔗 SSH 终端连接（使用 xterm.js）
- 📡 WebSocket 实时通信
- 🎨 现代化 UI 设计
- 📱 响应式布局

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

开发服务器将在 `http://localhost:10014` 启动，并自动代理 API 请求到后端服务器（`http://localhost:10016`）。

### 2.1 同时启动后端和前端（推荐）

```bash
npm run dev:all
```

这会同时启动：
- 后端服务：`http://localhost:10016`
- 前端服务：`http://localhost:10014`

### 3. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 4. 预览生产构建

```bash
npm run preview
```

## 项目结构

```
frontend/
├── src/
│   ├── assets/          # 静态资源（CSS、图片等）
│   │   └── style.css
│   ├── components/      # 可复用组件
│   ├── views/           # 页面视图
│   │   ├── ControlPanel.vue   # 控制面板页面
│   │   └── SSHTerminal.vue    # SSH 终端页面
│   ├── router/          # 路由配置
│   │   └── index.js
│   ├── App.vue          # 根组件
│   └── main.js          # 入口文件
├── index.html           # HTML 模板
├── vite.config.js       # Vite 配置
└── package.json         # 项目依赖
```

## 技术栈

- **框架**: Vue 3 (Composition API)
- **路由**: Vue Router 4
- **构建工具**: Vite 5
- **终端**: xterm.js + xterm-addon-fit
- **HTTP 客户端**: Axios
- **样式**: CSS3 (Scoped CSS)

## 开发说明

### 代理配置

开发模式下，Vite 会自动代理以下路径到后端服务器：

- `/api` → `http://localhost:10016`
- `/ws` → `ws://localhost:10016`

确保后端服务器在 10016 端口运行。

### SSH 终端

SSH 终端功能使用 xterm.js 实现，提供：

- 完整的终端仿真
- WebSocket 实时通信
- 支持密码和密钥认证
- 自适应终端大小

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## License

MIT
