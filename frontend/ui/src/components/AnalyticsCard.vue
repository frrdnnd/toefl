<template>
  <div class="card p-5 animate-slide-up cursor-default group" :style="{ animationDelay: `${delay}ms` }">
    <div class="flex items-start justify-between mb-4">
      <div :class="['w-11 h-11 rounded-xl flex items-center justify-center shadow-sm', bgClass]">
        <component :is="iconComponent" class="w-5 h-5" :class="iconColor" />
      </div>
      <span class="text-xs font-semibold px-2.5 py-1 rounded-full" :class="badgeClass">
        {{ badge }}
      </span>
    </div>
    <div class="space-y-0.5">
      <p class="text-2xl font-display font-bold text-slate-800">{{ value }}</p>
      <p class="text-sm text-slate-500">{{ title }}</p>
    </div>
    <!-- Subtle bottom line accent -->
    <div class="mt-4 h-1 w-full rounded-full bg-slate-100 overflow-hidden">
      <div
        class="h-full rounded-full bg-gradient-to-r transition-all duration-1000"
        :class="gradient"
        :style="{ width: progressWidth }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  BookOpen, CheckCircle, XCircle, Target, TrendingUp
} from 'lucide-vue-next'

const props = defineProps({
  title:     { type: String, required: true },
  value:     { type: [String, Number], required: true },
  icon:      { type: String, default: 'BookOpen' },
  gradient:  { type: String, default: 'from-blue-400 to-blue-600' },
  bg:        { type: String, default: 'bg-blue-50' },
  iconColor: { type: String, default: 'text-blue-600' },
  badge:     { type: String, default: '' },
  badgeClass:{ type: String, default: 'bg-blue-50 text-blue-600' },
  progress:  { type: Number, default: 100 },
  delay:     { type: Number, default: 0 }
})

const icons = { BookOpen, CheckCircle, XCircle, Target, TrendingUp }
const iconComponent = computed(() => icons[props.icon] || BookOpen)
const bgClass = computed(() => props.bg)
const progressWidth = computed(() => `${Math.min(100, props.progress)}%`)
</script>