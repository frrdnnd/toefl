<template>
  <div class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 space-y-4">
    <div>
      <h3 class="text-lg font-semibold text-slate-800">
        Submit Your Answer
      </h3>

      <p class="text-sm text-slate-500 mt-1">
        Choose your best answer before submitting.
      </p>
    </div>

    <button
      @click="submitAnswer"
      :disabled="!selectedAnswer || loading"
      class="w-full py-3 rounded-2xl font-semibold transition-all duration-300"
      :class="!selectedAnswer
        ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
        : 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white hover:shadow-lg hover:scale-[1.01]'"
    >
      {{ loading ? 'Evaluating...' : 'Submit Answer' }}
    </button>
  </div>
</template>

<script setup>
const props = defineProps({
  selectedAnswer: String,
  loading: Boolean
})

const emit = defineEmits(['submit'])

const submitAnswer = () => {
  emit('submit', props.selectedAnswer)
}
</script>