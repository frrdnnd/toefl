import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '@/pages/Dashboard.vue'
import Practice from '@/pages/Practice.vue'
import History from '@/pages/History.vue'
import Analytics from '@/pages/Analytics.vue'
import Settings from '@/pages/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Practice',
    component: Practice
  },

  {
    path: '/Dashboard',
    name: 'Dashboard',
    component: Dashboard
  },

  {
    path: '/history',
    name: 'History',
    component: History
  },

  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics
  },

  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router