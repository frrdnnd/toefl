<script setup>
import {
  LayoutDashboard,
  BookOpen,
  History,
  BarChart3,
  Settings
} from 'lucide-vue-next'

const menus = [
  {
    name: 'Practice',
    icon: BookOpen,
    path: '/'
  },
  {
    name: 'Dashboard',
    icon: LayoutDashboard,
    path: '/Dashboard'
  },
  {
    name: 'History',
    icon: History,
    path: '/history'
  },
  {
    name: 'Analytics',
    icon: BarChart3,
    path: '/analytics'
  },
  {
    name: 'Settings',
    icon: Settings,
    path: '/settings'
  }
]
</script>

<template>
  <aside
    class="w-72 h-screen bg-white border-r border-blue-100 fixed left-0 top-0 p-6 flex flex-col"
  >

    <!-- Logo -->
    <div class="mb-10">

      <h1 class="text-2xl font-bold text-blue-600">
        SMARTTOEFL AI
      </h1>

      <p class="text-sm text-slate-500 mt-1">
        AI TOEFL Platform
      </p>

    </div>

    <!-- Navigation -->
    <nav class="space-y-3 flex-1">

      <RouterLink
        v-for="menu in menus"
        :key="menu.name"
        :to="menu.path"
        class="flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300 text-slate-600 hover:bg-blue-50 hover:text-blue-600"
        active-class="bg-gradient-to-r from-blue-500 to-cyan-400 text-white shadow-lg"
      >

        <component
          :is="menu.icon"
          class="w-5 h-5"
        />

        <span class="font-medium">
          {{ menu.name }}
        </span>

      </RouterLink>

    </nav>

    <!-- Footer -->
    <div
      class="mt-auto bg-gradient-to-r from-blue-500 to-cyan-400 rounded-3xl p-5 text-white"
    >

      <h3 class="font-semibold">
        SMART AI Tutor
      </h3>

      <p class="text-sm mt-2 opacity-90 leading-relaxed">
        Adaptive TOEFL learning powered by AI + RAG.
      </p>

    </div>

  </aside>
</template>