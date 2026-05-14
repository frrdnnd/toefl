<template>
  <div class="flex flex-col items-center justify-center gap-3 py-8">
    <div class="relative w-12 h-12">
      <!-- Outer ring -->
      <div class="absolute inset-0 rounded-full border-4 border-blue-100"></div>
      <!-- Spinning ring -->
      <div class="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-500 animate-spin"
           style="filter: drop-shadow(0 0 8px rgba(59,130,246,0.6))"></div>
      <!-- Inner dot -->
      <div class="absolute inset-3 rounded-full bg-gradient-to-br from-blue-400 to-cyan-400 animate-pulse"></div>
    </div>
    <p v-if="text" class="text-sm text-slate-500 font-medium animate-pulse">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({
  text: { type: String, default: '' }
})
</script>