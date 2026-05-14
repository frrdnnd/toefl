<template>
  <MainLayout>

    <div class="space-y-8">

      <!-- Header -->
      <div>

        <h1 class="text-4xl font-extrabold tracking-tight text-slate-800">
          SMARTTOEFL AI Dashboard
        </h1>

        <p class="text-slate-500 mt-2 text-lg">
          Adaptive TOEFL analytics and AI recommendation overview.
        </p>

      </div>

      <!-- Analytics Cards -->
      <div
        class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6"
      >

        <AnalyticsCard
          title="Total Questions"
          :value="store.analytics?.total_questions || 0"
          subtitle="Practice sessions completed"
        />

        <AnalyticsCard
          title="Correct Answers"
          :value="store.analytics?.correct_answers || 0"
          subtitle="Successfully answered"
        />

        <AnalyticsCard
          title="Wrong Answers"
          :value="store.analytics?.wrong_answers || 0"
          subtitle="Need improvement"
        />

        <AnalyticsCard
          title="Accuracy"
          :value="`${store.analytics?.accuracy || 0}%`"
          subtitle="Current learning accuracy"
        />

      </div>

      <!-- Main Dashboard -->
      <div
        class="grid grid-cols-1 xl:grid-cols-3 gap-8"
      >

        <!-- Weakness Analysis -->
        <div
          class="xl:col-span-2 bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
        >

          <div
            class="flex items-center gap-3 mb-8"
          >

            <div
              class="w-2 h-8 rounded-full bg-gradient-to-b from-blue-500 to-cyan-400"
            />

            <h2
              class="text-3xl font-bold text-slate-800"
            >
              Weakness Analysis
            </h2>

          </div>

          <div
            class="space-y-8"
          >

            <!-- Grammar -->
            <div>

              <div
                class="flex justify-between mb-3"
              >

                <span
                  class="font-semibold text-slate-700"
                >
                  Grammar
                </span>

                <span
                  class="font-bold text-blue-600"
                >
                  {{ store.weakness?.grammar || 0 }}%
                </span>

              </div>

              <div
                class="w-full h-4 rounded-full bg-slate-100 overflow-hidden"
              >

                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
                  :style="{
                    width: `${store.weakness?.grammar || 0}%`
                  }"
                />

              </div>

            </div>

            <!-- Vocabulary -->
            <div>

              <div
                class="flex justify-between mb-3"
              >

                <span
                  class="font-semibold text-slate-700"
                >
                  Vocabulary
                </span>

                <span
                  class="font-bold text-blue-600"
                >
                  {{ store.weakness?.vocabulary || 0 }}%
                </span>

              </div>

              <div
                class="w-full h-4 rounded-full bg-slate-100 overflow-hidden"
              >

                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
                  :style="{
                    width: `${store.weakness?.vocabulary || 0}%`
                  }"
                />

              </div>

            </div>

            <!-- Reading -->
            <div>

              <div
                class="flex justify-between mb-3"
              >

                <span
                  class="font-semibold text-slate-700"
                >
                  Reading
                </span>

                <span
                  class="font-bold text-blue-600"
                >
                  {{ store.weakness?.reading || 0 }}%
                </span>

              </div>

              <div
                class="w-full h-4 rounded-full bg-slate-100 overflow-hidden"
              >

                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
                  :style="{
                    width: `${store.weakness?.reading || 0}%`
                  }"
                />

              </div>

            </div>

          </div>

        </div>

        <!-- Right Side -->
        <div
          class="space-y-6"
        >

          <!-- Progress -->
          <div
            class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
          >

            <h2
              class="text-2xl font-bold text-slate-800 mb-6"
            >
              Progress Summary
            </h2>

            <div
              class="mb-6"
            >

              <div
                class="flex justify-between mb-3"
              >

                <span
                  class="text-slate-600"
                >
                  Accuracy Progress
                </span>

                <span
                  class="font-bold text-blue-600"
                >
                  {{ store.analytics?.accuracy || 0 }}%
                </span>

              </div>

              <div
                class="w-full h-4 rounded-full bg-slate-100 overflow-hidden"
              >

                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-700"
                  :style="{
                    width: `${store.analytics?.accuracy || 0}%`
                  }"
                />

              </div>

            </div>

            <!-- Stats -->
            <div
              class="grid grid-cols-2 gap-4"
            >

              <div
                class="rounded-2xl bg-blue-50 border border-blue-100 p-5"
              >

                <p
                  class="text-xs uppercase tracking-wide text-blue-500 font-bold"
                >
                  Practice Level
                </p>

                <h3
                  class="text-2xl font-bold text-blue-700 mt-2"
                >
                  AI Adaptive
                </h3>

              </div>

              <div
                class="rounded-2xl bg-cyan-50 border border-cyan-100 p-5"
              >

                <p
                  class="text-xs uppercase tracking-wide text-cyan-500 font-bold"
                >
                  Learning Mode
                </p>

                <h3
                  class="text-2xl font-bold text-cyan-700 mt-2"
                >
                  Smart RAG
                </h3>

              </div>

            </div>

          </div>

          <!-- AI Insight -->
          <div
            class="rounded-3xl bg-gradient-to-r from-blue-500 to-indigo-600 p-8 text-white shadow-xl"
          >

            <h2
              class="text-3xl font-bold"
            >
              AI Learning Insight
            </h2>

            <p
              class="mt-4 text-blue-100 leading-relaxed"
            >

              {{
                store.recommendation?.recommendation ||
                'Analyzing your TOEFL learning pattern...'
              }}

            </p>

          </div>

        </div>

      </div>

      <!-- Recommendation -->
      <RecommendationCard
        :recommendation="store.recommendation"
      />

    </div>

  </MainLayout>
</template>

<script setup>
import { onMounted } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'

import AnalyticsCard from '@/components/AnalyticsCard.vue'

import RecommendationCard from '@/components/RecommendationCard.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

onMounted(async () => {

  await store.fetchDashboard()
})
</script>