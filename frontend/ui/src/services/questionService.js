import api from './api'

export default {

  async generateQuestion(data) {
    // api interceptor sudah return response.data, jadi tidak perlu .data lagi
    const response = await api.post('/generate-question', data)
    return response
  },

  async evaluateAnswer(data) {
    console.log('\n[Service] evaluateAnswer called')
    console.log('[Service] Payload:', data)
    try {
      console.log('[Service] Making POST request to /evaluate-answer')
      const response = await api.post('/evaluate-answer', data)
      console.log('[Service] Response received:', response)
      console.log('[Service] Response type:', typeof response)
      console.log('[Service] Response is array:', Array.isArray(response))
      console.log('[Service] Response keys:', Object.keys(response))
      return response
    } catch (error) {
      console.error('[Service] Evaluation error:', error.message)
      console.error('[Service] Full error:', error)
      throw error
    }
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