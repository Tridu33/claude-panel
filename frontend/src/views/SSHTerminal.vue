<template>
  <div class="ssh-terminal-page">
    <div class="ssh-header">
      <h2>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="24" height="24">
          <polyline points="4 17 10 11 4 5"/>
          <line x1="12" y1="19" x2="20" y2="19"/>
        </svg>
        SSH 终端
      </h2>
      <div class="ssh-status">
        <span :class="['status-badge', connected ? 'connected' : 'disconnected']">
          {{ connected ? '● 已连接' : '○ 未连接' }}
        </span>
        <button v-if="connected" @click="disconnect" class="btn-disconnect">断开连接</button>
      </div>
    </div>

    <!-- 连接表单 -->
    <div v-if="!connected" class="ssh-connect-form">
      <div class="form-card">
        <h3>连接到 SSH 服务器</h3>
        <form @submit.prevent="connect">
          <div class="form-group">
            <label>主机地址 *</label>
            <input 
              type="text" 
              v-model="form.hostname" 
              placeholder="例如: 192.168.1.100 或 example.com" 
              required 
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>端口</label>
              <input 
                type="number" 
                v-model.number="form.port" 
                placeholder="22" 
                min="1" 
                max="65535"
              />
            </div>
            <div class="form-group">
              <label>用户名 *</label>
              <input 
                type="text" 
                v-model="form.username" 
                placeholder="例如: root" 
                required 
              />
            </div>
          </div>

          <div class="form-group">
            <label>认证方式</label>
            <div class="auth-toggle">
              <button 
                type="button" 
                :class="['auth-btn', authMode === 'password' ? 'active' : '']"
                @click="authMode = 'password'"
              >
                密码
              </button>
              <button 
                type="button" 
                :class="['auth-btn', authMode === 'key' ? 'active' : '']"
                @click="authMode = 'key'"
              >
                SSH 密钥
              </button>
            </div>
          </div>

          <div v-if="authMode === 'password'" class="form-group">
            <label>密码</label>
            <input 
              type="password" 
              v-model="form.password" 
              placeholder="输入密码" 
            />
          </div>

          <div v-if="authMode === 'key'" class="form-group">
            <label>私钥文件路径</label>
            <input 
              type="text" 
              v-model="form.key_filename" 
              placeholder="例如: ~/.ssh/id_rsa" 
            />
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <button type="submit" :disabled="connecting" class="btn-connect">
            {{ connecting ? '连接中...' : '连接' }}
          </button>
        </form>
      </div>
    </div>

    <!-- 终端区域 -->
    <div v-if="connected || connecting" class="terminal-container">
      <div ref="terminalRef" class="terminal"></div>
      <div class="terminal-input-bar">
        <input 
          ref="inputRef"
          v-model="commandInput"
          @keyup.enter="executeCommand"
          :disabled="!connected"
          placeholder="输入命令并回车..."
          class="terminal-input"
        />
        <button 
          @click="executeCommand" 
          :disabled="!connected || !commandInput.trim()"
          class="btn-execute"
        >
          执行
        </button>
        <button @click="clearTerminal" class="btn-clear">
          清空
        </button>
      </div>
      
      <!-- 虚拟键盘 -->
      <VirtualKeyboard v-model="commandInput" @send="executeCommand" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'
import 'xterm/css/xterm.css'
import VirtualKeyboard from '../components/VirtualKeyboard.vue'

