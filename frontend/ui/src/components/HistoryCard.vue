<template>
  <div class="bg-white border border-blue-100 rounded-3xl p-5 shadow-sm hover:shadow-md transition-all duration-300">
    <div class="flex items-start justify-between gap-4 mb-4">
      <div>
        <p class="text-xs text-slate-500 mb-1">
          {{ item.category }} • {{ item.difficulty }}
        </p>

        <h3 class="font-semibold text-slate-800 leading-relaxed">
          {{ item.question }}
        </h3>
      </div>

      <div>
        <span
          class="text-xs px-3 py-1 rounded-full font-medium"
          :class="item.is_correct
            ? 'bg-green-100 text-green-700'
            : 'bg-red-100 text-red-700'"
        >
          {{ item.is_correct ? 'Correct' : 'Wrong' }}
        </span>
      </div>
    </div>

    <div class="grid md:grid-cols-2 gap-4 text-sm">
      <div>
        <p class="text-slate-500">Your Answer</p>
        <p class="font-semibold text-slate-700">
          {{ item.user_answer }}
        </p>
      </div>

      <div>
        <p class="text-slate-500">Weakness</p>
        <p class="font-semibold text-slate-700">
          {{ item.weakness_detected || 'None' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  item: Object
})
</script>