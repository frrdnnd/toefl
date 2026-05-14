import { defineStore } from 'pinia'
import { ref } from 'vue'

import questionService from '@/services/questionService'

export const useToeflStore = defineStore(
  'toefl',
  () => {

    const currentQuestion = ref(null)

    const loading = ref(false)

    const history = ref([])

    const analytics = ref(null)

    const recommendation = ref(null)

    const weakness = ref(null)

    // =========================
    // GENERATE QUESTION
    // =========================

    const generateQuestion = async (
      category,
      difficulty
    ) => {

      loading.value = true

      try {

        const data =
          await questionService.generateQuestion({
            category,
            difficulty
          })

        currentQuestion.value = data

      } catch (error) {

        console.error(error)

      } finally {

        loading.value = false
      }
    }

    // =========================
    // EVALUATE ANSWER
    // =========================

    const evaluateAnswer = async (
      payload
    ) => {

      loading.value = true

      try {

        const result =
          await questionService.evaluateAnswer(
            payload
          )

        await fetchHistory()

        await fetchDashboard()

        return result

      } catch (error) {

        console.error(error)

      } finally {

        loading.value = false
      }
    }

    // =========================
    // HISTORY
    // =========================

    const fetchHistory = async () => {

      try {

        history.value =
          await questionService.getHistory()

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
    // DASHBOARD
    // =========================

    const fetchDashboard = async () => {

      try {

        analytics.value =
          await questionService.getAnalytics()

        recommendation.value =
          await questionService.getRecommendation()

        weakness.value =
          await questionService.getWeaknessAnalysis()

      } catch (error) {

        console.error(error)
      }
    }

    return {

      currentQuestion,

      loading,

      history,

      analytics,

      recommendation,

      weakness,

      generateQuestion,

      evaluateAnswer,

      fetchHistory,

      clearHistory,

      fetchDashboard
    }
  }
)