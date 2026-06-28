# 命令输入和会话管理功能说明

## 功能概述

在 Claude Panel 中新增了命令输入和会话管理功能,可以直接向 tmux 会话发送命令,并支持删除会话。

## 主要功能

### 1. 命令输入区

#### 位置
在会话日志终端下方

#### 功能特性
- **长文本输入**: 支持多行命令输入
- **快捷键发送**: 
  - `Ctrl + Enter` (Windows/Linux)
  - `⌘ + Enter` (macOS)
- **实时反馈**: 发送后立即刷新日志显示
- **发送状态**: 按钮显示"发送中..."防止重复提交

#### 使用方式
1. 在文本框中输入命令(支持多行)
2. 点击"发送"按钮或按快捷键
3. 命令会发送到当前选中的 tmux 会话
4. 日志自动刷新,显示命令执行结果

### 2. 删除会话功能

#### 触发方式
点击"删除会话"按钮(红色)

#### 确认流程
1. 点击"删除会话"按钮
2. 弹出确认对话框
3. 显示警告信息和将要执行的操作
4. 用户选择"确认删除"或"取消"

#### 删除操作
确认后执行:
1. **停止日志管道**: `pipe-pane -t {session}`
2. **删除会话**: `tmux kill-session -t {session}`
3. 刷新会话列表
4. 清空当前选择

#### 警告信息
删除确认弹窗会提示:
- ⚠️ 停止该会话的日志管道
- ⚠️ 终止会话中的所有进程
- ⚠️ 删除该 tmux 会话
- ❗ 此操作不可撤销!

### 3. Pipe-Pane 日志跟踪

#### 实现原理
使用 tmux 内置的 `pipe-pane` 功能,无需额外插件

#### 工作流程
1. **创建会话时**:
   ```bash
   # 创建日志目录
   mkdir -p ~/.claude-server
   
   # 启动 pipe-pane
   tmux pipe-pane -t main "cat >> ~/.claude-server/tmux-main.log"
   ```

2. **实时跟踪**:
   ```bash
   tail -f ~/.claude-server/tmux-main.log
   ```

3. **删除会话时**:
   ```bash
   # 停止 pipe-pane
   tmux pipe-pane -t main
   
   # 删除会话
   tmux kill-session -t main
   ```

#### 日志位置
```
~/.claude-server/
├── tmux-main.log
├── tmux-codes.mac.Users.log
└── ...
```

## API 接口

### 1. 发送命令到会话

```bash
POST /api/tmux/send-command
Content-Type: application/json

{
  "session": "main",
  "command": "ls -la"
}

Response:
{
  "success": true,
  "message": "命令已发送到会话 main"
}
```

### 2. 删除会话

```bash
POST /api/tmux/delete-session
Content-Type: application/json

{
  "session": "main"
}

Response:
{
  "success": true,
  "message": "会话 main 已删除"
}
```

## 界面布局

```
┌─────────────────────────────────────────┐
│ 🔗 会话日志: main                       │
│                    [行数: 200] [自动] [刷新]│
├─────────────────────────────────────────┤
│ 日志内容...                             │
│ ...                                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔗 发送命令到会话: main                 │
├─────────────────────────────────────────┤
│ ┌─────────────────────────────────────┐ │
│ │ 输入命令...                          │ │
│ │ 支持多行输入                         │ │
│ │ Ctrl+Enter 或 ⌘+Enter 发送          │ │
│ └─────────────────────────────────────┘ │
│ [🚀 发送]              [🗑️ 删除会话]    │
└─────────────────────────────────────────┘
```

## 使用场景

### 场景 1: 执行简单命令
```
输入: ls -la
操作: 点击发送
结果: 在日志中显示目录内容
```

### 场景 2: 执行多行命令
```
输入: 
for i in {1..5}; do
  echo "Iteration $i"
  sleep 1
done

操作: Ctrl+Enter
结果: 显示 5 次迭代输出
```

### 场景 3: 删除不需要的会话
```
操作: 
1. 选择要删除的会话
2. 点击"删除会话"
3. 确认删除
结果: 会话被清理,列表刷新
```

