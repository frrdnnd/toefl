<template>
  <MainLayout>

    <div class="space-y-8">

      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold text-slate-800">
          Learning Analytics
        </h1>

        <p class="text-slate-500 mt-2">
          AI-powered TOEFL performance insights and adaptive learning analytics.
        </p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">

        <AnalyticsCard
          title="Total Questions"
          :value="store.analytics?.total_questions || 0"
        />

        <AnalyticsCard
          title="Correct Answers"
          :value="store.analytics?.correct_answers || 0"
        />

        <AnalyticsCard
          title="Wrong Answers"
          :value="store.analytics?.wrong_answers || 0"
        />

        <AnalyticsCard
          title="Accuracy"
          :value="`${store.analytics?.accuracy || 0}%`"
        />

      </div>

      <!-- Main Section -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">

        <!-- Weakness -->
        <div class="xl:col-span-2">

          <WeaknessChart
            :weakness="store.weakness"
          />

        </div>

        <!-- Recommendation -->
        <div
          class="bg-white border border-blue-100 rounded-3xl p-6 shadow-sm"
        >

          <h2 class="text-xl font-bold text-slate-800 mb-4">
            AI Recommendation
          </h2>

          <div
            class="rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white p-5"
          >

            <p class="leading-relaxed">
              {{
                store.recommendation?.recommendation
              }}
            </p>

          </div>

          <!-- Suggested Difficulty -->
          <div
            class="mt-6 bg-slate-50 rounded-2xl p-4 border border-slate-100"
          >

            <p class="text-sm text-slate-500">
              Suggested Difficulty
            </p>

            <h3 class="text-xl font-bold text-blue-600 mt-2">
              {{
                store.analytics?.suggested_difficulty
              }}
            </h3>

          </div>

        </div>

      </div>

    </div>

  </MainLayout>
</template>

<script setup>
import { onMounted } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'

import AnalyticsCard from '@/components/AnalyticsCard.vue'
import WeaknessChart from '@/components/WeaknessChart.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

onMounted(async () => {

  await store.fetchDashboard()

})
</script>