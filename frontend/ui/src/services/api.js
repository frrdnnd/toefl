import axios from 'axios'

const api = axios.create({
  // Gunakan fallback ke localhost jika env tidak terbaca
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 180000,  // Slow local LLM calls can take longer on cold starts
  headers: { 
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

/**
 * Request Interceptor
 * Berguna untuk menyisipkan Token atau memodifikasi config sebelum request terkirim.
 */
api.interceptors.request.use(
  (config) => {
    console.log('[API] Request:', config.method.toUpperCase(), config.url)
    // Contoh: const token = localStorage.getItem('token')
    // if (token) config.headers.Authorization = `Bearer ${token}`
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Response Interceptor
 * Menangani hasil kembalian dari server secara terpusat.
 */
api.interceptors.response.use(
  (response) => {
    // Langsung mengembalikan response.data agar di komponen tidak perlu .data.data
    console.log('[API Interceptor] Response received')
    console.log('[API Interceptor] Status:', response.status)
    console.log('[API Interceptor] URL:', response.config.url)
    console.log('[API Interceptor] response.data:', response.data)
    console.log('[API Interceptor] response.data type:', typeof response.data)
    console.log('[API Interceptor] Returning response.data')
    return response.data
  },
  (error) => {
    // Penanganan error global
    const errorMessage = error?.response?.data?.detail || error?.response?.data?.message || error.message
    
    console.error('[API Error]:', {
      status: error?.response?.status,
      url: error?.config?.url,
      method: error?.config?.method,
      message: errorMessage,
      data: error?.response?.data
    })

    // Anda bisa menambahkan logika notifikasi/toast di sini jika status === 401 (Unauthorized)
    
    return Promise.reject(error)
  }
)

export default api
