# 更新日志

## [1.3.0] - 2026-06-28

### 更新

#### 1. 前端端口调整
- ✅ 前端开发服务器端口从 3000 改为 10016
- ✅ 避免与其他服务端口冲突
- ✅ 更贴近后端端口(10015)，便于记忆

#### 2. 一键启动功能
- ✅ 添加 `npm run dev:all` 命令
- ✅ 使用 concurrently 同时启动后端和前端
- ✅ 添加 `npm run start:backend` 单独启动后端
- ✅ 简化开发流程，无需手动启动两个服务

### 使用方式

#### 方式一：分别启动
```bash
# 终端 1：启动后端
python main.py

# 终端 2：启动前端
cd frontend
npm run dev
```

#### 方式二：一键启动（推荐）
```bash
cd frontend
npm run dev:all
```

### 文件变更
- `frontend/vite.config.js` - 端口改为 10016
- `frontend/package.json` - 添加 dev:all 和 start:backend 脚本
- `README.md` - 更新端口说明
- `frontend/README.md` - 更新端口和启动方式

## [1.2.0] - 2026-06-28

### 新增功能

#### 1. Tmux 会话管理
- ✅ 添加 TmuxManager 类,实现 tmux 会话管理
- ✅ 新增 REST API 接口:
  - `GET /api/tmux/sessions` - 列出所有活跃会话
  - `POST /api/tmux/create` - 创建新会话
  - `POST /api/tmux/attach` - 切换到指定会话
- ✅ 前端实现:
  - 下拉菜单显示活跃会话列表(自动刷新)
  - “新增”按钮创建新会话
  - 弹窗表单输入项目路径
  - 实时预览会话名称(反向域名格式)
  - 路径验证(禁止 ~ 和根路径)
- ✅ 自动激活 Claude: 创建会话后自动 cd 到路径并启动 claude
- ✅ 会话命名规则: `/Users/mac/codes` → `codes.mac.Users`

### 文件变更

#### 新增文件
```
TMUX_GUIDE.md          # Tmux 会话管理使用指南
```

#### 修改文件
- `main.py` - 添加 TmuxManager 类和 tmux API 端点
- `frontend/src/views/ControlPanel.vue` - 添加 tmux 会话管理和创建功能
- `README.md` - 添加 tmux 会话管理说明
- `CHANGELOG.md` - 添加本版本更新记录

### 使用方式

#### 创建新会话
1. 点击顶部右侧“新增”按钮
2. 输入项目绝对路径(如 `/Users/mac/codes`)
3. 系统自动预览会话名称
4. 点击“创建”完成

#### 切换会话
- 从顶部的下拉菜单选择要切换的会话
- 会话列表每 5 秒自动刷新

### 注意事项

1. **tmux 必须安装**:
   ```bash
   brew install tmux  # macOS
   sudo apt-get install tmux  # Ubuntu
   ```

2. **路径规则**:
   - ✅ 必须使用绝对路径(以 / 开头)
   - ❌ 不允许使用 ~ 符号
   - ❌ 不允许使用根路径 /
   - ✅ 路径必须存在且是目录

3. **会话命名**:
   - 自动转换为反向域名格式
   - 示例: `/Users/mac/codes` → `codes.mac.Users`

## [1.1.0] - 2026-06-28

### 新增功能

#### 1. SSH 终端支持
- ✅ 添加 paramiko 依赖，实现 SSH 连接功能
- ✅ 新增 `/ws/ssh` WebSocket 端点，支持交互式 SSH 终端
- ✅ 新增 REST API 接口：
  - `GET /api/ssh/status` - 获取 SSH 连接状态
  - `POST /api/ssh/connect` - 建立 SSH 连接
  - `POST /api/ssh/command` - 执行 SSH 命令
  - `POST /api/ssh/disconnect` - 断开 SSH 连接
- ✅ 在原有 HTML 页面添加 SSH 终端入口按钮
- ✅ 创建 `/ssh` 路由页面

#### 2. Vue 3 前端项目
- ✅ 完整的 Vue 3 + Vite 项目结构
- ✅ 使用 Vue Router 实现路由管理
  - `/` - 控制面板页面
  - `/ssh` - SSH 终端页面
- ✅ 使用 xterm.js 实现专业终端仿真
- ✅ 现代化 UI 设计，支持响应式布局
- ✅ WebSocket 实时通信
- ✅ 自动代理配置（开发模式）

#### 3. 文档更新
- ✅ 完善 README.md
  - 添加功能特性说明
  - 添加 tmux 安装教程（macOS/Ubuntu/CentOS）
  - 添加 tmux-logging 插件安装指南
  - 添加 OpenLess 可选依赖说明
  - 添加项目结构说明
  - 添加 API 文档链接
- ✅ 添加前端项目 README.md

### 技术栈更新

#### 后端
- FastAPI >= 0.111.0
- Uvicorn >= 0.29.0
- **paramiko >= 3.3.0** (新增)
- **websocket-client >= 1.6.0** (新增)

#### 前端
- Vue 3.4.0
- Vue Router 4.2.5
- Vite 5.0.0
- xterm.js 5.3.0
- Axios 1.6.0

### 文件变更

#### 新增文件
```
frontend/
├── package.json
├── vite.config.js
├── index.html
├── README.md
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js
    ├── assets/style.css
    └── views/
        ├── ControlPanel.vue
        └── SSHTerminal.vue

ssh_manager.py          # SSH 连接管理模块
```

#### 修改文件
- `main.py` - 添加 SSH 路由和 WebSocket 端点
- `requirements.txt` - 添加 paramiko 和 websocket-client
- `README.md` - 完善项目文档
- `static/index.html` - 添加 SSH 入口按钮
- `static/style.css` - 添加 SSH 按钮样式

### 使用方式

#### 方式一：使用原有静态页面（推荐生产环境）

1. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

2. 启动后端服务：
```bash
python main.py
```

3. 访问 `http://localhost:10015`

#### 方式二：使用 Vue 开发模式（推荐开发环境）

1. 安装 Python 依赖并启动后端：
```bash
pip install -r requirements.txt
python main.py
```

2. 在另一个终端安装前端依赖：
```bash
cd frontend
npm install
```

3. 启动前端开发服务器：
```bash
npm run dev
```

4. 访问 `http://localhost:3000`（自动代理到后端）

### 兼容性

- ✅ 向后兼容：原有静态页面功能完全保留
- ✅ 渐进式迁移：Vue 前端可作为独立项目运行
- ✅ 可选依赖：SSH 功能为可选，不影响核心功能

### 注意事项

1. **SSH 安全**：
   - 首次连接未知主机时会自动接受主机密钥
   - 建议在生产环境配置 SSH 密钥认证
   - 不要在生产环境使用弱密码

2. **依赖安装**：
   - paramiko 可能需要系统安装 libffi 和 OpenSSL
   - macOS: `brew install libffi openssl`
   - Ubuntu: `sudo apt-get install libffi-dev libssl-dev`

3. **开发环境**：
   - 需要 Node.js >= 16
   - 推荐使用 npm >= 8 或 pnpm >= 8

### 已知问题

- Vue 前端为开发版本，生产部署需要构建
- SSH 终端在大文件传输时可能需要优化缓冲区

### 后续计划

- [ ] 添加 SSH 连接历史记录
- [ ] 支持多标签 SSH 会话
- [ ] 添加文件传输功能（SFTP）
- [ ] 完善 Vue 前端的生产构建配置
- [ ] 添加单元测试
