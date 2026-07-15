<template>
  <div class="page">
    <!-- Teleport: WS连接状态 & tmux会话选择器 → App.vue 的 #nav-controls -->
    <Teleport to="#nav-controls">
      <div class="header-right">
        <span :class="['badge', wsConnected ? 'badge-on' : 'badge-off']">
          WS {{ wsConnected ? '连接' : '断开' }}
        </span>
        <div class="tmux-select-wrap">
          <select v-model="currentMode" @change="changeMode" title="切换tmux会话" class="tmux-select">
            <option value="" disabled>
              {{ tmuxSessions.length ? '选择 tmux 会话' : '（无活动会话,点击右侧「新增」创建）' }}
            </option>
            <option v-for="session in tmuxSessions" :key="session.name" :value="session.name">
              {{ session.name }}
            </option>
          </select>
        </div>
        <button @click="showCreateSessionDialog" class="btn-new-session" title="新增 Session">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="btn-label">新增</span>
        </button>
        <button
          @click="showDeleteConfirm"
          :disabled="!currentSessionName"
          class="btn-delete-session-header"
          title="删除当前会话"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            <line x1="10" y1="11" x2="10" y2="17"/>
            <line x1="14" y1="11" x2="14" y2="17"/>
          </svg>
          <span class="btn-label">删除</span>
        </button>
      </div>
    </Teleport>

    <!-- 键盘机身 -->
    <div class="keyboard-body">
      <!-- Tmux 会话日志终端 -->
      <div class="terminal-section">
        <div class="terminal-header">
          <div class="terminal-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20">
              <polyline points="4 17 10 11 4 5"/>
              <line x1="12" y1="19" x2="20" y2="19"/>
            </svg>
            <span>{{ currentSessionName ? `会话日志: ${currentSessionName}` : '请选择会话' }}</span>
          </div>
          <div class="terminal-controls">
            <div class="line-count-control">
              <label>行数:</label>
              <input
                type="number"
                v-model.number="logLines"
                @change="loadSessionLogs"
                min="10"
                max="1000"
                class="line-count-input"
              />
            </div>
            <button
              @click="toggleAutoRefresh"
              :class="['btn-auto-refresh', autoRefresh ? 'active' : '']"
              :title="autoRefresh ? '关闭自动刷新' : '开启自动刷新'"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              {{ autoRefresh ? '3s' : '自动' }}
            </button>
            <button @click="loadSessionLogs" :disabled="loadingLogs" class="btn-refresh" title="手动刷新">
              <svg :class="{ 'spinning': loadingLogs }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              刷新
            </button>
          </div>
        </div>
        <div class="terminal-scroll-wrapper">
          <div class="terminal-content" ref="terminalContent">
            <div v-if="!currentSessionName" class="terminal-placeholder">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
                <polyline points="4 17 10 11 4 5"/>
                <line x1="12" y1="19" x2="20" y2="19"/>
              </svg>
              <p>请从顶部导航栏选择一个 tmux 会话</p>
            </div>
            <pre v-else-if="sessionLogs" class="terminal-logs">{{ sessionLogs }}</pre>
            <div v-else class="terminal-loading">
              <div class="loading-spinner"></div>
              <p>加载日志中...</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区（无侧栏，全宽） -->
      <div class="main-content">
        <!-- 命令输入区 -->
        <div class="command-input-section">
          <div class="command-header">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
              <polyline points="4 17 10 11 4 5"/>
              <line x1="12" y1="19" x2="20" y2="19"/>
            </svg>
            <span>发送命令到会话: {{ currentSessionName || '未选择' }}</span>
          </div>
          <div class="command-input-wrapper">
            <textarea
              v-model="commandInput"
              @keydown.ctrl.enter="sendCommand"
              @keydown.meta.enter="sendCommand"
              placeholder="输入命令...\n支持多行输入\nCtrl+Enter 或 ⌘+Enter 发送"
              class="command-textarea"
              rows="3"
            ></textarea>
            <div class="command-buttons">
              <button
                @click="sendCommand"
                :disabled="!currentSessionName || !commandInput.trim() || sendingCommand"
                class="btn-send-command"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
                {{ sendingCommand ? '发送中...' : '发送' }}
              </button>
            </div>
          </div>
        </div>

        <!-- 控制按钮区：7个按键 + 1个自动批准拨杆（从原 sidebar 移入） -->
        <div class="control-buttons">
          <!-- 麦克风键 -->
          <button class="key-btn key-compact" @click="pressKey('mic')" title="语音输入">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="2" width="6" height="12" rx="3"/>
              <path d="M5 10a7 7 0 0 0 14 0"/>
              <line x1="12" y1="19" x2="12" y2="22"/>
              <line x1="8" y1="22" x2="16" y2="22"/>
            </svg>
          </button>

          <!-- YES 键 -->
          <button class="key-btn key-compact key-yes" @click="pressKey('yes')" title="确认">
            <span class="key-label-small">YES</span>
          </button>

          <!-- NO 键 -->
          <button class="key-btn key-compact key-no" @click="pressKey('no')" title="拒绝">
            <span class="key-label-small">NO</span>
          </button>

          <!-- 自动批准拨杆 -->
          <div class="toggle-wrap-compact">
            <div class="toggle-label-small">自动</div>
            <label class="toggle-switch-compact" title="自动批准拨杆">
              <input type="checkbox" v-model="autoApprove" @change="toggleAutoApprove" />
              <span class="slider"></span>
            </label>
          </div>

          <!-- Esc 键 -->
          <button class="key-btn key-compact key-esc" @click="pressKey('esc')" title="退出">
            <span class="key-label-small key-esc-label">esc</span>
          </button>

          <!-- 上键 -->
          <button class="key-btn key-compact key-arrow-compact" @click="pressKey('up')" title="上">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                 stroke-linecap="round" stroke-linejoin="round">
              <polyline points="18 15 12 9 6 15"/>
            </svg>
          </button>

          <!-- 下键 -->
          <button class="key-btn key-compact key-arrow-compact" @click="pressKey('down')" title="下">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                 stroke-linecap="round" stroke-linejoin="round">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </button>

          <!-- Enter 键 -->
          <button class="key-btn key-compact" @click="pressKey('enter')" title="提交/执行">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                 stroke-linecap="round" stroke-linejoin="round">
              <polyline points="9 10 4 15 9 20"/>
              <path d="M20 4v7a4 4 0 0 1-4 4H4"/>
            </svg>
          </button>
        </div>

        <!-- 虚拟键盘 -->
        <VirtualKeyboard v-model="commandInput" @send="sendCommand" />

        <!-- 事件日志 -->
        <div class="log-box">
          <div class="log-title">
            事件日志
            <button @click="clearLogs" class="btn-ghost">清空</button>
          </div>
          <ul class="log-list">
            <li v-for="(log, index) in logs" :key="index" class="log-item">
              <span class="log-time">{{ log.time }}</span>
              <span class="log-action">{{ log.action }}</span>
              <span class="log-detail">{{ log.detail }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 创建会话弹窗 -->
    <div v-if="showDialog" class="modal-overlay" @click="closeDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🆕 新增 Tmux Session</h3>
          <button @click="closeDialog" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>项目路径（绝对路径）</label>
            <input
              type="text"
              v-model="newSessionPath"
              @keyup.enter="createSession"
              placeholder="例如: /Users/mac/codes"
              class="path-input"
              ref="pathInput"
            />
            <div v-if="validationError" class="error-message">{{ validationError }}</div>
            <div v-if="previewName" class="preview-message">
              会话名称预览: <code>{{ previewName }}</code>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDialog" class="btn-cancel">取消</button>
          <button @click="createSession" :disabled="creating" class="btn-create">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 删除会话确认弹窗 -->
    <div v-if="showDeleteDialog" class="modal-overlay" @click="closeDeleteDialog">
      <div class="modal-content modal-small" @click.stop>
        <div class="modal-header modal-header-warning">
          <h3>⚠️ 确认删除会话</h3>
          <button @click="closeDeleteDialog" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div class="warning-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="48" height="48">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <p>确定要删除会话 <code>{{ currentSessionName }}</code> 吗？</p>
            <p class="warning-detail">此操作将：</p>
            <ul class="warning-list">
              <li>停止该会话的日志管道</li>
              <li>终止会话中的所有进程</li>
              <li>删除该 tmux 会话</li>
            </ul>
            <p class="warning-note">此操作不可撤销！</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeDeleteDialog" class="btn-cancel">取消</button>
          <button @click="confirmDeleteSession" :disabled="deletingSession" class="btn-delete-confirm">
            {{ deletingSession ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 这里保持原有script内容不变，仅修改template
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import VirtualKeyboard from '../components/VirtualKeyboard.vue'
import { wsUrl } from '../auth'

export default {
  name: 'ControlPanel',
  components: {
    VirtualKeyboard
  },
  setup() {
    const wsConnected = ref(false)
    const currentMode = ref('')
    const lcdMessage = ref('Ready')
    const lcdInput = ref('')
    const autoApprove = ref(false)
    const logs = ref([])
    const ledStatus = ref([0, 0, 0, 0, 0, 0, 0])
    const tmuxSessions = ref([])
    
    // 终端日志相关
    const sessionLogs = ref('')
    const logLines = ref(60)
    const autoRefresh = ref(true)  // 默认开启自动刷新
    const loadingLogs = ref(false)
    const terminalContent = ref(null)
    let autoRefreshTimer = null
    
    // 命令输入相关
    const commandInput = ref('')
    const sendingCommand = ref(false)
    
    // 虚拟键盘相关
    const shiftActive = ref(false)
    const ctrlActive = ref(false)
    const altActive = ref(false)
    const capsActive = ref(false)
    
    // 虚拟键盘输入处理
    const handleVirtualKey = (key) => {
      // 处理特殊键
      if (key === 'Shift') {
        shiftActive.value = !shiftActive.value
        return
      }
      if (key === 'Ctrl') {
        ctrlActive.value = !ctrlActive.value
        return
      }
      if (key === 'Alt') {
        altActive.value = !altActive.value
        return
      }
      if (key === 'Caps') {
        capsActive.value = !capsActive.value
        return
      }
      
      // 处理 Backspace
      if (key === 'Backspace') {
        commandInput.value = commandInput.value.slice(0, -1)
        return
      }
      
      // 处理 Enter
      if (key === 'Enter') {
        commandInput.value += '\n'
        return
      }
      
      // 处理 Space
      if (key === 'Space') {
        commandInput.value += ' '
        return
      }
      
      // 处理 Tab
      if (key === 'Tab') {
        commandInput.value += '  '
        return
      }
      
      // 处理 Del
      if (key === 'Del') {
        // Del 键通常删除光标后的字符，这里简化为不做操作
        return
      }
      
      // 普通字符输入
      let char = key
      
      // 如果 Shift 或 Caps 激活，转换为大写
      if (shiftActive.value || capsActive.value) {
        if (char.length === 1 && char.match(/[a-z]/)) {
          char = char.toUpperCase()
        }
        // Shift 点击后自动关闭
        if (shiftActive.value) {
          shiftActive.value = false
        }
      }
      
      // 添加修饰键前缀
      let prefix = ''
      if (ctrlActive.value) prefix += 'Ctrl+'
      if (altActive.value) prefix += 'Alt+'
      
      commandInput.value += prefix + char
    }
    
    // 删除会话相关
    const showDeleteDialog = ref(false)
    const deletingSession = ref(false)
    
    // 弹窗相关
    const showDialog = ref(false)
    const newSessionPath = ref('')
    const validationError = ref('')
    const creating = ref(false)
    const pathInput = ref(null)
    
    let ws = null
    let reconnectTimer = null
    let refreshTimer = null

    // 当前选中的会话名称
    const currentSessionName = computed(() => {
      return currentMode.value || ''
    })

    // 预览会话名称
    const previewName = computed(() => {
      const path = newSessionPath.value.trim()
      if (!path) return ''
      
      // 转换为反向域名
      const cleanPath = path.replace(/\/+$/, '') // 移除末尾的斜杠
      const parts = cleanPath.split('/').filter(p => p)
      parts.reverse()
      return parts.join('.')
    })

    const getLedClass = (index) => {
      const status = ledStatus.value[index]
      if (status === 0) return 'off'
      if (status === 1) return 'on'
      if (status === 2) return 'running'
      return 'off'
    }

    const connectWebSocket = () => {
      ws = new WebSocket(wsUrl('/ws'))

      ws.onopen = () => {
        wsConnected.value = true
        console.log('WebSocket 已连接')
      }

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'state') {
          autoApprove.value = data.auto_approve
          ledStatus.value = data.led_status
          lcdMessage.value = data.lcd_message
          // 只在 current_mode 是 tmux 会话名称时才更新
          if (data.current_mode && !['0', '1', '2'].includes(data.current_mode.toString())) {
            currentMode.value = data.current_mode.toString()
          }
          if (data.logs) {
            logs.value = data.logs
          }
        }
      }

      ws.onclose = () => {
        wsConnected.value = false
        console.log('WebSocket 已断开，3秒后重连...')
        reconnectTimer = setTimeout(connectWebSocket, 3000)
      }

      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error)
      }
    }

    const sendWsCommand = (data) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data))
      }
    }

    const pressKey = (key) => {
      sendWsCommand({ type: 'keypress', key })
    }

    const toggleAutoApprove = () => {
      sendWsCommand({ type: 'toggle_auto_approve' })
    }

    // Tmux 会话日志相关

    const loadSessionLogs = async () => {
      if (!currentSessionName.value) return
      
      loadingLogs.value = true
      try {
        const response = await fetch(`/api/tmux/logs?session=${encodeURIComponent(currentSessionName.value)}&lines=${logLines.value}`)
        const data = await response.json()
        
        if (data.success) {
          sessionLogs.value = data.logs
          // 自动滚动到底部
          await nextTick()
          if (terminalContent.value) {
            terminalContent.value.scrollTop = terminalContent.value.scrollHeight
          }
        } else {
          sessionLogs.value = `错误: ${data.error || '加载日志失败'}`
        }
      } catch (error) {
        console.error('加载会话日志失败:', error)
        sessionLogs.value = `加载失败: ${error.message}`
      } finally {
        loadingLogs.value = false
      }
    }

    const toggleAutoRefresh = () => {
      autoRefresh.value = !autoRefresh.value
      
      if (autoRefresh.value) {
        // 开启自动刷新
        autoRefreshTimer = setInterval(() => {
          loadSessionLogs()
        }, 3000)
      } else {
        // 关闭自动刷新
        if (autoRefreshTimer) {
          clearInterval(autoRefreshTimer)
          autoRefreshTimer = null
        }
      }
    }

    // 发送命令到 tmux 会话
    const sendCommand = async () => {
      console.log('[ControlPanel] sendCommand 被调用')
      console.log('[ControlPanel] 当前选中的会话:', currentSessionName.value)
      console.log('[ControlPanel] 输入框内容:', commandInput.value)
      
      if (!currentSessionName.value) {
        console.warn('[ControlPanel] 未选择会话')
        alert('请先选择一个 tmux 会话')
        return
      }
      
      // 如果输入框为空，不发送
      const command = commandInput.value
      if (!command || !command.trim()) {
        console.warn('[ControlPanel] 命令为空')
        return
      }
      
      console.log('[ControlPanel] 准备发送命令:', command)
      
      sendingCommand.value = true
      try {
        console.log('[ControlPanel] 发送 POST 请求到 /api/tmux/send-command')
        
        const response = await fetch('/api/tmux/send-command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session: currentSessionName.value,
            command: command  // 直接发送输入框内容，包含数字和回车
          })
        })
        
        console.log('[ControlPanel] 收到响应，状态:', response.status)
        
        const data = await response.json()
        console.log('[ControlPanel] 响应数据:', data)
        
        if (data.success) {
          console.log('[ControlPanel] 命令发送成功')
          // 清空输入框
          commandInput.value = ''
          // 立即刷新日志
          await loadSessionLogs()
        } else {
          console.error('[ControlPanel] 命令发送失败:', data.error)
          alert('发送命令失败: ' + (data.error || '未知错误'))
        }
      } catch (error) {
        console.error('[ControlPanel] 请求异常:', error)
        alert('发送命令失败: ' + error.message)
      } finally {
        sendingCommand.value = false
        console.log('[ControlPanel] sendCommand 执行完毕')
      }
    }

    // 显示删除确认弹窗
    const showDeleteConfirm = () => {
      showDeleteDialog.value = true
    }

    // 关闭删除弹窗
    const closeDeleteDialog = () => {
      showDeleteDialog.value = false
    }

    // 确认删除会话
    const confirmDeleteSession = async () => {
      if (!currentSessionName.value) return
      
      deletingSession.value = true
      try {
        const response = await fetch('/api/tmux/delete-session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session: currentSessionName.value
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 关闭弹窗
          closeDeleteDialog()
          // 清空当前选择
          currentMode.value = ''
          // 清空日志
          sessionLogs.value = ''
          // 刷新会话列表
          await loadTmuxSessions()
          // 提示成功
          alert(data.message || '会话已删除')
        } else {
          alert('删除失败: ' + (data.error || '未知错误'))
        }
      } catch (error) {
        console.error('删除会话失败:', error)
        alert('删除失败: ' + error.message)
      } finally {
        deletingSession.value = false
      }
    }

    const clearLogs = () => {
      logs.value = []
    }

    // Tmux 相关方法
    const loadTmuxSessions = async () => {
      try {
        const response = await fetch('/api/tmux/sessions')
        const data = await response.json()
        if (data.success) {
          tmuxSessions.value = data.sessions
        }
      } catch (error) {
        console.error('加载 tmux 会话失败:', error)
      }
    }

    const validatePath = (path) => {
      if (!path.startsWith('/')) {
        return '路径必须是绝对路径'
      }
      if (path === '/') {
        return '不允许使用根路径 /'
      }
      if (path.includes('~')) {
        return '不允许使用 ~ 符号，请使用完整路径'
      }
      return ''
    }

    const showCreateSessionDialog = async () => {
      showDialog.value = true
      newSessionPath.value = ''
      validationError.value = ''
      await nextTick()
      pathInput.value?.focus()
    }

    const closeDialog = () => {
      showDialog.value = false
      newSessionPath.value = ''
      validationError.value = ''
    }

    const createSession = async () => {
      const path = newSessionPath.value.trim()
      
      // 验证路径
      const error = validatePath(path)
      if (error) {
        validationError.value = error
        return
      }
      
      if (!path) {
        validationError.value = '请输入路径'
        return
      }
      
      creating.value = true
      validationError.value = ''
      
      try {
        const response = await fetch('/api/tmux/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path })
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 刷新会话列表
          await loadTmuxSessions()
          // 切换到新会话
          currentMode.value = data.session_name
          await changeMode()
          // 关闭弹窗
          closeDialog()
          // 显示成功消息
          lcdMessage.value = data.message
        } else {
          validationError.value = data.error || '创建失败'
        }
      } catch (error) {
        console.error('创建会话失败:', error)
        validationError.value = '创建失败: ' + error.message
      } finally {
        creating.value = false
      }
    }

    const changeMode = async () => {
      if (!currentMode.value) return
      
      try {
        const response = await fetch('/api/tmux/attach', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_name: currentMode.value })
        })
        
        const data = await response.json()
        
        if (data.success) {
          lcdMessage.value = data.message
        } else {
          console.error('切换会话失败:', data.error)
        }
      } catch (error) {
        console.error('切换会话失败:', error)
      }
    }

    onMounted(() => {
      connectWebSocket()
      loadTmuxSessions()
      // 每 5 秒刷新一次会话列表
      refreshTimer = setInterval(loadTmuxSessions, 5000)
      
      // 如果自动刷新默认开启，启动日志自动刷新
      if (autoRefresh.value) {
        autoRefreshTimer = setInterval(() => {
          loadSessionLogs()
        }, 3000)
      }
    })

    onUnmounted(() => {
      if (ws) {
        ws.close()
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer)
      }
      if (refreshTimer) {
        clearInterval(refreshTimer)
      }
      if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer)
      }
    })

    return {
      wsConnected,
      currentMode,
      currentSessionName,
      lcdMessage,
      lcdInput,
      autoApprove,
      logs,
      tmuxSessions,
      sessionLogs,
      logLines,
      autoRefresh,
      loadingLogs,
      terminalContent,
      commandInput,
      sendingCommand,
      shiftActive,
      ctrlActive,
      altActive,
      capsActive,
      handleVirtualKey,
      showDeleteDialog,
      deletingSession,
      showDialog,
      newSessionPath,
      validationError,
      creating,
      previewName,
      pathInput,
      getLedClass,
      pressKey,
      toggleAutoApprove,
      changeMode,
      clearLogs,
      showCreateSessionDialog,
      closeDialog,
      createSession,
      loadSessionLogs,
      toggleAutoRefresh,
      sendCommand,
      showDeleteConfirm,
      closeDeleteDialog,
      confirmDeleteSession
    }
  }
}
</script>

