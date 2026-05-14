<template>
  <MainLayout>

    <div class="max-w-4xl mx-auto space-y-8">

      <!-- Header -->
      <div>

        <h1 class="text-3xl font-bold text-slate-800">
          Settings
        </h1>

        <p class="text-slate-500 mt-2">
          Configure your SMARTTOEFL AI learning preferences.
        </p>

      </div>

      <!-- Settings Card -->
      <div
        class="bg-white border border-blue-100 rounded-3xl p-8 shadow-sm space-y-8"
      >

        <!-- TOEFL Target -->
        <div>

          <label class="block text-sm font-semibold text-slate-700 mb-3">
            Target TOEFL Score
          </label>

          <input
            v-model="targetScore"
            type="number"
            placeholder="100"
            class="w-full rounded-2xl border border-slate-200 px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />

        </div>

        <!-- Difficulty -->
        <div>

          <label class="block text-sm font-semibold text-slate-700 mb-3">
            Preferred Difficulty
          </label>

          <select
            v-model="difficulty"
            class="w-full rounded-2xl border border-slate-200 px-5 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <option>Easy</option>
            <option>Intermediate</option>
            <option>Advanced</option>
          </select>

        </div>

        <!-- AI Tutor -->
        <div
          class="flex items-center justify-between bg-slate-50 rounded-2xl p-5 border border-slate-100"
        >

          <div>

            <h3 class="font-semibold text-slate-800">
              AI Tutor Mode
            </h3>

            <p class="text-sm text-slate-500 mt-1">
              Enable adaptive AI conversational tutoring.
            </p>

          </div>

          <input
            v-model="aiTutor"
            type="checkbox"
            class="w-5 h-5"
          />

        </div>

        <!-- API -->
        <div
          class="flex items-center justify-between bg-slate-50 rounded-2xl p-5 border border-slate-100"
        >

          <div>

            <h3 class="font-semibold text-slate-800">
              Backend API
            </h3>

            <p class="text-sm text-slate-500 mt-1">
              FastAPI + Qwen2 + RAG system status.
            </p>

          </div>

          <span
            class="px-4 py-2 rounded-full bg-green-100 text-green-700 text-sm font-semibold"
          >
            Online
          </span>

        </div>

        <!-- Save -->
        <button
          @click="saveSettings"
          class="px-6 py-3 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-semibold shadow-md hover:shadow-xl transition-all duration-300"
        >
          Save Settings
        </button>

      </div>

    </div>

  </MainLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'

const targetScore = ref(100)
const difficulty = ref('Easy')
const aiTutor = ref(true)

onMounted(() => {

  const saved = localStorage.getItem(
    'smarttoefl-settings'
  )

  if (saved) {

    const parsed = JSON.parse(saved)

    targetScore.value = parsed.targetScore
    difficulty.value = parsed.difficulty
    aiTutor.value = parsed.aiTutor
  }
})

const saveSettings = () => {

  localStorage.setItem(
    'smarttoefl-settings',
    JSON.stringify({
      targetScore: targetScore.value,
      difficulty: difficulty.value,
      aiTutor: aiTutor.value
    })
  )

  alert('Settings saved successfully!')
}
</script>