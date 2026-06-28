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
    port: 10016,
    proxy: {
      '/api': {
        target: 'http://localhost:10015',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:10015',
        ws: true,
        changeOrigin: true
      },
      '/static': {
        target: 'http://localhost:10015',
        changeOrigin: true
      }
    }
  }
})
