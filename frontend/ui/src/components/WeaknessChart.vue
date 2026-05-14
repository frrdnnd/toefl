<template>
  <div class="bg-white border border-blue-100 rounded-3xl p-6 shadow-sm">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-xl font-bold text-slate-800">
          Weakness Analysis
        </h2>

        <p class="text-sm text-slate-500 mt-1">
          AI-powered adaptive learning insights.
        </p>
      </div>
    </div>

    <div class="space-y-5">
      <div v-for="item in weaknessItems" :key="item.label">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-slate-700">
            {{ item.label }}
          </span>

          <span class="text-sm font-semibold text-slate-800">
            {{ item.value }}%
          </span>
        </div>

        <div class="w-full h-3 rounded-full bg-slate-100 overflow-hidden">
          <div
            class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
            :style="{ width: `${item.value}%` }"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  weakness: Object
})

const weaknessItems = computed(() => [
  {
    label: 'Grammar',
    value: props.weakness?.grammar || 0
  },
  {
    label: 'Vocabulary',
    value: props.weakness?.vocabulary || 0
  },
  {
    label: 'Reading',
    value: props.weakness?.reading || 0
  }
])
</script>