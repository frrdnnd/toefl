<template>
  <div
    class="relative overflow-hidden rounded-3xl bg-gradient-to-r from-blue-500 to-indigo-600 p-8 text-white shadow-xl"
  >

    <div class="relative z-10">

      <div class="flex items-center justify-between">

        <div>

          <h2 class="text-2xl font-bold">
            AI Recommendation
          </h2>

          <p class="text-blue-100 mt-1">
            Personalized for you
          </p>

        </div>

        <div
          class="px-4 py-2 rounded-full bg-white/20 text-sm font-semibold"
        >
          Adaptive
        </div>

      </div>

      <div class="mt-6">

        <p class="text-lg leading-relaxed text-blue-50">

          {{
            recommendation?.recommendation ||
            'Loading your personalized recommendation...'
          }}

        </p>

      </div>

      <RouterLink
        to="/practice"
        class="inline-flex items-center gap-2 text-white font-semibold mt-6 hover:opacity-80 transition"
      >
        Start practicing now →
      </RouterLink>

    </div>

    <div
      class="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-white/10"
    />

  </div>
</template>

<script setup>
defineProps({
  recommendation: Object
})
</script>