<style scoped>
/* ================================================================
   页面布局 — 相对/自适应，不写死固定宽度
   ================================================================ */
.page {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: clamp(0.5rem, 1.5vw, 1rem);
  display: flex;
  flex-direction: column;
  gap: clamp(0.5rem, 1.2vw, 1rem);
}

/* ---- Teleport 到 #nav-controls 的 WS / tmux 控件 ---- */
.header-right {
  display: flex;
  align-items: center;
  gap: clamp(0.3rem, 0.8vw, 0.75rem);
  flex-wrap: wrap;
  justify-content: center;
}

.badge {
  padding: 0.3rem 0.65rem;
  border-radius: 20px;
  font-size: clamp(0.7rem, 1vw, 0.8rem);
  font-weight: 600;
  white-space: nowrap;
}

.badge-on {
  background: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.badge-off {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.tmux-select-wrap {
  display: inline-flex;
  align-items: center;
  min-width: 0;
}

.tmux-select {
  padding: 0.4rem 0.75rem;
  background: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: clamp(0.75rem, 1vw, 0.9rem);
  cursor: pointer;
  min-width: clamp(140px, 16vw, 200px);
  max-width: 360px;
}

.tmux-select:focus {
  outline: none;
  border-color: white;
}

.btn-new-session,
.btn-delete-session-header {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.75rem;
  border: none;
  border-radius: 8px;
  font-size: clamp(0.7rem, 0.9vw, 0.85rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-new-session {
  background: rgba(16, 185, 129, 0.9);
  color: white;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.btn-new-session:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.btn-delete-session-header {
  background: rgba(239, 68, 68, 0.9);
  color: white;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.btn-delete-session-header:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
}

.btn-delete-session-header:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ---- 键盘机身 ---- */
.keyboard-body {
  display: flex;
  flex-direction: column;
  gap: clamp(0.5rem, 1.2vw, 1rem);
}

/* ---- 终端区域 ---- */
.terminal-section {
  background: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.terminal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: clamp(0.6rem, 1.2vw, 1rem) clamp(0.75rem, 1.5vw, 1.5rem);
  background: #2d2d2d;
  border-bottom: 1px solid #3e3e3e;
}

.terminal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
  font-size: clamp(0.8rem, 1.1vw, 0.95rem);
}

.terminal-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.line-count-control {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #9ca3af;
  font-size: clamp(0.7rem, 0.9vw, 0.85rem);
}

.line-count-input {
  width: clamp(50px, 8vw, 70px);
  padding: 0.35rem 0.5rem;
  background: #1e1e1e;
  border: 1px solid #3e3e3e;
  border-radius: 6px;
  color: #e2e8f0;
  font-size: 0.85rem;
  text-align: center;
}

.line-count-input:focus {
  outline: none;
  border-color: #10b981;
}

.btn-auto-refresh,
.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.4rem 0.6rem;
  background: #374151;
  color: #e2e8f0;
  border: 1px solid #4b5563;
  border-radius: 6px;
  font-size: clamp(0.7rem, 0.85vw, 0.8rem);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-auto-refresh:hover,
.btn-refresh:hover:not(:disabled) {
  background: #4b5563;
  border-color: #6b7280;
}

.btn-auto-refresh.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 终端滚动包裹层（提供横向滚动条） */
.terminal-scroll-wrapper {
  position: relative;
  overflow-x: auto;
  overflow-y: hidden;
}

.terminal-scroll-wrapper::-webkit-scrollbar {
  height: 8px;
}

.terminal-scroll-wrapper::-webkit-scrollbar-track {
  background: #1e293b;
  border-radius: 4px;
}

.terminal-scroll-wrapper::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

.terminal-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

.terminal-content {
  min-width: 100%;
  height: clamp(250px, 40vh, 400px);
  overflow-y: auto;
  padding: clamp(0.5rem, 1.2vw, 1rem);
  background: #0f172a;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: clamp(0.7rem, 0.95vw, 0.85rem);
  line-height: 1.5;
}

.terminal-content::-webkit-scrollbar {
  width: 8px;
}

.terminal-content::-webkit-scrollbar-track {
  background: #1e293b;
}

.terminal-content::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

.terminal-content::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

.terminal-placeholder,
.terminal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
  color: #64748b;
  gap: 1rem;
}

.terminal-placeholder svg,
.terminal-loading svg {
  opacity: 0.5;
}

.terminal-placeholder p,
.terminal-loading p {
  margin: 0;
  font-size: clamp(0.8rem, 1vw, 0.95rem);
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #334155;
  border-top-color: #10b981;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.terminal-logs {
  margin: 0;
  padding: 0;
  color: #e2e8f0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
}

/* ---- 主内容区（全宽，无侧栏） ---- */
.main-content {
  display: flex;
  flex-direction: column;
  gap: clamp(0.5rem, 1.2vw, 1rem);
  width: 100%;
}

/* ---- 命令输入区 ---- */
.command-input-section {
  background: #1e1e1e;
  border-radius: 12px;
  padding: clamp(0.75rem, 1.5vw, 1.5rem);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.command-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
  font-size: clamp(0.8rem, 1.1vw, 0.95rem);
  margin-bottom: clamp(0.5rem, 1vw, 1rem);
}

.command-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.command-textarea {
  width: 100%;
  padding: clamp(0.5rem, 1vw, 1rem);
  background: #0f172a;
  border: 2px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: clamp(0.75rem, 0.95vw, 0.9rem);
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  max-height: 300px;
  box-sizing: border-box;
}

.command-textarea:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.command-textarea::placeholder {
  color: #64748b;
}

.command-buttons {
  display: flex;
  gap: 0.75rem;
}

.btn-send-command {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: clamp(0.8rem, 0.95vw, 0.9rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
  flex: 1;
}

.btn-send-command:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.btn-send-command:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* ---- 虚拟键盘（组件根元素样式穿透） ---- */
:deep(.virtual-keyboard) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

/* ================================================================
   控制按钮区 — 7 键 + 1 拨杆（原 sidebar 内容移入）
   ================================================================ */
.control-buttons {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: clamp(0.4rem, 1vw, 0.75rem);
  padding: clamp(0.5rem, 1.2vw, 1rem);
  background: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 按键基础 */
.key-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: clamp(48px, 8vw, 70px);
  height: clamp(48px, 8vw, 70px);
  padding: 0.5rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  flex-shrink: 0;
}

.key-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.key-btn:active {
  transform: translateY(0);
}

.key-compact {
  padding: 0.4rem;
}

.key-compact svg {
  width: clamp(12px, 2vw, 16px);
  height: clamp(12px, 2vw, 16px);
}

.key-label-small {
  font-size: clamp(0.65rem, 0.9vw, 0.75rem);
  font-weight: 700;
}

.key-yes {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-color: #10b981;
}

.key-no {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border-color: #ef4444;
}

.key-esc {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-color: rgba(251, 191, 36, 0.3);
}

.key-esc:hover {
  background: linear-gradient(135deg, #fde68a 0%, #fcd34d 100%);
}

.key-esc-label {
  background: none;
  color: #92400e;
  padding: 0;
  font-weight: 700;
}

.key-arrow-compact svg {
  width: clamp(12px, 2vw, 16px);
  height: clamp(12px, 2vw, 16px);
}

/* 按键波纹 */
.key-ripple {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.6);
  transform: scale(0);
  animation: ripple 0.6s linear;
  pointer-events: none;
}

@keyframes ripple {
  to {
    transform: scale(4);
    opacity: 0;
  }
}

/* ---- 紧凑拨杆 ---- */
.toggle-wrap-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.6rem;
  background: white;
  border-radius: 8px;
  flex-shrink: 0;
}

.toggle-label-small {
  font-size: clamp(0.65rem, 0.8vw, 0.75rem);
  color: #6b7280;
  font-weight: 600;
}

.toggle-switch-compact {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.toggle-switch-compact input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-switch-compact .slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.toggle-switch-compact .slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

.toggle-switch-compact input:checked + .slider {
  background-color: #10b981;
}

.toggle-switch-compact input:checked + .slider:before {
  transform: translateX(20px);
}

/* ---- 事件日志 ---- */
.log-box {
  background: white;
  border-radius: 12px;
  padding: clamp(0.75rem, 1.5vw, 1.5rem);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.log-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #374151;
  margin-bottom: clamp(0.5rem, 1vw, 1rem);
  font-size: clamp(0.9rem, 1.2vw, 1.1rem);
}

.log-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: clamp(180px, 30vh, 300px);
  overflow-y: auto;
}

.log-item {
  padding: clamp(0.4rem, 0.8vw, 0.75rem);
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  gap: clamp(0.4rem, 0.8vw, 1rem);
  font-size: clamp(0.75rem, 0.9vw, 0.9rem);
  flex-wrap: wrap;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #6b7280;
  font-family: monospace;
  min-width: 70px;
  flex-shrink: 0;
}

.log-action {
  color: #374151;
  font-weight: 500;
  min-width: 80px;
  flex-shrink: 0;
}

.log-detail {
  color: #6b7280;
  flex: 1;
  min-width: 120px;
}

/* ---- 弹窗 ---- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  animation: modalSlideIn 0.3s ease-out;
}

.modal-small {
  max-width: 500px;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header-warning {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.modal-header h3 {
  margin: 0;
  font-size: clamp(1rem, 1.4vw, 1.25rem);
  font-weight: 600;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
  flex-shrink: 0;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: clamp(1rem, 2vw, 2rem);
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-weight: 500;
  font-size: 0.9rem;
}

.path-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  transition: all 0.2s;
  box-sizing: border-box;
}

.path-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.error-message {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
}

.preview-message {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #e0f2fe;
  color: #0369a1;
  border-radius: 6px;
  font-size: 0.85rem;
}

.preview-message code {
  background: #bae6fd;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-weight: 600;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  flex-wrap: wrap;
}

.btn-cancel,
.btn-create,
.btn-delete-confirm {
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  font-size: clamp(0.85rem, 1vw, 0.95rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: white;
  color: #374151;
  border: 2px solid #d1d5db;
}

.btn-cancel:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
}

.btn-create {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.btn-create:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.4);
}

.btn-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-delete-confirm {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  box-shadow: 0 2px 4px rgba(239, 68, 68, 0.3);
}

.btn-delete-confirm:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.4);
}

.btn-delete-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

/* 警告信息 */
.warning-message {
  text-align: center;
  color: #374151;
}

.warning-message svg {
  color: #ef4444;
  margin-bottom: 1rem;
  width: clamp(36px, 6vw, 48px);
  height: clamp(36px, 6vw, 48px);
}

.warning-message p {
  margin: 0.6rem 0;
  font-size: clamp(0.85rem, 1vw, 1rem);
}

.warning-message code {
  background: #fef3c7;
  padding: 0.2rem 0.45rem;
  border-radius: 4px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  color: #92400e;
  font-weight: 600;
  word-break: break-all;
}

.warning-detail {
  color: #6b7280;
  font-size: 0.9rem;
}

.warning-list {
  text-align: left;
  background: #fef3c7;
  padding: 0.8rem 1.2rem;
  border-radius: 8px;
  margin: 0.8rem 0;
  list-style-type: disc;
  padding-left: 2rem;
}

.warning-list li {
  margin: 0.4rem 0;
  color: #92400e;
  font-size: clamp(0.8rem, 0.9vw, 0.9rem);
}

.warning-note {
  color: #ef4444;
  font-weight: 600;
  font-size: 0.9rem;
  margin-top: 0.8rem;
}

.btn-ghost {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.btn-ghost:hover {
  background: #f3f4f6;
}

/* ================================================================
   响应式断点 — 平板
   ================================================================ */
@media (max-width: 768px) {
  .page {
    padding: 0.4rem;
    gap: 0.5rem;
  }

  .header-right {
    gap: 0.3rem;
  }

  .tmux-select {
    min-width: 120px;
    font-size: 0.75rem;
  }

  .btn-label {
    display: none;
  }

  .btn-new-session,
  .btn-delete-session-header {
    padding: 0.35rem 0.55rem;
  }

  .terminal-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .terminal-content {
    height: clamp(200px, 35vh, 300px);
    font-size: 0.7rem;
  }

  .control-buttons {
    gap: 0.4rem;
    padding: 0.5rem 0.6rem;
  }

  .key-btn {
    width: clamp(40px, 12vw, 56px);
    height: clamp(40px, 12vw, 56px);
  }

  .log-list {
    max-height: 180px;
  }

  .log-item {
    flex-direction: column;
    gap: 0.2rem;
  }

  .log-time,
  .log-action {
    min-width: auto;
  }

  .command-textarea {
    font-size: 16px; /* 防止iOS缩放 */
  }

  .modal-content {
    margin: 0.5rem;
    max-height: 85vh;
  }
}

/* ================================================================
   响应式断点 — 手机
   ================================================================ */
@media (max-width: 480px) {
  .page {
    padding: 0.25rem;
    gap: 0.4rem;
  }

  .header-right {
    gap: 0.2rem;
  }

  .badge {
    font-size: 0.65rem;
    padding: 0.2rem 0.45rem;
  }

  .tmux-select {
    min-width: 100px;
    max-width: 160px;
    font-size: 0.7rem;
  }

  .terminal-header {
    padding: 0.5rem 0.6rem;
  }

  .terminal-title {
    font-size: 0.75rem;
  }

  .terminal-content {
    height: 180px;
    min-width: 480px; /* 强制最小宽度，保证内容不挤压，启用横向滚动条 */
    font-size: 0.65rem;
    padding: 0.4rem;
  }

  .terminal-scroll-wrapper {
    -webkit-overflow-scrolling: touch;
  }

  .terminal-scroll-wrapper::-webkit-scrollbar {
    height: 6px;
  }

  .control-buttons {
    gap: 0.3rem;
    padding: 0.4rem;
  }

  .key-btn {
    width: clamp(36px, 14vw, 48px);
    height: clamp(36px, 14vw, 48px);
    border-radius: 6px;
  }

  .key-compact svg {
    width: 12px;
    height: 12px;
  }

  .key-label-small {
    font-size: 0.6rem;
  }

  .toggle-wrap-compact {
    padding: 0.3rem 0.4rem;
  }

  .toggle-label-small {
    font-size: 0.6rem;
  }

  .command-input-section {
    padding: 0.6rem;
  }

  .btn-send-command {
    padding: 0.6rem 1rem;
    font-size: 0.8rem;
  }

  .log-box {
    padding: 0.6rem;
  }

  .log-item {
    padding: 0.4rem;
  }

  .modal-header {
    padding: 0.8rem 1rem;
  }

  .modal-body {
    padding: 0.8rem;
  }

  .modal-footer {
    padding: 0.6rem 1rem;
  }
}
</style>
