<template>
  <div
    v-if="question"
    class="space-y-6"
  >
    <!-- Passage -->
    <div class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 md:p-8 space-y-5">
      <div class="flex items-center justify-between gap-4">
        <QuestionBadges
          :category="question.section"
          :difficulty="question.difficulty"
          :estimated-range="question.estimated_toefl_range"
          :topic="question.topic"
          :source="source"
          :rag="!!question.rag_used"
        />
        <span class="text-sm text-slate-400 whitespace-nowrap">Reading Passage</span>
      </div>

      <h2 class="text-2xl font-bold text-slate-800 capitalize">
        {{ question.topic }}
      </h2>

      <p class="text-slate-700 leading-8 whitespace-pre-line text-[15px]">
        {{ question.passage }}
      </p>
    </div>

    <!-- Questions -->
    <div
      v-for="(item, index) in question.questions"
      :key="item.id"
      class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 space-y-4"
    >
      <div class="flex items-start justify-between gap-3">
        <h3 class="font-semibold text-slate-800 leading-relaxed">
          <span class="text-blue-600 font-bold mr-1">{{ index + 1 }}.</span>
          {{ item.question }}
        </h3>
        <span class="text-[11px] px-2 py-1 rounded-full bg-slate-100 text-slate-500 font-semibold whitespace-nowrap capitalize">
          {{ formatType(item.type) }}
        </span>
      </div>

      <div class="grid gap-3">
        <button
          v-for="letter in letters"
          :key="letter"
          :disabled="submitted"
          @click="answers[item.id] = letter"
          class="w-full text-left p-3.5 rounded-2xl border transition-all duration-200"
          :class="optionClass(item, letter)"
        >
          <span class="font-bold mr-2">{{ letter }}.</span>
          {{ item.options?.[letter] }}
        </button>
      </div>

      <!-- Per-question result -->
      <div
        v-if="submitted && results[item.id]"
        class="rounded-2xl p-4 text-sm"
        :class="results[item.id].is_correct
          ? 'bg-green-50 border border-green-100'
          : 'bg-red-50 border border-red-100'"
      >
        <p class="font-bold mb-1" :class="results[item.id].is_correct ? 'text-green-700' : 'text-red-700'">
          {{ results[item.id].is_correct ? '✓ Correct' : '✗ Incorrect' }}
          <span class="text-slate-500 font-normal">
            · Correct answer: {{ results[item.id].correct_answer_text || results[item.id].correct_answer }}
          </span>
        </p>
        <p class="text-slate-700 leading-relaxed">{{ item.explanation }}</p>
        <p
          v-if="!results[item.id].is_correct && results[item.id].recommendation"
          class="text-slate-600 mt-2"
        >
          💡 {{ results[item.id].recommendation }}
        </p>
      </div>
    </div>

    <!-- Summary + submit -->
    <div class="bg-white rounded-3xl border border-blue-100 shadow-sm p-6 space-y-4">
      <div v-if="submitted" class="text-center">
        <p class="text-slate-500">Your score for this passage</p>
        <p class="text-4xl font-extrabold text-blue-600 mt-1">
          {{ correctCount }} / {{ question.questions.length }}
        </p>
      </div>

      <button
        v-if="!submitted"
        @click="handleSubmit"
        :disabled="!allAnswered || loading"
        class="w-full py-3 rounded-2xl font-semibold transition-all duration-300"
        :class="(!allAnswered || loading)
          ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
          : 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white hover:shadow-lg hover:scale-[1.01]'"
      >
        <span v-if="loading">Checking...</span>
        <span v-else-if="allAnswered">Submit Answers</span>
        <span v-else>Answer all {{ question.questions.length }} questions to submit</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import QuestionBadges from '@/components/QuestionBadges.vue'

const props = defineProps({
  question: Object,
  source: { type: String, default: '' },
  results: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['submit-reading'])

const letters = ['A', 'B', 'C', 'D']
const answers = reactive({})
const submitted = ref(false)

// Reset when a new passage is loaded.
watch(() => props.question, () => {
  Object.keys(answers).forEach((key) => delete answers[key])
  submitted.value = false
})

// Mark submitted once the parent has provided results.
watch(() => props.results, (value) => {
  if (value && Object.keys(value).length) {
    submitted.value = true
  }
}, { deep: true })

const allAnswered = computed(() =>
  (props.question?.questions || []).every((item) => answers[item.id])
)

const correctCount = computed(() =>
  Object.values(props.results || {}).filter((r) => r.is_correct).length
)

const formatType = (type) => (type || '').replace(/_/g, ' ')

const optionClass = (item, letter) => {
  const selected = answers[item.id]

  if (submitted.value && props.results[item.id]) {
    if (letter === item.answer) return 'border-green-500 bg-green-50 text-slate-800'
    if (letter === selected) return 'border-red-400 bg-red-50 text-slate-800'
    return 'border-slate-200 text-slate-500'
  }

  return selected === letter
    ? 'border-blue-500 bg-blue-50 shadow-sm'
    : 'border-slate-200 hover:border-blue-300 hover:bg-blue-50/40'
}

const handleSubmit = () => {
  if (!allAnswered.value) return

  const payload = props.question.questions.map((item) => ({
    id: item.id,
    type: item.type,
    question: item.question,
    options: item.options,
    answer: item.answer,
    explanation: item.explanation,
    selected: answers[item.id]
  }))

  emit('submit-reading', payload)
}
</script>
