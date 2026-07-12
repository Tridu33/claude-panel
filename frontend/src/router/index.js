import { createRouter, createWebHistory } from 'vue-router'
import ControlPanel from '../views/ControlPanel.vue'
import SSHTerminal from '../views/SSHTerminal.vue'
import Login from '../views/Login.vue'
import { checkAuth } from '../auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'ControlPanel',
    component: ControlPanel,
  },
  {
    path: '/ssh',
    name: 'SSHTerminal',
    component: SSHTerminal,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 全局守卫:未登录一律跳转 /login
router.beforeEach(async (to) => {
  // 公开路由直接放行
  if (to.meta.public) {
    // 已登录又访问 /login,则回首页
    if (to.name === 'Login') {
      const ok = await checkAuth()
      if (ok) return { name: 'ControlPanel' }
    }
    return true
  }
  // 受保护路由:校验会话
  const ok = await checkAuth()
  if (!ok) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