### 场景 4: 与 Claude 交互
```
输入: 请帮我分析这段代码
操作: 发送
结果: Claude 在会话中响应
```

## 技术实现

### 后端 (Python)

#### 发送命令
```python
# 使用 send-keys 发送命令
subprocess.run(['tmux', 'send-keys', '-t', session, command])
# 发送 Enter 键执行
subprocess.run(['tmux', 'send-keys', '-t', session, 'Enter'])
```

#### 删除会话
```python
# 停止 pipe-pane
subprocess.run(['tmux', 'pipe-pane', '-t', session])
# 删除会话
subprocess.run(['tmux', 'kill-session', '-t', session])
```

#### Pipe-Pane 日志
```python
# 创建日志目录
log_dir = os.path.expanduser('~/.claude-server')
os.makedirs(log_dir, exist_ok=True)

# 启动日志管道
pipe_command = f"cat >> {log_file}"
subprocess.run(['tmux', 'pipe-pane', '-t', session, pipe_command])
```

### 前端 (Vue 3)

#### 命令输入
- 使用 `<textarea>` 支持多行输入
- 监听 `Ctrl+Enter` 和 `⌘+Enter` 快捷键
- 发送时禁用按钮防止重复提交
- 发送成功后清空输入框并刷新日志

#### 删除确认
- 模态弹窗确认
- 警告信息和操作说明
- 删除过程中禁用按钮
- 删除成功后刷新会话列表

## 注意事项

### 1. Pipe-Pane 限制
- 日志是追加写入,不会自动清理
- 大日志文件可能占用较多磁盘空间
- 建议定期清理旧日志文件

### 2. 命令执行
- 命令在 tmux 会话中执行
- 需要确保会话处于交互状态
- 长时间运行的命令会阻塞后续命令

### 3. 删除会话
- 删除操作不可撤销
- 会终止会话中的所有进程
- 建议先保存重要数据

### 4. 权限要求
- 需要对 `~/.claude-server` 目录有写入权限
- 需要有权限管理 tmux 会话

## 日志管理

### 查看日志
```bash
# 查看所有日志文件
ls -lh ~/.claude-server/

# 实时查看某个会话的日志
tail -f ~/.claude-server/tmux-main.log

# 查看日志大小
du -sh ~/.claude-server/
```

### 清理日志
```bash
# 清理所有日志
rm ~/.claude-server/tmux-*.log

# 清理特定会话的日志
rm ~/.claude-server/tmux-main.log

# 清理大于 100MB 的日志
find ~/.claude-server/ -name "tmux-*.log" -size +100M -delete
```

### 自动清理(可选)
```bash
# 添加到 crontab,每天清理一次
0 2 * * * find ~/.claude-server/ -name "tmux-*.log" -mtime +7 -delete
```

## 常见问题

### Q1: 命令发送后没有响应
**原因**: 会话可能不在交互状态

**解决**:
```bash
# 检查会话状态
tmux list-sessions

# 手动附加到会话
tmux attach -t main
```

### Q2: 日志没有实时更新
**原因**: pipe-pane 可能已停止

**解决**:
```bash
# 重新启动 pipe-pane
tmux pipe-pane -t main "cat >> ~/.claude-server/tmux-main.log"
```

### Q3: 删除会话失败
**原因**: 会话不存在或权限不足

**解决**:
```bash
# 检查会话是否存在
tmux has-session -t main

# 手动删除
tmux kill-session -t main
```

### Q4: 日志文件过大
**原因**: 长时间运行产生大量日志

**解决**:
```bash
# 清空日志文件
> ~/.claude-server/tmux-main.log

# 或删除文件(会自动重建)
rm ~/.claude-server/tmux-main.log
```

## 未来改进

- [ ] 支持命令历史记录
- [ ] 添加命令自动补全
- [ ] 支持日志文件自动清理
- [ ] 添加日志搜索功能
- [ ] 支持批量删除会话
- [ ] 添加会话导出/导入功能
