import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    host: '0.0.0.0',
    port: 20016,
    allowedHosts: ['tools.slamkun.top', '.slamkun.top', '47.86.215.76', 'localhost', '127.0.0.1'],
    proxy: {
      '/api': {
        target: 'http://localhost:10016',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:10016',
        ws: true,
        changeOrigin: true
      },
      '/static': {
        target: 'http://localhost:10016',
        changeOrigin: true
      }
    }
  },
  build: {
    // 构建产物直接输出到 Python 包目录,wheel 天然包含前端静态资源
    outDir: '../tmux_ai_coder_panel/frontend_dist',
    emptyOutDir: true,
  }
})
