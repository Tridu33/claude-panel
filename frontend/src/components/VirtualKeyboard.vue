<template>
  <div class="virtual-keyboard">
    <div class="keyboard-row">
      <button @click="handleVirtualKey('`')" class="key key-number">`</button>
      <button @click="handleVirtualKey('1')" class="key key-number">1</button>
      <button @click="handleVirtualKey('2')" class="key key-number">2</button>
      <button @click="handleVirtualKey('3')" class="key key-number">3</button>
      <button @click="handleVirtualKey('4')" class="key key-number">4</button>
      <button @click="handleVirtualKey('5')" class="key key-number">5</button>
      <button @click="handleVirtualKey('6')" class="key key-number">6</button>
      <button @click="handleVirtualKey('7')" class="key key-number">7</button>
      <button @click="handleVirtualKey('8')" class="key key-number">8</button>
      <button @click="handleVirtualKey('9')" class="key key-number">9</button>
      <button @click="handleVirtualKey('0')" class="key key-number">0</button>
      <button @click="handleVirtualKey('-')" class="key key-number">-</button>
      <button @click="handleVirtualKey('=')" class="key key-number">=</button>
      <button @click="handleVirtualKey('Backspace')" class="key key-wide key-function">⌫ Del</button>
    </div>
    <div class="keyboard-row">
      <button @click="handleVirtualKey('Tab')" class="key key-tab key-function">Tab</button>
      <button @click="handleVirtualKey('q')" class="key key-letter">q</button>
      <button @click="handleVirtualKey('w')" class="key key-letter">w</button>
      <button @click="handleVirtualKey('e')" class="key key-letter">e</button>
      <button @click="handleVirtualKey('r')" class="key key-letter">r</button>
      <button @click="handleVirtualKey('t')" class="key key-letter">t</button>
      <button @click="handleVirtualKey('y')" class="key key-letter">y</button>
      <button @click="handleVirtualKey('u')" class="key key-letter">u</button>
      <button @click="handleVirtualKey('i')" class="key key-letter">i</button>
      <button @click="handleVirtualKey('o')" class="key key-letter">o</button>
      <button @click="handleVirtualKey('p')" class="key key-letter">p</button>
      <button @click="handleVirtualKey('[')" class="key key-symbol">[</button>
      <button @click="handleVirtualKey(']')" class="key key-symbol">]</button>
      <button @click="handleVirtualKey('\\')" class="key key-symbol">\</button>
    </div>
    <div class="keyboard-row">
      <button @click="handleVirtualKey('Caps')" :class="['key', 'key-modifier', 'key-caps', { 'key-active': capsActive }]">Caps</button>
      <button @click="handleVirtualKey('a')" class="key key-letter">a</button>
      <button @click="handleVirtualKey('s')" class="key key-letter">s</button>
      <button @click="handleVirtualKey('d')" class="key key-letter">d</button>
      <button @click="handleVirtualKey('f')" class="key key-letter">f</button>
      <button @click="handleVirtualKey('g')" class="key key-letter">g</button>
      <button @click="handleVirtualKey('h')" class="key key-letter">h</button>
      <button @click="handleVirtualKey('j')" class="key key-letter">j</button>
      <button @click="handleVirtualKey('k')" class="key key-letter">k</button>
      <button @click="handleVirtualKey('l')" class="key key-letter">l</button>
      <button @click="handleVirtualKey(';')" class="key key-symbol">;</button>
      <button @click="handleVirtualKey(`'`)" class="key key-symbol">'</button>
      <button @click="handleVirtualKey('Enter')" class="key key-enter">↵ Enter</button>
    </div>
    <div class="keyboard-row">
      <button @click="handleVirtualKey('Shift')" :class="['key', 'key-special', 'key-shift', { 'key-active': shiftActive }]">⇧ Shift</button>
      <button @click="handleVirtualKey('z')" class="key key-letter">z</button>
      <button @click="handleVirtualKey('x')" class="key key-letter">x</button>
      <button @click="handleVirtualKey('c')" class="key key-letter">c</button>
      <button @click="handleVirtualKey('v')" class="key key-letter">v</button>
      <button @click="handleVirtualKey('b')" class="key key-letter">b</button>
      <button @click="handleVirtualKey('n')" class="key key-letter">n</button>
      <button @click="handleVirtualKey('m')" class="key key-letter">m</button>
      <button @click="handleVirtualKey(',')" class="key key-symbol">,</button>
      <button @click="handleVirtualKey('.')" class="key key-symbol">.</button>
      <button @click="handleVirtualKey('/')" class="key key-symbol">/</button>
      <button @click="handleVirtualKey('Shift')" :class="['key', 'key-special', 'key-shift', { 'key-active': shiftActive }]">⇧ Shift</button>
    </div>
    <div class="keyboard-row">
      <button @click="handleVirtualKey('Ctrl')" :class="['key', 'key-modifier', 'key-ctrl', { 'key-active': ctrlActive }]">Ctrl</button>
      <button @click="handleVirtualKey('Alt')" :class="['key', 'key-modifier', 'key-alt', { 'key-active': altActive }]">Alt</button>
      <button @click="handleVirtualKey('Space')" class="key key-space">Space</button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'VirtualKeyboard',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'send'],
  setup(props, { emit }) {
    const shiftActive = ref(false)
    const ctrlActive = ref(false)
    const altActive = ref(false)
    const capsActive = ref(false)

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
        emit('update:modelValue', props.modelValue.slice(0, -1))
        return
      }

      // 处理 Enter
      if (key === 'Enter') {
        console.log('[VirtualKeyboard] Enter 键被点击')
        console.log('[VirtualKeyboard] 当前输入内容:', props.modelValue)
        // 直接触发 send 事件，发送当前输入内容
        emit('send')
        console.log('[VirtualKeyboard] 已触发 send 事件')
        return
      }

      // 处理 Space
      if (key === 'Space') {
        emit('update:modelValue', props.modelValue + ' ')
        return
      }

      // 处理 Tab
      if (key === 'Tab') {
        emit('update:modelValue', props.modelValue + '  ')
        return
      }

      // 处理 Del
      if (key === 'Del') {
        return
      }
      
      // 处理 Esc
      if (key === 'Esc' || key === 'esc') {
        emit('send')
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

      emit('update:modelValue', props.modelValue + prefix + char)
    }

    return {
      shiftActive,
      ctrlActive,
      altActive,
      capsActive,
      handleVirtualKey
    }
  }
}
</script>

