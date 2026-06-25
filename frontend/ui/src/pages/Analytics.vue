<template>
  <MainLayout>
    <div class="space-y-8">

      <!-- Header -->
      <div>
        <h1 class="text-3xl font-bold text-slate-800">Learning Analytics</h1>
        <p class="text-slate-500 mt-2">
          Detailed TOEFL skill performance, accuracy breakdown, and learning focus.
        </p>
      </div>

      <!-- Top Summary -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">

        <!-- Performance Circle -->
        <div class="bg-gradient-to-br from-blue-600 to-cyan-400 rounded-3xl p-8 text-white shadow-lg">
          <h2 class="text-2xl font-bold">Overall Performance</h2>
          <p class="text-white/80 mt-2">Your current TOEFL practice accuracy.</p>
          <div class="flex justify-center mt-8">
            <div class="w-44 h-44 rounded-full border-8 border-white/30 flex items-center justify-center">
              <div class="text-center">
                <p class="text-5xl font-bold">{{ store.analytics?.accuracy || 0 }}%</p>
                <p class="text-white/80 mt-1">Accuracy</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Estimated TOEFL Score -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm flex flex-col justify-between">
          <div>
            <h2 class="text-2xl font-bold text-slate-800">Estimated TOEFL ITP</h2>
            <p class="text-slate-500 mt-1">Projected from your overall accuracy.</p>
          </div>
          <div class="mt-6 text-center">
            <p class="text-6xl font-extrabold text-blue-600">
              {{ store.analytics?.estimated_toefl_score || '—' }}
            </p>
            <p class="text-slate-500 mt-2">
              Range {{ store.analytics?.estimated_toefl_range || 'N/A' }}
            </p>
          </div>
          <div class="mt-6 rounded-2xl bg-blue-50 border border-blue-100 p-4 text-center">
            <p class="text-xs uppercase tracking-wide font-bold text-blue-500">Learning Level</p>
            <p class="text-xl font-extrabold text-blue-700 mt-1">
              {{ store.analytics?.learning_level || 'Beginner' }}
            </p>
          </div>
        </div>

        <!-- Practice Summary -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
          <h2 class="text-2xl font-bold text-slate-800">Practice Summary</h2>
          <p class="text-slate-500 mt-1">Your total practice result overview.</p>

          <div class="grid grid-cols-3 gap-3 mt-6">
            <div class="bg-slate-50 rounded-2xl p-4 border border-slate-100">
              <p class="text-xs text-slate-500">Total</p>
              <h3 class="text-3xl font-bold text-slate-800 mt-2">
                {{ store.analytics?.total_questions || 0 }}
              </h3>
            </div>
            <div class="bg-green-50 rounded-2xl p-4 border border-green-100">
              <p class="text-xs text-slate-500">Correct</p>
              <h3 class="text-3xl font-bold text-green-600 mt-2">
                {{ store.analytics?.correct_answers || 0 }}
              </h3>
            </div>
            <div class="bg-red-50 rounded-2xl p-4 border border-red-100">
              <p class="text-xs text-slate-500">Wrong</p>
              <h3 class="text-3xl font-bold text-red-500 mt-2">
                {{ store.analytics?.wrong_answers || 0 }}
              </h3>
            </div>
          </div>

          <div class="mt-6">
            <div class="flex justify-between text-sm mb-2">
              <span class="text-slate-500">Correct vs Wrong</span>
              <span class="font-semibold text-slate-700">
                {{ store.analytics?.correct_answers || 0 }} / {{ store.analytics?.wrong_answers || 0 }}
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

      <!-- Accuracy Breakdowns -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">

        <!-- By Category -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-2xl font-bold text-slate-800">Accuracy by Category</h2>
              <p class="text-slate-500 mt-1">Grammar, Vocabulary, and Reading.</p>
            </div>
            <div class="hidden md:block text-right">
              <p class="text-sm text-slate-500">Weakest Area</p>
              <h3 class="text-xl font-bold text-blue-600 capitalize">{{ weakestSkill }}</h3>
            </div>
          </div>

          <div class="space-y-5">
            <div
              v-for="skill in categoryBreakdown"
              :key="skill.name"
              class="bg-slate-50 border border-slate-100 rounded-2xl p-5"
            >
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ skill.name }}</h3>
                  <p class="text-xs text-slate-400">
                    <span v-if="skill.total">{{ skill.correct }}/{{ skill.total }} benar</span>
                    <span v-else>Belum ada latihan</span>
                  </p>
                </div>
                <span
                  class="text-lg font-bold"
                  :class="skill.total ? 'text-blue-600' : 'text-slate-300'"
                >
                  {{ skill.total ? skill.value + '%' : '—' }}
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

        <!-- By Difficulty -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-slate-800">Accuracy by Difficulty</h2>
            <p class="text-slate-500 mt-1">Easy, Intermediate, and Advanced.</p>
          </div>

          <div class="space-y-5">
            <div
              v-for="level in difficultyBreakdown"
              :key="level.name"
              class="bg-slate-50 border border-slate-100 rounded-2xl p-5"
            >
              <div class="flex items-center justify-between mb-3">
                <div>
                  <h3 class="font-bold text-slate-800">{{ level.name }}</h3>
                  <p class="text-xs text-slate-400">
                    {{ level.range }}
                    <span v-if="level.total"> · {{ level.correct }}/{{ level.total }} benar</span>
                    <span v-else> · belum ada latihan</span>
                  </p>
                </div>
                <span
                  class="text-lg font-bold"
                  :class="level.total ? 'text-purple-600' : 'text-slate-300'"
                >
                  {{ level.total ? level.value + '%' : '—' }}
                </span>
              </div>
              <div class="h-3 bg-white rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                  :style="{ width: `${level.value}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- AI Tutor: Weakness + Recommendations -->
      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">

        <!-- Weakness Topics -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
          <h2 class="text-2xl font-bold text-slate-800">Weakness Topics</h2>
          <p class="text-slate-500 mt-2">Skills where you make the most mistakes.</p>

          <div v-if="weaknessTopics.length" class="mt-6 space-y-3">
            <div
              v-for="topic in weaknessTopics"
              :key="topic.topic"
              class="flex items-center justify-between bg-slate-50 rounded-2xl p-4 border border-slate-100"
            >
              <div>
                <p class="font-semibold text-slate-800 capitalize">{{ formatTopic(topic.topic) }}</p>
                <p class="text-xs text-slate-400 capitalize">{{ topic.category }}</p>
              </div>
              <span class="text-sm font-bold text-red-500">{{ topic.accuracy }}%</span>
            </div>
          </div>
          <p v-else class="mt-6 text-slate-400">
            No weak topics detected yet. Keep practicing to build your profile.
          </p>
        </div>

        <!-- AI Recommendation -->
        <div class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm">
          <h2 class="text-2xl font-bold text-slate-800">AI Tutor Recommendation</h2>
          <p class="text-slate-500 mt-2">Personalized next steps based on your history.</p>

          <div class="mt-6 space-y-3">
            <div
              v-for="(rec, index) in recommendations"
              :key="index"
              class="rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white p-5"
            >
              <p class="leading-relaxed">{{ rec }}</p>
            </div>
          </div>

          <div class="mt-6 flex items-center justify-between bg-slate-50 rounded-2xl p-4 border border-slate-100">
            <span class="text-slate-600">Suggested Difficulty</span>
            <span class="font-bold text-blue-600">
              {{ store.recommendation?.suggested_difficulty || store.analytics?.suggested_difficulty || 'Easy' }}
            </span>
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

const categoryBreakdown = computed(() => {
  const stats = store.analytics?.category_stats || {}
  return [
    { name: 'Grammar', key: 'grammar' },
    { name: 'Vocabulary', key: 'vocabulary' },
    { name: 'Reading', key: 'reading' }
  ].map(({ name, key }) => {
    const s = stats[key] || {}
    return { name, value: s.accuracy ?? 0, total: s.total ?? 0, correct: s.correct ?? 0 }
  })
})

const difficultyBreakdown = computed(() => {
  const stats = store.analytics?.difficulty_stats || {}
  return [
    { name: 'Easy', key: 'easy', range: 'TOEFL ITP 400–450' },
    { name: 'Intermediate', key: 'intermediate', range: 'TOEFL ITP 450–520' },
    { name: 'Advanced', key: 'advanced', range: 'TOEFL ITP 550–650' }
  ].map(({ name, key, range }) => {
    const s = stats[key] || {}
    return { name, range, value: s.accuracy ?? 0, total: s.total ?? 0, correct: s.correct ?? 0 }
  })
})

const weakestSkill = computed(() => {
  const practiced = categoryBreakdown.value.filter((s) => s.total > 0)
  if (!practiced.length) return '—'
  return [...practiced].sort((a, b) => a.value - b.value)[0].name
})

const weaknessTopics = computed(() =>
  store.analytics?.weakness_topics || store.weakness?.weak_topics || []
)

const recommendations = computed(() => {
  const recs = store.recommendation?.recommendations || store.weakness?.recommendations
  if (recs && recs.length) return recs
  return [
    store.recommendation?.recommendation ||
    'Practice more TOEFL questions to unlock personalized AI recommendations.'
  ]
})

const formatTopic = (topic) => (topic || '').replace(/_/g, ' ')
</script>
