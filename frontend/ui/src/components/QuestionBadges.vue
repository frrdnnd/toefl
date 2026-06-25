<template>
  <div class="flex flex-wrap items-center gap-2">
    <span
      v-if="category"
      class="text-xs px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-semibold capitalize"
    >
      {{ category }}
    </span>

    <span
      v-if="difficulty"
      class="text-xs px-3 py-1 rounded-full font-semibold capitalize"
      :class="difficultyClass"
    >
      {{ difficulty }}
    </span>

    <span
      v-if="estimatedRange"
      class="text-xs px-3 py-1 rounded-full bg-cyan-100 text-cyan-700 font-semibold"
    >
      TOEFL ITP {{ estimatedRange }}
    </span>

    <span
      v-if="topic"
      class="text-xs px-3 py-1 rounded-full bg-slate-100 text-slate-600 font-semibold capitalize"
    >
      {{ topic }}
    </span>

    <span
      v-if="source"
      class="text-xs px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 font-semibold capitalize"
    >
      {{ sourceLabel }}
    </span>

    <span
      v-if="rag"
      class="text-xs px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 font-semibold"
      title="Grounded with RAG knowledge"
    >
      ⛁ RAG
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  category: { type: String, default: '' },
  difficulty: { type: String, default: '' },
  estimatedRange: { type: String, default: '' },
  topic: { type: String, default: '' },
  source: { type: String, default: '' },
  rag: { type: Boolean, default: false }
})

const difficultyClass = computed(() => {
  const value = (props.difficulty || '').toLowerCase()
  if (value === 'advanced') return 'bg-purple-100 text-purple-700'
  if (value === 'intermediate' || value === 'medium') return 'bg-amber-100 text-amber-700'
  return 'bg-green-100 text-green-700'
})

const sourceLabel = computed(() => {
  const value = (props.source || '').toLowerCase()
  if (value === 'openai') return 'AI · OpenAI'
  if (value === 'ollama') return 'AI · Ollama'
  if (value === 'dataset') return 'Dataset'
  return props.source
})
</script>
