import { defineStore } from 'pinia'
import { ref } from 'vue'

import questionService from '@/services/questionService'

export const useToeflStore = defineStore('toefl', () => {

  const currentQuestion = ref(null)
  const source = ref(null)          // dataset | openai | ollama
  const loading = ref(false)

  const history = ref([])
  const analytics = ref(null)
  const recommendation = ref(null)
  const weakness = ref(null)

  // =========================
  // GENERATE QUESTION
  // =========================
  const generateQuestion = async (category, difficulty, mode = 'dataset') => {
    loading.value = true
    try {
      const res = await questionService.generateQuestion({ category, difficulty, mode })
      currentQuestion.value = res?.data ?? null
      source.value = res?.source ?? null
      return res
    } catch (error) {
      console.error('[Store] generateQuestion error:', error)
      currentQuestion.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  // =========================
  // CHECK ANSWER (single question)
  // =========================
  const checkAnswer = async (payload) => {
    try {
      const result = await questionService.checkAnswer(payload)
      return result
    } catch (error) {
      console.error('[Store] checkAnswer error:', error)
      return null
    }
  }

  // Refresh analytics/history after a practice session.
  const refreshProgress = async () => {
    await fetchHistory()
    await fetchDashboard()
  }

  // =========================
  // HISTORY
  // =========================
  const fetchHistory = async () => {
    try {
      history.value = await questionService.getHistory()
    } catch (error) {
      console.error(error)
    }
  }

  const clearHistory = async () => {
    try {
      await questionService.clearHistory()
      history.value = []
      await fetchDashboard()
    } catch (error) {
      console.error(error)
    }
  }

  // =========================
  // DASHBOARD / ANALYTICS
  // =========================
  const fetchDashboard = async () => {
    try {
      analytics.value = await questionService.getAnalytics()
      recommendation.value = await questionService.getRecommendation()
      weakness.value = await questionService.getWeaknessAnalysis()
    } catch (error) {
      console.error(error)
    }
  }

  return {
    currentQuestion,
    source,
    loading,
    history,
    analytics,
    recommendation,
    weakness,
    generateQuestion,
    checkAnswer,
    refreshProgress,
    fetchHistory,
    clearHistory,
    fetchDashboard
  }
})
