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
          class="px-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-400 text-white font-bold shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-50"
        >
          <span v-if="store.loading">
            Generating...
          </span>

          <span v-else>
            Generate Question
          </span>
        </button>
      </div>

      <!-- Controls -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Category -->
        <div class="bg-white rounded-3xl border border-blue-100 p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 mb-5">
            Select Category
          </h3>

          <div class="flex flex-wrap gap-4">
            <button
              v-for="item in categories"
              :key="item"
              @click="selectedCategory = item"
              class="px-6 py-4 rounded-2xl border transition-all duration-300 font-semibold"
              :class="
                selectedCategory === item
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent shadow-lg'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'
              "
            >
              {{ item }}
            </button>
          </div>
        </div>

        <!-- Difficulty -->
        <div class="bg-white rounded-3xl border border-blue-100 p-6 shadow-sm">
          <h3 class="font-bold text-slate-800 mb-5">
            Select Difficulty
          </h3>

          <div class="flex flex-wrap gap-4">
            <button
              v-for="item in difficulties"
              :key="item"
              @click="selectedDifficulty = item"
              class="px-6 py-4 rounded-2xl border transition-all duration-300 font-semibold"
              :class="
                selectedDifficulty === item
                  ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white border-transparent shadow-lg'
                  : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'
              "
            >
              {{ item }}
            </button>
          </div>
        </div>

      </div>

      <!-- Evaluation Result -->
      <div
        v-if="evaluationResult"
        class="bg-white rounded-3xl border p-6 shadow-sm space-y-5"
        :class="
          evaluationResult.is_correct
            ? 'border-green-200 bg-green-50'
            : 'border-red-200 bg-red-50'
        "
      >

        <!-- Status -->
        <div class="flex items-center gap-3">
          <span
            class="text-sm font-bold px-4 py-2 rounded-full"
            :class="
              evaluationResult.is_correct
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            "
          >
            {{
              evaluationResult.is_correct
                ? '✓ Correct Answer'
                : '✗ Incorrect Answer'
            }}
          </span>
        </div>

        <!-- Correct Answer -->
        <div class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">
            ✅ Correct Answer
          </h3>

          <p class="text-slate-700">
            {{ evaluationResult.correct_answer }}
          </p>
        </div>

        <!-- Translation -->
        <div class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">
            🇮🇩 Translation
          </h3>

          <p class="text-slate-700 leading-relaxed">
            {{ evaluationResult.translation }}
          </p>
        </div>

        <!-- Explanation -->
        <div class="bg-white rounded-2xl p-4 border border-slate-100">
          <h3 class="font-bold text-slate-800 mb-2">
            📘 Explanation
          </h3>

          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.explanation }}
            </p>
          </div>

          <div>
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.explanation_id }}
            </p>
          </div>
        </div>

        <!-- Why Wrong -->
        <div
          v-if="!evaluationResult.is_correct"
          class="bg-white rounded-2xl p-4 border border-red-100"
        >
          <h3 class="font-bold text-red-700 mb-2">
            ❌ Why Your Answer Is Wrong
          </h3>

          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.why_wrong }}
            </p>
          </div>

          <div>
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.why_wrong_id }}
            </p>
          </div>
        </div>

        <!-- Grammar Tip -->
        <div class="bg-white rounded-2xl p-4 border border-blue-100">
          <h3 class="font-bold text-blue-700 mb-2">
            💡 Grammar Tip
          </h3>

          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.grammar_tip }}
            </p>
          </div>

          <div>
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.grammar_tip_id }}
            </p>
          </div>
        </div>

        <!-- TOEFL Tip -->
        <div class="bg-white rounded-2xl p-4 border border-cyan-100">
          <h3 class="font-bold text-cyan-700 mb-2">
            🎯 TOEFL Strategy Tip
          </h3>

          <div class="mb-4">
            <p class="text-xs font-semibold text-slate-500 mb-1">English:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.toefl_tip }}
            </p>
          </div>

          <div>
            <p class="text-xs font-semibold text-slate-500 mb-1">Bahasa Indonesia:</p>
            <p class="text-slate-700 leading-relaxed">
              {{ evaluationResult.toefl_tip_id }}
            </p>
          </div>
        </div>

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
        class="bg-white border border-dashed border-blue-200 rounded-3xl p-20 text-center overflow-hidden relative"
      >

        <!-- Background Glow -->
        <div class="absolute inset-0 pointer-events-none">
          <div
            class="absolute w-72 h-72 bg-cyan-200/30 blur-3xl rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
          />
        </div>

        <!-- AI Animation -->
        <div class="relative z-10 mb-4 flex justify-center">
          <AIAnimation />
        </div>

        <!-- Title -->
        <h2 class="text-3xl font-bold text-slate-800 relative z-10">
          Start TOEFL Practice
        </h2>

        <!-- Subtitle -->
        <p
          class="text-slate-500 mt-4 max-w-xl mx-auto leading-relaxed relative z-10"
        >
          Select category and difficulty, then generate adaptive TOEFL
          questions powered by AI.
        </p>

      </div>

    </div>
  </MainLayout>
</template>

<script setup>
import { ref } from 'vue'

import MainLayout from '@/layouts/MainLayout.vue'
import QuestionCard from '@/components/QuestionCard.vue'
import AIAnimation from '@/components/AIAnimation.vue'

import { useToeflStore } from '@/store/useToeflStore'

const store = useToeflStore()

const categories = ['Grammar', 'Vocabulary', 'Reading']

const difficulties = [
  'Easy',
  'Intermediate',
  'Advanced'
]

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

const submitAnswer = async (answer) => {
  if (!store.currentQuestion) {
    console.error('❌ No current question')
    return
  }

  console.log('\n========== SUBMIT ANSWER START ==========')
  evaluationResult.value = null

  const payload = {
    question: store.currentQuestion.question,
    options: store.currentQuestion.options,
    user_answer: answer,
    correct_answer: store.currentQuestion.answer,
    category: selectedCategory.value,
    difficulty: selectedDifficulty.value
  }

  console.log('📤 Payload:', JSON.stringify(payload, null, 2))

  try {
    console.log('⏳ Calling store.evaluateAnswer...')
    const result = await store.evaluateAnswer(payload)

    console.log('📥 Result from store:', result)
    console.log('Result type:', typeof result)
    console.log('Result is null:', result === null)
    console.log('Result is undefined:', result === undefined)
    console.log('Result keys:', result ? Object.keys(result) : 'N/A')

    if (result && typeof result === 'object') {
      evaluationResult.value = result
      console.log('✅ evaluationResult.value SET:', evaluationResult.value)
    } else {
      console.warn('⚠️  Result is not an object:', result)
      evaluationResult.value = null
    }
  } catch (error) {
    console.error('❌ Submit Answer Error:', error.message)
    console.error('Full error:', error)
  }
  console.log('========== SUBMIT ANSWER END ==========' )
}
</script>