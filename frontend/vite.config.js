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
    port: 10014,
    allowedHosts: ['tools.slamkun.top', '.slamkun.top'],
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
  }
})
