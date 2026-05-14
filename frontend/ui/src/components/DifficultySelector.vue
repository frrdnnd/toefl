<template>
  <div class="bg-white rounded-2xl p-4 border border-blue-100 shadow-sm">
    <h3 class="text-sm font-semibold text-slate-700 mb-3">
      Select Difficulty
    </h3>

    <div class="flex flex-wrap gap-3">
      <button
        v-for="level in levels"
        :key="level"
        @click="$emit('update:modelValue', level)"
        class="px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300"
        :class="modelValue === level
          ? 'bg-gradient-to-r from-blue-500 to-cyan-400 text-white shadow-md'
          : 'bg-slate-100 text-slate-700 hover:bg-blue-50'"
      >
        {{ level }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: String
})

const levels = ['Easy', 'Intermediate', 'Advanced']
</script>