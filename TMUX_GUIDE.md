# Tmux 会话管理功能说明

## 功能概述

在 Claude Panel 中集成了 tmux 会话管理功能,可以方便地创建、切换和管理 tmux 会话。

## 使用方式

### 1. 查看活跃会话

在控制面板顶部,下拉菜单会显示当前所有活跃的 tmux 会话。会话列表每 5 秒自动刷新一次。

### 2. 创建新会话

1. 点击顶部右侧的 **"新增"** 按钮
2. 在弹窗中输入项目的**绝对路径**,例如: `/Users/mac/codes`
3. 系统会自动预览生成的会话名称(反向域名格式)
4. 点击 **"创建"** 按钮

### 3. 切换会话

从下拉菜单中选择要切换的会话,系统会自动附加到该会话。

## 会话命名规则

路径会自动转换为**反向域名格式**的会话名称:

| 输入路径 | 会话名称 |
|---------|---------|
| `/Users/mac/codes` | `codes.mac.Users` |
| `/Users/mac/projects/myapp` | `myapp.projects.mac.Users` |
| `/var/www/html` | `html.www.var` |

## 路径验证规则

系统会验证输入的路径:

✅ **允许**:
- 必须以 `/` 开头的绝对路径
- 路径必须存在
- 路径必须是目录

❌ **禁止**:
- 使用 `~` 符号(如 `~/codes`)
- 使用根路径 `/`
- 路径不存在
- 路径不是目录

## 自动激活 Claude

创建新会话时,系统会自动:
1. 创建 tmux 会话(分离模式)
2. 切换到指定路径
3. 启动 `claude` 命令

## API 接口

### 列出会话

```bash
GET /api/tmux/sessions

Response:
{
  "success": true,
  "sessions": [
    {
      "name": "codes.mac.Users",
      "path": "/Users/mac/codes"
    }
  ]
}
```

### 创建会话

```bash
POST /api/tmux/create
Content-Type: application/json

{
  "path": "/Users/mac/codes"
}

Response:
{
  "success": true,
  "session_name": "codes.mac.Users",
  "path": "/Users/mac/codes",
  "message": "已创建会话: codes.mac.Users"
}
```

### 切换会话

```bash
POST /api/tmux/attach
Content-Type: application/json

{
  "session_name": "codes.mac.Users"
}

Response:
{
  "success": true,
  "message": "已切换到会话: codes.mac.Users"
}
```

## 技术实现

### 后端 (Python)

- 使用 `subprocess` 调用 tmux 命令
- 路径验证使用 `os.path` 模块
- 会话名称转换采用反向域名表示法

### 前端 (Vue 3)

- 使用 computed 属性实时预览会话名称
- 弹窗表单带输入验证
- 定时刷新会话列表(5秒间隔)
- WebSocket 实时通信

## 注意事项

1. **tmux 必须安装**: 确保系统已安装 tmux
   ```bash
   # macOS
   brew install tmux
   
   # Ubuntu/Debian
   sudo apt-get install tmux
   ```

2. **权限要求**: 运行服务的用户需要有权限创建和管理 tmux 会话

3. **会话持久化**: tmux 会话在服务重启后仍然存在,可以继续使用

4. **手动管理**: 也可以通过命令行手动管理会话:
   ```bash
   # 列出所有会话
   tmux list-sessions
   
   # 附加到会话
   tmux attach -t codes.mac.Users
   
   # 删除会话
   tmux kill-session -t codes.mac.Users
   ```

## 示例场景

### 场景 1: 启动新项目

1. 点击"新增"按钮
2. 输入 `/Users/mac/projects/newapp`
3. 系统创建会话 `newapp.projects.mac.Users`
4. 自动启动 Claude,可以开始编码

### 场景 2: 切换项目

1. 从下拉菜单选择已有的会话
2. 系统自动切换到该会话
3. LCD 屏幕显示切换成功消息

### 场景 3: 管理多个项目

- 为每个项目创建独立的 tmux 会话
- 通过下拉菜单快速切换
- 每个会话保持独立的 Claude 实例

## 故障排查

### 问题: 会话列表为空

**原因**: tmux 没有运行或没有活跃会话

**解决**:
```bash
# 检查 tmux 是否安装
tmux -V

# 手动创建一个测试会话
tmux new-session -d -s test
```

### 问题: 创建会话失败

**原因**: 路径不存在或权限不足

**解决**:
- 确认路径存在且是目录
- 检查路径拼写
- 确保不使用 `~` 符号

### 问题: Claude 没有启动

**原因**: claude 命令未在 PATH 中

**解决**:
```bash
# 检查 claude 是否可用
which claude

# 如果不可用,检查安装
```

## 未来改进

- [ ] 支持自定义会话名称
- [ ] 添加会话删除功能
- [ ] 显示会话状态(活跃/分离)
- [ ] 支持批量操作
- [ ] 添加会话搜索功能
