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
            Generate adaptive TOEFL questions powered by SMARTTOEFL AI.
          </p>
        </div>

        <button
          @click="generateQuestion"
          :disabled="store.loading"
          class="px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-bold shadow-lg hover:scale-105 transition-all"
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
          <div class="flex flex-wrap gap-4">
            <button
              v-for="item in difficulties"
              :key="item"
              @click="selectedDifficulty = item"
              class="px-6 py-4 rounded-2xl border transition-all duration-300 font-semibold"
              :class="selectedDifficulty === item
                ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent shadow-lg'
                : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'"
            >
              {{ item }}
            </button>
          </div>
        </div>

      </div>

      <!-- Evaluation Result -->
      <div
        v-if="evaluationResult"
        class="bg-white rounded-3xl border p-6 shadow-sm"
        :class="evaluationResult.is_correct
          ? 'border-green-200 bg-green-50'
          : 'border-red-200 bg-red-50'"
      >
        <div class="flex items-center gap-3 mb-4">
          <span
            class="text-sm font-bold px-3 py-1 rounded-full"
            :class="evaluationResult.is_correct
              ? 'bg-green-100 text-green-700'
              : 'bg-red-100 text-red-700'"
          >
            {{ evaluationResult.is_correct ? '✓ Correct!' : '✗ Wrong' }}
          </span>
        </div>
        <p class="text-slate-700 mb-2"><span class="font-semibold">Analysis:</span> {{ evaluationResult.analysis }}</p>
        <p class="text-slate-700 mb-2"><span class="font-semibold">Grammar tip:</span> {{ evaluationResult.grammar_tip }}</p>
        <p class="text-slate-700"><span class="font-semibold">Improvement:</span> {{ evaluationResult.improvement }}</p>
      </div>

      <!-- Question Card -->
      <QuestionCard
        v-if="store.currentQuestion"
        :question="store.currentQuestion"
        @submit-answer="submitAnswer"
      />

      <!-- Empty State -->
      <div
        v-else
        class="bg-white border border-dashed border-blue-200 rounded-3xl p-20 text-center"
      >
        <div class="text-6xl mb-6">🤖</div>
        <h2 class="text-3xl font-bold text-slate-800">Start TOEFL Practice</h2>
        <p class="text-slate-500 mt-4 max-w-xl mx-auto leading-relaxed">
          Select category and difficulty, then generate adaptive TOEFL questions powered by AI.
        </p>
      </div>

    </div>
  </MainLayout>
</template>

<script setup>
import { ref } from 'vue'
import MainLayout from '@/layouts/MainLayout.vue'
import QuestionCard from '@/components/QuestionCard.vue'
import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

const categories = ['Grammar', 'Vocabulary', 'Reading']
const difficulties = ['Easy', 'Intermediate', 'Advanced']

const selectedCategory = ref('Grammar')
const selectedDifficulty = ref('Easy')
const evaluationResult = ref(null)

const generateQuestion = async () => {
  evaluationResult.value = null
  try {
    await store.generateQuestion(
      selectedCategory.value,
      selectedDifficulty.value
    )
  } catch (error) {
    console.error(error)
  }
}

// answer = "A" / "B" / "C" / "D" — dikirim dari QuestionCard
const submitAnswer = async (answer) => {
  if (!store.currentQuestion) return
  evaluationResult.value = null

  const result = await store.evaluateAnswer({
    question: store.currentQuestion.question,
    user_answer: answer,
    correct_answer: store.currentQuestion.answer,
    category: selectedCategory.value,
    difficulty: selectedDifficulty.value
  })

  if (result) {
    evaluationResult.value = result
  }
}
</script>