import { computed } from 'vue'
import { useToeflStore } from '@/store/useToeflStore.js'

export function useAnalytics() {
  const store = useToeflStore()

  const accuracyColor = computed(() => {
    const acc = store.analytics?.accuracy ?? 0
    if (acc >= 80) return 'text-emerald-600'
    if (acc >= 60) return 'text-blue-600'
    if (acc >= 40) return 'text-amber-600'
    return 'text-red-600'
  })

  const accuracyGradient = computed(() => {
    const acc = store.analytics?.accuracy ?? 0
    if (acc >= 80) return 'from-emerald-400 to-emerald-500'
    if (acc >= 60) return 'from-blue-400 to-blue-500'
    if (acc >= 40) return 'from-amber-400 to-amber-500'
    return 'from-red-400 to-red-500'
  })

  const weaknessItems = computed(() => {
    const w = store.weakness
    if (!w) return []
    return [
      { label: 'Grammar', value: w.grammar ?? 0, color: 'bg-blue-500' },
      { label: 'Vocabulary', value: w.vocabulary ?? 0, color: 'bg-cyan-500' },
      { label: 'Reading', value: w.reading ?? 0, color: 'bg-indigo-400' }
    ]
  })

  const analyticsCards = computed(() => {
    const a = store.analytics
    if (!a) return []
    return [
      {
        title: 'Total Questions',
        value: a.total_questions ?? 0,
        icon: 'BookOpen',
        gradient: 'from-blue-500 to-blue-600',
        bg: 'bg-blue-50',
        iconColor: 'text-blue-600'
      },
      {
        title: 'Correct Answers',
        value: a.correct_answers ?? 0,
        icon: 'CheckCircle',
        gradient: 'from-emerald-400 to-emerald-500',
        bg: 'bg-emerald-50',
        iconColor: 'text-emerald-600'
      },
      {
        title: 'Wrong Answers',
        value: a.wrong_answers ?? 0,
        icon: 'XCircle',
        gradient: 'from-red-400 to-red-500',
        bg: 'bg-red-50',
        iconColor: 'text-red-500'
      },
      {
        title: 'Accuracy',
        value: `${a.accuracy ?? 0}%`,
        icon: 'Target',
        gradient: 'from-purple-400 to-indigo-500',
        bg: 'bg-purple-50',
        iconColor: 'text-purple-600'
      },
      {
        title: 'Suggested Level',
        value: a.suggested_difficulty ?? '—',
        icon: 'TrendingUp',
        gradient: 'from-cyan-400 to-blue-500',
        bg: 'bg-cyan-50',
        iconColor: 'text-cyan-600'
      }
    ]
  })

  return { accuracyColor, accuracyGradient, weaknessItems, analyticsCards }
}