import api from './api'

export default {

  async generateQuestion(data) {

    const response = await api.post(
      '/generate-question',
      data
    )

    return response.data
  },

  async evaluateAnswer(data) {

    const response = await api.post(
      '/evaluate-answer',
      data
    )

    return response.data
  },

  async getHistory() {

    const response = await api.get(
      '/history'
    )

    return response.data
  },

  async clearHistory() {

    const response = await api.delete(
      '/history'
    )

    return response.data
  },

  async getAnalytics() {

    const response = await api.get(
      '/analytics'
    )

    return response.data
  },

  async getRecommendation() {

    const response = await api.get(
      '/recommendation'
    )

    return response.data
  },

  async getWeaknessAnalysis() {

    const response = await api.get(
      '/weakness-analysis'
    )

    return response.data
  }
}