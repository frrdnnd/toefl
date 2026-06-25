<template>
  <MainLayout>
    <div class="space-y-8">

      <!-- Header -->
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        <div>
          <h1 class="text-4xl font-extrabold text-slate-800">
            TOEFL AI Practice
          </h1>
          <p class="text-slate-500 mt-2">
            Generate academic, TOEFL ITP-style questions powered by SMARTTOEFL AI.
          </p>
        </div>

        <button
          @click="generateQuestion"
          :disabled="store.loading"
          class="px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-bold shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50"
        >
          <span v-if="store.loading">Generating...</span>
          <span v-else>Generate Question</span>
        </button>
      </div>

      <!-- Controls -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Category -->
        <div class="bg-white rounded-3xl border border-blue-100 p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 mb-5">Select Category</h3>
          <div class="flex flex-wrap gap-4">
            <button
              v-for="item in categories"
              :key="item"
              @click="selectedCategory = item"
              class="px-6 py-4 rounded-2xl border transition-all duration-300 font-semibold"
              :class="selectedCategory === item
                ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent shadow-lg'
                : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'"
            >
              {{ item }}
            </button>
          </div>
        </div>

        <!-- Difficulty -->
        <div class="bg-white rounded-3xl border border-blue-100 p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 mb-5">Select Difficulty</h3>
          <div class="grid sm:grid-cols-3 gap-3">
            <button
              v-for="item in difficulties"
              :key="item.value"
              @click="selectedDifficulty = item.value"
              class="px-4 py-3 rounded-2xl border text-left transition-all duration-300"
              :class="selectedDifficulty === item.value
                ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent shadow-lg'
                : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'"
            >
              <span class="block font-bold">{{ item.label }}</span>
              <span
                class="block text-xs mt-1"
                :class="selectedDifficulty === item.value ? 'text-white/90' : 'text-slate-400'"
              >
                {{ item.range }}
              </span>
            </button>
          </div>
        </div>

      </div>

      <!-- Mode -->
      <div class="bg-white rounded-3xl border border-blue-100 p-6 shadow-sm">
        <h3 class="font-bold text-slate-800 mb-5">Question Mode</h3>
        <div class="grid md:grid-cols-3 gap-3">
          <button
            v-for="item in modes"
            :key="item.value"
            @click="selectedMode = item.value"
            class="px-4 py-3 rounded-2xl border text-left transition-all duration-300"
            :class="selectedMode === item.value
              ? 'bg-gradient-to-r from-indigo-500 to-blue-500 text-white border-transparent shadow-lg'
              : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'"
          >
            <span class="block font-bold">{{ item.label }}</span>
            <span
              class="block text-xs mt-1"
              :class="selectedMode === item.value ? 'text-white/90' : 'text-slate-400'"
            >
              {{ item.desc }}
            </span>
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div
        v-if="store.loading"
        class="bg-white rounded-3xl border border-blue-100 p-12 text-center shadow-sm"
      >
        <div class="inline-block w-10 h-10 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
        <p class="text-slate-500 mt-4">Preparing your TOEFL question...</p>
      </div>

      <!-- Evaluation Result (Grammar / Vocabulary) -->
      <div
        v-if="evaluationResult && !isReading"
        class="bg-white rounded-3xl border p-6 shadow-sm space-y-5"
        :class="evaluationResult.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'"
      >
        <div class="flex items-center gap-3 flex-wrap">
          <span
            class="text-sm font-bold px-4 py-2 rounded-full"
            :class="evaluationResult.is_correct ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
          >
            {{ evaluationResult.is_correct ? '✓ Correct Answer' : '✗ Incorrect Answer' }}
          </span>
          <span
            v-if="evaluationResult.topic"
            class="text-xs font-semibold px-3 py-1 rounded-full bg-slate-100 text-slate-600 capitalize"
          >
            Topic: {{ evaluationResult.topic }}
          </span>
        </div>

        <!-- Correct Answer -->
        <div class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">✅ Correct Answer</h3>
          <p class="text-slate-700">
            {{ evaluationResult.correct_answer_text || evaluationResult.correct_answer }}
          </p>
        </div>

        <!-- Translation -->
        <div v-if="evaluationResult.translation" class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">🇮🇩 Translation</h3>
          <p class="text-slate-700 leading-relaxed">{{ evaluationResult.translation }}</p>
        </div>

        <!-- Explanation -->
        <div class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">📘 Explanation</h3>
          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.explanation }}</p>
          </div>
          <div v-if="evaluationResult.explanation_id">
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.explanation_id }}</p>
          </div>
        </div>

        <!-- Why Wrong -->
        <div
          v-if="!evaluationResult.is_correct && evaluationResult.why_wrong"
          class="bg-white rounded-2xl p-4 border border-red-100"
        >
          <h3 class="font-bold text-red-700 mb-2">❌ Why Your Answer Is Wrong</h3>
          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.why_wrong }}</p>
          </div>
          <div v-if="evaluationResult.why_wrong_id">
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.why_wrong_id }}</p>
          </div>
        </div>

        <!-- Weakness Recommendation -->
        <div
          v-if="!evaluationResult.is_correct && evaluationResult.recommendation"
          class="bg-white rounded-2xl p-4 border border-amber-100"
        >
          <h3 class="font-bold text-amber-700 mb-2">🎯 Weakness Recommendation</h3>
          <p class="text-slate-700 leading-relaxed">{{ evaluationResult.recommendation }}</p>
        </div>

        <!-- Grammar Tip -->
        <div v-if="evaluationResult.grammar_tip" class="bg-white rounded-2xl p-4 border border-blue-100">
          <h3 class="font-bold text-blue-700 mb-2">💡 Grammar Tip</h3>
          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.grammar_tip }}</p>
          </div>
          <div v-if="evaluationResult.grammar_tip_id">
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.grammar_tip_id }}</p>
          </div>
        </div>

        <!-- TOEFL Tip -->
        <div v-if="evaluationResult.toefl_tip" class="bg-white rounded-2xl p-4 border border-cyan-100">
          <h3 class="font-bold text-cyan-700 mb-2">🎯 TOEFL Strategy Tip</h3>
          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.toefl_tip }}</p>
          </div>
          <div v-if="evaluationResult.toefl_tip_id">
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">{{ evaluationResult.toefl_tip_id }}</p>
          </div>
        </div>
      </div>

      <!-- Reading -->
      <ReadingCard
        v-if="store.currentQuestion && isReading"
        :question="store.currentQuestion"
        :source="store.source"
        :results="readingResults"
        :loading="readingLoading"
        @submit-reading="submitReading"
      />

      <!-- Grammar / Vocabulary card -->
      <QuestionCard
        v-else-if="store.currentQuestion && !store.loading"
        :question="store.currentQuestion"
        :source="store.source"
        @submit-answer="submitAnswer"
      />

      <!-- Empty State -->
      <div
        v-else-if="!store.currentQuestion && !store.loading"
        class="bg-white border border-dashed border-blue-200 rounded-3xl p-20 text-center overflow-hidden relative"
      >
        <div class="absolute inset-0 pointer-events-none">
          <div class="absolute w-72 h-72 bg-cyan-200/30 blur-3xl rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <div class="relative z-10 mb-4 flex justify-center">
          <AIAnimation />
        </div>
        <h2 class="text-3xl font-bold text-slate-800 relative z-10">Start TOEFL Practice</h2>
        <p class="text-slate-500 mt-4 max-w-xl mx-auto leading-relaxed relative z-10">
          Select a category, difficulty, and mode, then generate academic
          TOEFL ITP-style questions powered by AI.
        </p>
      </div>

    </div>
  </MainLayout>