export default {
  name: 'SSHTerminal',
  components: {
    VirtualKeyboard
  },
  setup() {
    const connected = ref(false)
    const connecting = ref(false)
    const authMode = ref('password')
    const errorMessage = ref('')
    const commandInput = ref('')
    const terminalRef = ref(null)
    const inputRef = ref(null)
    
    const form = ref({
      hostname: '',
      port: 22,
      username: '',
      password: '',
      key_filename: ''
    })

    let ws = null
    let term = null
    let fitAddon = null
    let terminalOutput = ref('')

    const connect = async () => {
      errorMessage.value = ''
      connecting.value = true

      try {
        // 创建 xterm 终端
        await nextTick()
        initTerminal()

        // 建立 WebSocket 连接
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/ssh`)

        ws.onopen = () => {
          console.log('SSH WebSocket 已连接')
          // 发送 SSH 连接请求
          ws.send(JSON.stringify({
            type: 'connect',
            hostname: form.value.hostname,
            port: form.value.port,
            username: form.value.username,
            password: authMode.value === 'password' ? form.value.password : undefined,
            key_filename: authMode.value === 'key' ? form.value.key_filename : undefined
          }))
        }

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data)
          
          if (data.type === 'connect_result') {
            if (data.success) {
              connected.value = true
              connecting.value = false
              term.writeln(`\x1b[32m✓ ${data.message}\x1b[0m`)
              if (data.initial_output) {
                term.write(data.initial_output)
              }
              term.write('\r\n$ ')
              inputRef.value?.focus()
            } else {
              errorMessage.value = data.error
              connecting.value = false
              term.writeln(`\x1b[31m✗ ${data.error}\x1b[0m`)
            }
          } else if (data.type === 'command_result') {
            if (data.output) {
              term.write(data.output)
            }
            term.write('\r\n$ ')
          } else if (data.type === 'disconnect_result') {
            if (data.success) {
              term.writeln(`\x1b[33m${data.message}\x1b[0m`)
            }
          }
        }

        ws.onclose = () => {
          console.log('SSH WebSocket 已断开')
          connected.value = false
        }

        ws.onerror = (error) => {
          console.error('SSH WebSocket 错误:', error)
          errorMessage.value = 'WebSocket 连接失败'
          connecting.value = false
        }

      } catch (error) {
        console.error('连接失败:', error)
        errorMessage.value = `连接失败: ${error.message}`
        connecting.value = false
      }
    }

    const initTerminal = () => {
      if (!terminalRef.value) return

      term = new Terminal({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        theme: {
          background: '#1e1e1e',
          foreground: '#d4d4d4',
          cursor: '#d4d4d4',
          selectionBackground: '#3a3d41',
          black: '#1e1e1e',
          red: '#f44747',
          green: '#6a9955',
          yellow: '#d7ba7d',
          blue: '#569cd6',
          magenta: '#c586c0',
          cyan: '#4dc9b0',
          white: '#d4d4d4'
        }
      })

      fitAddon = new FitAddon()
      term.loadAddon(fitAddon)
      term.open(terminalRef.value)
      fitAddon.fit()

      term.writeln('\x1b[36m╔══════════════════════════════════════════════════════════╗\x1b[0m')
      term.writeln('\x1b[36m║                                                          ║\x1b[0m')
      term.writeln('\x1b[36m║         🔗 SSH Terminal - Claude Panel                  ║\x1b[0m')
      term.writeln('\x1b[36m║                                                          ║\x1b[0m')
      term.writeln('\x1b[36m╚══════════════════════════════════════════════════════════╝\x1b[0m')
      term.writeln('')
      term.writeln('正在连接到 SSH 服务器...')
      term.writeln('')

      // 监听窗口大小变化
      window.addEventListener('resize', () => {
        fitAddon.fit()
      })
    }

    const executeCommand = async () => {
      if (!commandInput.value.trim() || !ws || !connected.value) return

      const command = commandInput.value.trim()
      term.writeln(command)
      commandInput.value = ''

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
          type: 'command',
          command: command
        }))
      }
    }

    const disconnect = () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'disconnect' }))
        ws.close()
      }
      connected.value = false
      if (term) {
        term.writeln('\r\n\x1b[33m已断开连接\x1b[0m')
      }
    }

    const clearTerminal = () => {
      if (term) {
        term.clear()
        term.write('\r\n$ ')
      }
    }

    onMounted(() => {
      // 可以在这里检查之前的连接状态
    })

    onUnmounted(() => {
      if (ws) {
        ws.close()
      }
      if (term) {
        term.dispose()
      }
    })

    return {
      connected,
      connecting,
      authMode,
      errorMessage,
      commandInput,
      terminalRef,
      inputRef,
      form,
      connect,
      executeCommand,
      disconnect,
      clearTerminal
    }
  }
}
</script>

<style scoped>
.ssh-terminal-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.ssh-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.ssh-header h2 {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.75rem;
}

.ssh-status {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-badge {
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
}

.status-badge.connected {
  background: rgba(255, 255, 255, 0.3);
}

.status-badge.disconnected {
  background: rgba(255, 255, 255, 0.15);
}

.btn-disconnect {
  padding: 0.5rem 1.5rem;
  background: rgba(239, 68, 68, 0.8);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-disconnect:hover {
  background: rgba(239, 68, 68, 1);
}

.ssh-connect-form {
  display: flex;
  justify-content: center;
  padding: 2rem;
}

.form-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
}

.form-card h3 {
  margin: 0 0 2rem 0;
  color: #1f2937;
  font-size: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #374151;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #10b981;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
}

.auth-toggle {
  display: flex;
  gap: 0.5rem;
}

.auth-btn {
  flex: 1;
  padding: 0.75rem;
  background: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.auth-btn.active {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.error-message {
  padding: 1rem;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.btn-connect {
  width: 100%;
  padding: 1rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-connect:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.btn-connect:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.terminal-container {
  background: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.terminal {
  height: 600px;
  padding: 1rem;
}

.terminal-input-bar {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
  background: #2d2d2d;
  border-top: 1px solid #3e3e3e;
}

.terminal-input {
  flex: 1;
  padding: 0.75rem;
  background: #1e1e1e;
  color: #d4d4d4;
  border: 2px solid #3e3e3e;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Menlo, Monaco, "Courier New", monospace';
}

.terminal-input:focus {
  outline: none;
  border-color: #10b981;
}

.btn-execute, .btn-clear {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-execute {
  background: #10b981;
  color: white;
}

.btn-execute:hover:not(:disabled) {
  background: #059669;
}

.btn-execute:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-clear {
  background: #6b7280;
  color: white;
}

.btn-clear:hover {
  background: #4b5563;
}
</style>
