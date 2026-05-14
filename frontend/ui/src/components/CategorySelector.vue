<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="cat in categories"
      :key="cat.value"
      class="flex items-center gap-2 px-4 py-2 rounded-xl font-medium text-sm transition-all duration-200 border"
      :class="modelValue === cat.value
        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white border-blue-500 shadow-md shadow-blue-200'
        : 'bg-white text-slate-600 border-blue-100 hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50'"
      @click="$emit('update:modelValue', cat.value)"
    >
      <component :is="cat.icon" class="w-4 h-4" />
      {{ cat.label }}
    </button>
  </div>
</template>

<script setup>
import { BookType, AlignLeft, Lightbulb } from 'lucide-vue-next'

defineProps({ modelValue: { type: String, default: 'Grammar' } })
defineEmits(['update:modelValue'])

const categories = [
  { value: 'Grammar',    label: 'Grammar',    icon: BookType },
  { value: 'Vocabulary', label: 'Vocabulary', icon: Lightbulb },
  { value: 'Reading',    label: 'Reading',    icon: AlignLeft }
]
</script>