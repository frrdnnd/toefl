<template>
  <div class="ai-animation">
    <Vue3Lottie
      :animationData="animationData"
      :height="220"
      :width="220"
    />
  </div>
</template>

<script setup>
import { Vue3Lottie } from 'vue3-lottie'

import animationData from '@/assets/animations/eve-bot.json'
</script>

<style scoped>
.ai-animation {
  display: flex;
  justify-content: center;
  align-items: center;

  animation: floating 4s ease-in-out infinite;

  filter:
    drop-shadow(0 0 20px rgba(59,130,246,0.25))
    drop-shadow(0 0 40px rgba(34,211,238,0.18));
}

@keyframes floating {
  0% {
    transform: translateY(0px);
  }

  50% {
    transform: translateY(-12px);
  }

  100% {
    transform: translateY(0px);
  }
}
</style>  