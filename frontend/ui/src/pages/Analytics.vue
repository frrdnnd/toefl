<template>
  <MainLayout>
    <div class="space-y-8">

      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold text-slate-800">
          Learning Analytics
        </h1>

        <p class="text-slate-500 mt-2">
          Detailed TOEFL skill performance, accuracy breakdown, and learning focus.
        </p>
      </div>

      <!-- Top Summary -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">

        <!-- Performance Circle -->
        <div
          class="bg-gradient-to-br from-blue-600 to-cyan-400 rounded-3xl p-8 text-white shadow-lg"
        >
          <h2 class="text-2xl font-bold">
            Overall Performance
          </h2>

          <p class="text-white/80 mt-2">
            Your current TOEFL practice accuracy.
          </p>

          <div class="flex justify-center mt-8">
            <div
              class="w-44 h-44 rounded-full border-8 border-white/30 flex items-center justify-center"
            >
              <div class="text-center">
                <p class="text-5xl font-bold">
                  {{ store.analytics?.accuracy || 0 }}%
                </p>

                <p class="text-white/80 mt-1">
                  Accuracy
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Question Distribution -->
        <div
          class="xl:col-span-2 bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
        >
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-2xl font-bold text-slate-800">
                Practice Summary
              </h2>

              <p class="text-slate-500 mt-1">
                Your total practice result overview.
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div class="bg-slate-50 rounded-2xl p-5 border border-slate-100">
              <p class="text-sm text-slate-500">
                Total Questions
              </p>

              <h3 class="text-4xl font-bold text-slate-800 mt-3">
                {{ store.analytics?.total_questions || 0 }}
              </h3>
            </div>

            <div class="bg-green-50 rounded-2xl p-5 border border-green-100">
              <p class="text-sm text-slate-500">
                Correct Answers
              </p>

              <h3 class="text-4xl font-bold text-green-600 mt-3">
                {{ store.analytics?.correct_answers || 0 }}
              </h3>
            </div>

            <div class="bg-red-50 rounded-2xl p-5 border border-red-100">
              <p class="text-sm text-slate-500">
                Wrong Answers
              </p>

              <h3 class="text-4xl font-bold text-red-500 mt-3">
                {{ store.analytics?.wrong_answers || 0 }}
              </h3>
            </div>
          </div>

          <div class="mt-8">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-slate-500">
                Correct vs Wrong Ratio
              </span>

              <span class="font-semibold text-slate-700">
                {{ store.analytics?.correct_answers || 0 }}
                /
                {{ store.analytics?.wrong_answers || 0 }}
              </span>
            </div>

            <div class="h-4 bg-slate-100 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-green-400 to-blue-500 rounded-full"
                :style="{ width: `${store.analytics?.accuracy || 0}%` }"
              ></div>
            </div>
          </div>
        </div>

      </div>

      <!-- Skill Breakdown -->
      <div
        class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
      >
        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-2xl font-bold text-slate-800">
              Skill Breakdown
            </h2>

            <p class="text-slate-500 mt-1">
              Analyze which TOEFL areas need more attention.
            </p>
          </div>

          <div class="hidden md:block text-right">
            <p class="text-sm text-slate-500">
              Weakest Area
            </p>

            <h3 class="text-xl font-bold text-blue-600">
              {{ weakestSkill }}
            </h3>
          </div>
        </div>

        <div class="space-y-6">
          <div
            v-for="skill in skillBreakdown"
            :key="skill.name"
            class="bg-slate-50 border border-slate-100 rounded-2xl p-5"
          >
            <div class="flex items-center justify-between mb-3">
              <div>
                <h3 class="font-bold text-slate-800">
                  {{ skill.name }}
                </h3>

                <p class="text-sm text-slate-500">
                  {{ skill.description }}
                </p>
              </div>

              <span class="text-lg font-bold text-blue-600">
                {{ skill.value }}%
              </span>
            </div>

            <div class="h-3 bg-white rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                :style="{ width: `${skill.value}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Insight -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">

        <!-- AI Recommendation -->
        <div
          class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
        >
          <h2 class="text-2xl font-bold text-slate-800">
            AI Learning Recommendation
          </h2>

          <p class="text-slate-500 mt-2">
            Personalized next step based on your current practice history.
          </p>

          <div
            class="mt-6 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white p-6"
          >
            <p class="text-lg leading-relaxed">
              {{
                store.recommendation?.recommendation ||
                'Practice more TOEFL questions to unlock personalized AI recommendations.'
              }}
            </p>
          </div>
        </div>

        <!-- Study Plan -->
        <div
          class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm"
        >
          <h2 class="text-2xl font-bold text-slate-800">
            Suggested Study Plan
          </h2>

          <p class="text-slate-500 mt-2">
            Recommended focus for your next practice session.
          </p>

          <div class="mt-6 space-y-4">
            <div class="flex items-center justify-between bg-slate-50 rounded-2xl p-4">
              <span class="text-slate-600">
                Focus Category
              </span>

              <span class="font-bold text-blue-600">
                {{ weakestSkill }}
              </span>
            </div>

            <div class="flex items-center justify-between bg-slate-50 rounded-2xl p-4">
              <span class="text-slate-600">
                Suggested Difficulty
              </span>

              <span class="font-bold text-blue-600">
                {{
                  store.recommendation?.suggested_difficulty ||
                  store.analytics?.suggested_difficulty ||
                  'Easy'
                }}
              </span>
            </div>

            <div class="flex items-center justify-between bg-slate-50 rounded-2xl p-4">
              <span class="text-slate-600">
                Learning Mode
              </span>

              <span class="font-bold text-cyan-600">
                Smart RAG
              </span>
            </div>
          </div>
        </div>

      </div>

    </div>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

onMounted(async () => {
  await store.fetchDashboard()
})

const skillBreakdown = computed(() => {
  const weakness = store.weakness || {}

  return [
    {
      name: 'Grammar',
      value: weakness.grammar || 0,
      description: 'Tenses, sentence structure, clauses, and subject-verb agreement.'
    },
    {
      name: 'Vocabulary',
      value: weakness.vocabulary || 0,
      description: 'Meaning, synonyms, antonyms, and word usage in context.'
    },
    {
      name: 'Reading',
      value: weakness.reading || 0,
      description: 'Main idea, inference, detail questions, and passage comprehension.'
    }
  ]
})

const weakestSkill = computed(() => {
  const sorted = [...skillBreakdown.value].sort(
    (a, b) => a.value - b.value
  )

  return sorted[0]?.name || 'Grammar'
})
</script>