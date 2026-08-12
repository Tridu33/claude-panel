<template>
  <div class="login-wrap">
    <form class="login-card" @submit.prevent="onSubmit">
      <div class="brand">
        <span class="logo">🎹</span>
        <h1>Claude Panel</h1>
      </div>
      <p class="subtitle">请输入账号密码登录</p>

      <div class="form-group">
        <label>账号</label>
        <input
          type="text"
          v-model="account"
          autocomplete="username"
          placeholder="账号"
          :disabled="loading"
          autofocus
        />
      </div>

      <div class="form-group">
        <label>密码</label>
        <input
          type="password"
          v-model="password"
          autocomplete="current-password"
          placeholder="密码"
          :disabled="loading"
        />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button class="login-btn" type="submit" :disabled="loading">
        {{ loading ? '登录中…' : '登 录' }}
      </button>
    </form>
  </div>
</template>

<script>
import { login } from '../auth'

export default {
  name: 'Login',
  data() {
    return {
      account: '',
      password: '',
      loading: false,
      error: '',
    }
  },
  methods: {
    async onSubmit() {
      this.error = ''
      this.loading = true
      try {
        const res = await login(this.account, this.password)
        if (res.ok) {
          // 登录成功,跳到目标路由或首页
          const redirect = this.$route.query.redirect || '/'
          this.$router.replace(redirect)
        } else {
          this.error = res.error || '登录失败'
        }
      } catch (e) {
        this.error = e.message && e.message.includes('后端')
          ? e.message + ' — 请确认 start.bat 已完整启动两个服务'
          : '网络错误,请重试'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}
.login-card {
  width: 100%;
  max-width: 380px;
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}
.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.6rem;
  margin-bottom: 0.25rem;
}
.logo {
  font-size: 2rem;
}
.brand h1 {
  margin: 0;
  color: #10b981;
  font-size: 1.6rem;
  font-weight: 700;
}
.subtitle {
  text-align: center;
  color: #94a3b8;
  margin: 0.5rem 0 1.75rem;
  font-size: 0.95rem;
}
.form-group {
  margin-bottom: 1.1rem;
}
.form-group label {
  display: block;
  color: #cbd5e1;
  font-size: 0.85rem;
  margin-bottom: 0.4rem;
}
.form-group input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.7rem 0.85rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus {
  border-color: #10b981;
}
.login-btn {
  width: 100%;
  padding: 0.8rem;
  margin-top: 0.5rem;
  background: #10b981;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.login-btn:hover:not(:disabled) {
  background: #059669;
}
.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #f87171;
  font-size: 0.85rem;
  margin: 0 0 0.75rem;
  text-align: center;
}
</style>
