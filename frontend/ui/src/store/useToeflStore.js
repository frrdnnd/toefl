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

    const evaluationResult = ref(null)

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

    const evaluateAnswer = async (payload) => {

      loading.value = true

      console.log('\n[Store] evaluateAnswer called with:', payload)

      try {

        const result = await questionService.evaluateAnswer(payload)

        console.log('[Store] Response from service:', result)
        console.log('[Store] Response type:', typeof result)
        console.log('[Store] Response keys:', result ? Object.keys(result) : 'N/A')

        evaluationResult.value = result

        console.log('[Store] evaluationResult.value set to:', evaluationResult.value)

        await fetchHistory()

        await fetchDashboard()

        console.log('[Store] Returning result:', result)
        return result

      } catch (error) {

        console.error('[Store] Evaluation Error:', error)
        console.error('[Store] Error message:', error.message)
        console.error('[Store] Error stack:', error.stack)

        return null

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

      evaluationResult,

      generateQuestion,

      evaluateAnswer,

      fetchHistory,

      clearHistory,

      fetchDashboard
    }
  }
)