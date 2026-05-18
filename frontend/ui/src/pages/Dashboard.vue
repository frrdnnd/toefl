<template>
  <MainLayout>
    <div class="space-y-8">

      <!-- Welcome Hero -->
      <div
        class="rounded-3xl bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 p-8 text-white shadow-xl"
      >
        <div class="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">
          <div>
            <p class="text-blue-100 font-semibold">
              Welcome back to
            </p>

            <h1 class="text-4xl font-extrabold tracking-tight mt-2">
              SMARTTOEFL AI Dashboard
            </h1>

            <p class="text-blue-100 mt-3 text-lg max-w-2xl">
              Track your TOEFL learning progress and continue your adaptive practice journey.
            </p>
          </div>

          <div class="bg-white/15 backdrop-blur rounded-3xl p-6 min-w-[220px]">
            <p class="text-blue-100 text-sm">
              Current Accuracy
            </p>

            <h2 class="text-5xl font-extrabold mt-2">
              {{ store.analytics?.accuracy || 0 }}%
            </h2>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div class="bg-white border border-blue-100 rounded-3xl p-6 shadow-sm">
          <p class="text-slate-500">
            Total Practice
          </p>

          <h3 class="text-4xl font-extrabold text-slate-800 mt-3">
            {{ store.analytics?.total_questions || 0 }}
          </h3>

          <p class="text-sm text-slate-400 mt-2">
            Questions completed
          </p>
        </div>

        <div class="bg-white border border-green-100 rounded-3xl p-6 shadow-sm">
          <p class="text-slate-500">
            Correct Answers
          </p>

          <h3 class="text-4xl font-extrabold text-green-600 mt-3">
            {{ store.analytics?.correct_answers || 0 }}
          </h3>

          <p class="text-sm text-slate-400 mt-2">
            Strong responses
          </p>
        </div>

        <div class="bg-white border border-red-100 rounded-3xl p-6 shadow-sm">
          <p class="text-slate-500">
            Wrong Answers
          </p>

          <h3 class="text-4xl font-extrabold text-red-500 mt-3">
            {{ store.analytics?.wrong_answers || 0 }}
          </h3>

          <p class="text-sm text-slate-400 mt-2">
            Need review
          </p>
        </div>

      </div>

      <!-- Dashboard Content -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">

        <!-- Next Practice Focus -->
        <div class="xl:col-span-2 bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">

          <div class="flex items-center justify-between mb-8">
            <div>
              <h2 class="text-2xl font-bold text-slate-800">
                Next Practice Focus
              </h2>

              <p class="text-slate-500 mt-1">
                Recommended area to improve based on your latest performance.
              </p>
            </div>

            <div class="hidden md:block text-right">
              <p class="text-sm text-slate-500">
                Focus Skill
              </p>

              <h3 class="text-2xl font-bold text-blue-600">
                {{ weakestSkill }}
              </h3>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
            <div
              v-for="skill in skillCards"
              :key="skill.name"
              class="rounded-2xl border border-slate-100 bg-slate-50 p-5"
            >
              <div class="flex items-center justify-between">
                <h3 class="font-bold text-slate-800">
                  {{ skill.name }}
                </h3>

                <span class="font-bold text-blue-600">
                  {{ skill.value }}%
                </span>
              </div>

              <div class="mt-4 h-3 rounded-full bg-white overflow-hidden">
                <div
                  class="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-400"
                  :style="{ width: `${skill.value}%` }"
                ></div>
              </div>

              <p class="text-sm text-slate-500 mt-4">
                {{ skill.label }}
              </p>
            </div>
          </div>

        </div>

        <!-- Continue Learning -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">

          <h2 class="text-2xl font-bold text-slate-800">
            Continue Learning
          </h2>

          <p class="text-slate-500 mt-2">
            Suggested next session.
          </p>

          <div class="mt-6 rounded-2xl bg-blue-50 border border-blue-100 p-5">
            <p class="text-sm uppercase tracking-wide font-bold text-blue-500">
              Difficulty
            </p>

            <h3 class="text-3xl font-extrabold text-blue-700 mt-2">
              {{
                store.recommendation?.suggested_difficulty ||
                store.analytics?.suggested_difficulty ||
                'Easy'
              }}
            </h3>
          </div>

          <RouterLink
            to="/practice"
            class="mt-6 block text-center rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 px-6 py-4 font-bold text-white shadow-lg hover:opacity-90 transition"
          >
            Start Practice
          </RouterLink>

        </div>

      </div>

      <!-- AI Insight -->
      <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
        <h2 class="text-2xl font-bold text-slate-800">
          AI Learning Insight
        </h2>

        <p class="text-slate-500 mt-2">
          A quick recommendation from your adaptive TOEFL tutor.
        </p>

        <div class="mt-6 rounded-2xl bg-gradient-to-r from-blue-500 to-indigo-600 p-6 text-white">
          <p class="text-lg leading-relaxed">
            {{
              store.recommendation?.recommendation ||
              'Complete more TOEFL practice questions to unlock personalized AI insight.'
            }}
          </p>
        </div>
      </div>

    </div>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

onMounted(async () => {
  await store.fetchDashboard()
})

const skillCards = computed(() => {
  const weakness = store.weakness || {}

  return [
    {
      name: 'Grammar',
      value: weakness.grammar || 0,
      label: 'Grammar accuracy'
    },
    {
      name: 'Vocabulary',
      value: weakness.vocabulary || 0,
      label: 'Word usage accuracy'
    },
    {
      name: 'Reading',
      value: weakness.reading || 0,
      label: 'Reading skill accuracy'
    }
  ]
})

const weakestSkill = computed(() => {
  const sorted = [...skillCards.value].sort(
    (a, b) => a.value - b.value
  )

  return sorted[0]?.name || 'Grammar'
})
</script>