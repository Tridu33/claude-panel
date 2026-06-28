<template>
  <div class="page">
    <header class="page-header">
      <div class="header-left">
        <span class="logo">⌨️</span>
        <div>
          <h1>Claude 控制面板</h1>
        </div>
      </div>
      <div class="header-right">
        <span :class="['badge', wsConnected ? 'badge-on' : 'badge-off']">
          WS {{ wsConnected ? '连接' : '断开' }}
        </span>
        <select v-model="currentMode" @change="changeMode" title="切换tmux会话" class="tmux-select">
          <option value="" disabled>选择 tmux 会话</option>
          <option v-for="session in tmuxSessions" :key="session.name" :value="session.name">
            {{ session.name }}
          </option>
        </select>
        <button @click="showCreateSessionDialog" class="btn-new-session" title="新增 Session">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          新增
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
          删除
        </button>
      </div>
    </header>

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
              {{ autoRefresh ? '5s' : '自动' }}
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
        <div class="terminal-content" ref="terminalContent">
          <div v-if="!currentSessionName" class="terminal-placeholder">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="48" height="48">
              <polyline points="4 17 10 11 4 5"/>
              <line x1="12" y1="19" x2="20" y2="19"/>
            </svg>
            <p>请从顶部下拉菜单选择一个 tmux 会话</p>
          </div>
          <pre v-else-if="sessionLogs" class="terminal-logs">{{ sessionLogs }}</pre>
          <div v-else class="terminal-loading">
            <div class="loading-spinner"></div>
            <p>加载日志中...</p>
          </div>
        </div>
      </div>

      <!-- 主内容区 + 右侧栏 -->
      <div class="main-layout">
        <!-- 左侧：命令输入 + 事件日志 -->
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

        <!-- 右侧：按键区 + 拨杆 -->
        <div class="sidebar">
          <div class="key-column">
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

            <!-- Enter 键 -->
            <button class="key-btn key-compact" @click="pressKey('enter')" title="提交/执行">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                   stroke-linecap="round" stroke-linejoin="round">
                <polyline points="9 10 4 15 9 20"/>
                <path d="M20 4v7a4 4 0 0 1-4 4H4"/>
              </svg>
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

            <!-- 自动批准拨杆 -->
            <div class="toggle-wrap-compact">
              <div class="toggle-label-small">自动</div>
              <label class="toggle-switch-compact" title="自动批准拨杆">
                <input type="checkbox" v-model="autoApprove" @change="toggleAutoApprove" />
                <span class="slider"></span>
              </label>
            </div>
          </div>
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

export default {
  name: 'ControlPanel',
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
    const logLines = ref(200)
    const autoRefresh = ref(false)
    const loadingLogs = ref(false)
    const terminalContent = ref(null)
    let autoRefreshTimer = null
    
    // 命令输入相关
    const commandInput = ref('')
    const sendingCommand = ref(false)
    
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
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      ws = new WebSocket(`${protocol}//${window.location.host}/ws`)

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
          currentMode.value = data.current_mode.toString()
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
        }, 5000)
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
      if (!currentSessionName.value || !commandInput.value.trim()) return
      
      sendingCommand.value = true
      try {
        const response = await fetch('/api/tmux/send-command', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session: currentSessionName.value,
            command: commandInput.value
          })
        })
        
        const data = await response.json()
        
        if (data.success) {
          // 清空输入框
          commandInput.value = ''
          // 立即刷新日志
          await loadSessionLogs()
        } else {
          alert('发送命令失败: ' + (data.error || '未知错误'))
        }
      } catch (error) {
        console.error('发送命令失败:', error)
        alert('发送命令失败: ' + error.message)
      } finally {
        sendingCommand.value = false
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
/* 页面布局 */
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 头部 */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  font-size: 2.5rem;
}

.header-left h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.badge {
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

.badge-on {
  background: rgba(16, 185, 129, 0.3);
  color: #10b981;
}

.badge-off {
  background: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.tmux-select {
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 200px;
}

.tmux-select:focus {
  outline: none;
  border-color: white;
}

.btn-new-session,
.btn-delete-session-header {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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

/* 键盘机身 */
.keyboard-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 终端区域 */
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
  padding: 1rem 1.5rem;
  background: #2d2d2d;
  border-bottom: 1px solid #3e3e3e;
}

.terminal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
  font-size: 0.95rem;
}

.terminal-controls {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.line-count-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
  font-size: 0.85rem;
}

.line-count-input {
  width: 70px;
  padding: 0.4rem 0.6rem;
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
  gap: 0.4rem;
  padding: 0.5rem 0.75rem;
  background: #374151;
  color: #e2e8f0;
  border: 1px solid #4b5563;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
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

.terminal-content {
  height: 400px;
  overflow-y: auto;
  padding: 1rem;
  background: #0f172a;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
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
  font-size: 0.95rem;
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

/* 主布局 */
.main-layout {
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 1rem;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 命令输入区 */
.command-input-section {
  background: #1e1e1e;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.command-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #10b981;
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 1rem;
}

.command-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.command-textarea {
  width: 100%;
  padding: 1rem;
  background: #0f172a;
  border: 2px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  min-height: 80px;
  max-height: 300px;
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
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
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

/* 日志框 */
.log-box {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.log-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: #374151;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.log-list {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  gap: 1rem;
  font-size: 0.9rem;
}

.log-item:last-child {
  border-bottom: none;
}

.log-time {
  color: #6b7280;
  font-family: monospace;
  min-width: 80px;
}

.log-action {
  color: #374151;
  font-weight: 500;
  min-width: 100px;
}

.log-detail {
  color: #6b7280;
  flex: 1;
}

/* 右侧栏 */
.sidebar {
  background: #f9fafb;
  border-radius: 12px;
  padding: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.key-column {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* 紧凑按键 */
.key-compact {
  padding: 0.75rem !important;
  min-height: auto !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.key-compact svg {
  width: 24px;
  height: 24px;
}

.key-label-small {
  font-size: 0.85rem;
  font-weight: 700;
}

.key-arrow-compact svg {
  width: 20px;
  height: 20px;
}

/* 紧凑拨杆 */
.toggle-wrap-compact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 0.5rem;
  background: white;
  border-radius: 8px;
  margin-top: 0.5rem;
}

.toggle-label-small {
  font-size: 0.75rem;
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

/* 弹窗样式 */
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
}

.modal-content {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
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
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header-warning {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
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
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.2);
}

.modal-body {
  padding: 2rem;
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
  padding: 1.5rem 2rem;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
}

.btn-cancel,
.btn-create {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
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

/* 警告信息 */
.warning-message {
  text-align: center;
  color: #374151;
}

.warning-message svg {
  color: #ef4444;
  margin-bottom: 1rem;
}

.warning-message p {
  margin: 0.75rem 0;
  font-size: 1rem;
}

.warning-message code {
  background: #fef3c7;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  color: #92400e;
  font-weight: 600;
}

.warning-detail {
  color: #6b7280;
  font-size: 0.9rem;
}

.warning-list {
  text-align: left;
  background: #fef3c7;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  margin: 1rem 0;
  list-style-type: disc;
  padding-left: 2.5rem;
}

.warning-list li {
  margin: 0.5rem 0;
  color: #92400e;
  font-size: 0.9rem;
}

.warning-note {
  color: #ef4444;
  font-weight: 600;
  font-size: 0.95rem;
  margin-top: 1rem;
}

.btn-delete-confirm {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
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

/* 按键样式 */
.key-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
}

.key-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.key-btn:active {
  transform: translateY(0);
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
</style>