<style scoped>
/* 虚拟键盘 */
.virtual-keyboard {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 1rem;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.keyboard-row {
  display: flex;
  gap: 0.4rem;
  margin-bottom: 0.4rem;
  justify-content: center;
}

.keyboard-row:last-child {
  margin-bottom: 0;
}

.key {
  flex: 1;
  max-width: 60px;
  padding: 0.75rem 0.5rem;
  background: linear-gradient(145deg, #ffffff 0%, #f3f4f6 100%);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.key:hover {
  background: linear-gradient(145deg, #f9fafb 0%, #e5e7eb 100%);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.key:active {
  transform: translateY(0);
  background: linear-gradient(145deg, #e5e7eb 0%, #d1d5db 100%);
}

/* 数字键 - 橙色渐变 */
.key-number {
  background: linear-gradient(145deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-color: rgba(251, 191, 36, 0.3);
}

.key-number:hover {
  background: linear-gradient(145deg, #fde68a 0%, #fcd34d 100%);
}

/* 字母键 - 蓝紫渐变 */
.key-letter {
  background: linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%);
  color: #1e40af;
  border-color: rgba(147, 197, 253, 0.3);
}

.key-letter:hover {
  background: linear-gradient(145deg, #bfdbfe 0%, #93c5fd 100%);
}

/* 符号键 - 粉色渐变 */
.key-symbol {
  background: linear-gradient(145deg, #fce7f3 0%, #fbcfe8 100%);
  color: #9d174d;
  border-color: rgba(251, 207, 232, 0.3);
}

.key-symbol:hover {
  background: linear-gradient(145deg, #fbcfe8 0%, #f9a8d4 100%);
}

/* 功能键 - 青绿渐变 */
.key-function {
  background: linear-gradient(145deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border-color: rgba(167, 243, 208, 0.3);
}

.key-function:hover {
  background: linear-gradient(145deg, #a7f3d0 0%, #6ee7b7 100%);
}

.key-special {
  background: linear-gradient(145deg, #fef3c7 0%, #fde68a 100%);
  border-color: rgba(251, 191, 36, 0.3);
  color: #92400e;
}

.key-shift {
  background: linear-gradient(145deg, #fef3c7 0%, #fde68a 100%);
  border-color: rgba(251, 191, 36, 0.3);
  color: #92400e;
}

.key-shift:hover {
  background: linear-gradient(145deg, #fde68a 0%, #fcd34d 100%);
}

.key-modifier {
  background: linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%);
  border-color: rgba(199, 210, 254, 0.3);
  color: #3730a3;
  font-size: 0.8rem;
}

.key-caps {
  background: linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%);
  border-color: rgba(199, 210, 254, 0.3);
  color: #3730a3;
}

.key-ctrl {
  background: linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%);
  border-color: rgba(199, 210, 254, 0.3);
  color: #3730a3;
}

.key-alt {
  background: linear-gradient(145deg, #e0e7ff 0%, #c7d2fe 100%);
  border-color: rgba(199, 210, 254, 0.3);
  color: #3730a3;
}

.key-active {
  background: linear-gradient(145deg, #10b981 0%, #059669 100%) !important;
  border-color: rgba(16, 185, 129, 0.5) !important;
  color: white !important;
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.key-wide {
  max-width: 100px;
  flex: 1.5;
}

.key-space {
  flex: 4;
  max-width: none;
  background: linear-gradient(145deg, #f3f4f6 0%, #e5e7eb 100%);
}

.key-space:hover {
  background: linear-gradient(145deg, #e5e7eb 0%, #d1d5db 100%);
}

.key-tab {
  max-width: 80px;
  flex: 1.5;
}

.key-enter {
  max-width: 100px;
  flex: 1.5;
  background: linear-gradient(145deg, #10b981 0%, #059669 100%);
  color: white;
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
}

.key-enter:hover {
  background: linear-gradient(145deg, #059669 0%, #047857 100%);
  box-shadow: 0 6px 12px rgba(16, 185, 129, 0.4);
}
</style>
