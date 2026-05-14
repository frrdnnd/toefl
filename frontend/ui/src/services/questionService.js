import api from './api'

export default {

  async generateQuestion(data) {
    // api interceptor sudah return response.data, jadi tidak perlu .data lagi
    const response = await api.post('/generate-question', data)
    return response
  },

  async evaluateAnswer(data) {
    const response = await api.post('/evaluate-answer', data)
    return response
  },

  async getHistory() {
    const response = await api.get('/history')
    return response
  },

  async clearHistory() {
    const response = await api.delete('/history')
    return response
  },

  async getAnalytics() {
    const response = await api.get('/analytics')
    return response
  },

  async getRecommendation() {
    const response = await api.get('/recommendation')
    return response
  },

  async getWeaknessAnalysis() {
    const response = await api.get('/weakness-analysis')
    return response
  }
}