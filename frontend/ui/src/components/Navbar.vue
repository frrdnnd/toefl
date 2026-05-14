<template>
  <header class="sticky top-0 z-20 glass border-b border-blue-100/60 px-6 py-3.5 flex items-center justify-between gap-4">
    <!-- Left: hamburger + title -->
    <div class="flex items-center gap-4">
      <button
        class="lg:hidden p-2 rounded-lg hover:bg-blue-50 transition-colors"
        @click="$emit('toggle-sidebar')"
      >
        <Menu class="w-5 h-5 text-slate-600" />
      </button>
      <div>
        <h2 class="font-display font-bold text-slate-800 text-base leading-tight">{{ pageTitle }}</h2>
        <p class="text-xs text-slate-400">{{ pageSubtitle }}</p>
      </div>
    </div>

    <!-- Center: search -->
    <div class="hidden md:flex flex-1 max-w-xs items-center gap-2 bg-slate-50 border border-blue-100 rounded-xl px-3 py-2 focus-within:ring-2 focus-within:ring-blue-200 focus-within:border-blue-300 transition-all">
      <Search class="w-4 h-4 text-slate-400 flex-shrink-0" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search questions..."
        class="flex-1 bg-transparent text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none"
      />
    </div>

    <!-- Right: actions -->
    <div class="flex items-center gap-2">
      <!-- AI Status -->
      <div class="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-100">
        <div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
        <span class="text-xs font-semibold text-emerald-600">AI Online</span>
      </div>

      <!-- Notifications -->
      <button class="relative p-2 rounded-xl hover:bg-blue-50 transition-colors">
        <Bell class="w-5 h-5 text-slate-500" />
        <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-blue-500 border border-white" />
      </button>

      <!-- Avatar -->
      <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-white text-xs font-bold shadow-sm cursor-pointer hover:scale-105 transition-transform">
        U
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { Menu, Search, Bell } from 'lucide-vue-next'

defineEmits(['toggle-sidebar'])

const route = useRoute()
const searchQuery = ref('')

const pages = {
  '/': { title: 'Dashboard', subtitle: 'Your learning overview' },
  '/practice': { title: 'Practice', subtitle: 'AI-powered question generator' },
  '/history': { title: 'History', subtitle: 'Your past practice sessions' }
}

const pageTitle = computed(() => pages[route.path]?.title ?? 'SmartTOEFL AI')
const pageSubtitle = computed(() => pages[route.path]?.subtitle ?? '')
</script>