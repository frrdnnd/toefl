<template>
  <MainLayout>

    <div class="max-w-6xl mx-auto space-y-8">

      <!-- Header -->
      <div
        class="flex items-center justify-between"
      >

        <div>

          <h1 class="text-3xl font-bold text-slate-800">
            Practice History
          </h1>

          <p class="text-slate-500 mt-2">
            Review your TOEFL learning journey and AI evaluations.
          </p>

        </div>

        <button
          @click="store.clearHistory"
          class="px-5 py-3 rounded-2xl bg-red-500 text-white font-semibold hover:bg-red-600 transition"
        >
          Clear History
        </button>

      </div>

      <!-- History List -->
      <div
        v-if="store.history.length"
        class="space-y-6"
      >

        <HistoryCard
          v-for="item in store.history"
          :key="item.id"
          :item="item"
        />

      </div>

      <!-- Empty -->
      <div
        v-else
        class="bg-white border border-dashed border-blue-200 rounded-3xl p-20 text-center"
      >

        <h2 class="text-2xl font-bold text-slate-700">
          No Practice History Yet
        </h2>

        <p class="text-slate-500 mt-3">
          Start practicing to generate your TOEFL learning analytics.
        </p>

      </div>

    </div>

  </MainLayout>
</template>

<script setup>
import { onMounted } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'

import HistoryCard from '@/components/HistoryCard.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

onMounted(async () => {

  await store.fetchHistory()
})
</script>