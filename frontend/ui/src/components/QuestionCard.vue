<template>
  <div
    v-if="question"
    class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 space-y-6"
  >
    <!-- Meta badges -->
    <div class="flex items-center justify-between gap-4">
      <QuestionBadges
        :category="question.section"
        :difficulty="question.difficulty"
        :estimated-range="question.estimated_toefl_range"
        :topic="question.topic"
        :source="source"
        :rag="!!question.rag_used"
      />
      <span class="text-sm text-slate-400 whitespace-nowrap">TOEFL Practice</span>
    </div>

    <!-- Question -->
    <h2 class="text-xl font-semibold text-slate-800 leading-relaxed">
      {{ question.question }}
    </h2>

    <!-- Options -->
    <div class="grid gap-4">
      <button
        v-for="letter in letters"
        :key="letter"
        @click="selectedAnswer = letter"
        class="w-full text-left p-4 rounded-2xl border transition-all duration-300"
        :class="selectedAnswer === letter
          ? 'border-blue-500 bg-blue-50 shadow-sm'
          : 'border-slate-200 hover:border-blue-300 hover:bg-blue-50/40'"
      >
        <span class="font-bold text-blue-600 mr-2">{{ letter }}.</span>
        {{ question.options?.[letter] }}
      </button>
    </div>

    <!-- Submit -->
    <button
      @click="handleSubmit"
      :disabled="!selectedAnswer"
      class="w-full py-3 rounded-2xl font-semibold transition-all duration-300"
      :class="!selectedAnswer
        ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
        : 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white hover:shadow-lg hover:scale-[1.01]'"
    >
      Submit Answer
    </button>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import QuestionBadges from '@/components/QuestionBadges.vue'

const props = defineProps({
  question: Object,
  source: { type: String, default: '' }
})

const emit = defineEmits(['submit-answer'])

const letters = ['A', 'B', 'C', 'D']
const selectedAnswer = ref(null)

// Reset selection whenever a new question is loaded.
watch(() => props.question, () => {
  selectedAnswer.value = null
})

const handleSubmit = () => {
  if (!selectedAnswer.value) return
  emit('submit-answer', selectedAnswer.value)
}
</script>
