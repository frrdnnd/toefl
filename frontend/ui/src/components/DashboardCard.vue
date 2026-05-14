<template>
  <div class="card p-5 animate-slide-up" :style="{ animationDelay: `${delay}ms` }">
    <div class="flex items-center justify-between mb-5">
      <h3 class="font-display font-semibold text-slate-800">{{ title }}</h3>
      <slot name="header-right" />
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  delay: { type: Number, default: 0 }
})
</script>