</template>

<script setup>
import { ref, computed } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'
import QuestionCard from '@/components/QuestionCard.vue'
import ReadingCard from '@/components/ReadingCard.vue'
import AIAnimation from '@/components/AIAnimation.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

const categories = ['Grammar', 'Vocabulary', 'Reading']

const difficulties = [
  { value: 'Easy', label: 'Easy', range: 'TOEFL ITP 400–450' },
  { value: 'Intermediate', label: 'Intermediate', range: 'TOEFL ITP 450–520' },
  { value: 'Advanced', label: 'Advanced', range: 'TOEFL ITP 550–650' }
]

const modes = [
  { value: 'dataset', label: 'Dataset', desc: 'Curated TOEFL question bank' },
  { value: 'ai', label: 'AI Generate', desc: 'Fresh questions from the LLM' },
  { value: 'hybrid', label: 'Hybrid', desc: 'Dataset seed + AI variation' }
]

const selectedCategory = ref('Grammar')
const selectedDifficulty = ref('Easy')
const selectedMode = ref('dataset')

const evaluationResult = ref(null)
const readingResults = ref({})
const readingLoading = ref(false)

const isReading = computed(() => store.currentQuestion?.section === 'reading')

const generateQuestion = async () => {
  evaluationResult.value = null
  readingResults.value = {}
  await store.generateQuestion(
    selectedCategory.value,
    selectedDifficulty.value,
    selectedMode.value
  )
}

const submitAnswer = async (letter) => {
  const q = store.currentQuestion
  if (!q) return

  evaluationResult.value = null

  const result = await store.checkAnswer({
    question_id: q.id,
    selected_answer: letter,
    correct_answer: q.answer,
    category: selectedCategory.value,
    difficulty: selectedDifficulty.value,
    topic: q.topic,
    question: q.question,
    options: q.options,
    explanation: q.explanation,
    bilingual: true
  })

  evaluationResult.value = result
  await store.refreshProgress()
}

const submitReading = async (items) => {
  readingLoading.value = true

  const entries = await Promise.all(
    items.map(async (item) => {
      const result = await store.checkAnswer({
        question_id: item.id,
        selected_answer: item.selected,
        correct_answer: item.answer,
        category: selectedCategory.value,
        difficulty: selectedDifficulty.value,
        topic: item.type,
        question: item.question,
        options: item.options,
        explanation: item.explanation,
        bilingual: false
      })
      return [item.id, result || { is_correct: item.selected === item.answer }]
    })
  )

  readingResults.value = Object.fromEntries(entries)
  readingLoading.value = false
  await store.refreshProgress()
}
</script>
