import { createRouter, createWebHistory } from 'vue-router'
import ControlPanel from '../views/ControlPanel.vue'
import SSHTerminal from '../views/SSHTerminal.vue'

const routes = [
  {
    path: '/',
    name: 'ControlPanel',
    component: ControlPanel
  },
  {
    path: '/ssh',
    name: 'SSHTerminal',
    component: SSHTerminal
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
