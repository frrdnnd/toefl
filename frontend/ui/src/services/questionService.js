import api from './api'

export default {

  // New API: generate a question from the dataset / AI / hybrid pipeline.
  // Returns { success, source, data }.
  async generateQuestion({ category, difficulty, mode = 'dataset' }) {
    const response = await api.get('/api/questions/generate', {
      params: { category, difficulty, mode }
    })
    return response
  },

  // New API: check a single answer. Returns evaluation + recommendation.
  async checkAnswer(payload) {
    const response = await api.post('/api/questions/check-answer', payload)
    return response
  },

  // Legacy endpoints kept for backward compatibility.
  async evaluateAnswer(data) {
    const response = await api.post('/evaluate-answer', data)
    return response
  },

  async getHistory() {
    return await api.get('/history')
  },

  async clearHistory() {
    return await api.delete('/history')
  },

  async getAnalytics() {
    return await api.get('/analytics')
  },

  async getRecommendation() {
    return await api.get('/recommendation')
  },

  async getWeaknessAnalysis() {
    return await api.get('/weakness-analysis')
  }
}
