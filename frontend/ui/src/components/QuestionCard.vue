<template>
  <div
    v-if="question"
    class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 space-y-6"
  >
    <div class="flex items-center justify-between">
      <span class="text-xs px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">
        {{ question.difficulty }}
      </span>
      <span class="text-sm text-slate-500">
        TOEFL Practice
      </span>
    </div>

    <h2 class="text-xl font-semibold text-slate-800 leading-relaxed">
      {{ question.question }}
    </h2>

    <div class="grid gap-4">
      <button
        v-for="option in question.options"
        :key="option"
        @click="selectedAnswer = option.charAt(0)"
        class="w-full text-left p-4 rounded-2xl border transition-all duration-300"
        :class="selectedAnswer === option.charAt(0)
          ? 'border-blue-500 bg-blue-50 shadow-sm'
          : 'border-slate-200 hover:border-blue-300 hover:bg-blue-50/40'"
      >
        {{ option }}
      </button>
    </div>

    <!-- Submit button -->
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

const props = defineProps({
  question: Object
})

const emit = defineEmits(['submit-answer'])

const selectedAnswer = ref(null)

// Reset pilihan setiap kali soal berganti
watch(() => props.question, () => {
  selectedAnswer.value = null
})

const handleSubmit = () => {
  if (!selectedAnswer.value) return
  emit('submit-answer', selectedAnswer.value)
}
</script>