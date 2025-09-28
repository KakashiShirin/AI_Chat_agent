import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export interface UploadResponse {
  session_id: string
  tables_created: number
  message: string
}

export interface SchemaResponse {
  session_id: string
  schema: Record<string, any>
}

export interface QueryResponse {
  answer: string
  explanation?: string
  chart_type?: string
  chart_data?: any
  generated_code?: string
  raw_data?: string
  api_calls_made?: number
  total_tokens_used?: number
  error?: string
}

export interface ChatSession {
  chat_id: string
  database_session_id: string
  created_at: number
  last_activity: number
  message_count: number
  age_minutes: number
}

export interface ChatContext {
  schema_info?: any
  last_query?: string
  last_result?: any
  conversation_history?: Array<{
    timestamp: number
    message: {
      type: 'user' | 'assistant'
      content: string
      chart_type?: string
      chart_data?: any
    }
  }>
  data_summary?: string
}

export interface ChatResponse extends QueryResponse {
  chat_id: string
  database_session_id: string
  message_count: number
}

export interface ApiKeyStatus {
  total_api_keys: number
  api_key_usage: Record<string, {
    calls_made: number
    tokens_used: number
    last_used?: number
  }>
  total_calls: number
  total_tokens: number
}

export interface CreditUsage {
  total_api_calls: number
  total_tokens_used: number
  estimated_cost_usd: number
  api_keys_count: number
  api_key_usage: Record<string, any>
}

export const apiService = {
  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await api.get('/api/v1/health')
    return response.data
  },

  // File upload
  async uploadFile(file: File): Promise<UploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/api/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Get schema
  async getSchema(sessionId: string): Promise<SchemaResponse> {
    const response = await api.get(`/api/v1/schema/${sessionId}`)
    return response.data
  },

  // Query AI
  async queryAI(query: string, sessionId: string): Promise<QueryResponse> {
    const response = await api.post('/api/v1/query', {
      query,
      session_id: sessionId,
    })
    return response.data
  },

  // Chat Session Management
  async createChatSession(databaseSessionId: string): Promise<{ chat_id: string; database_session_id: string; message: string }> {
    const response = await api.post('/api/v1/chat/create', {
      database_session_id: databaseSessionId,
    })
    return response.data
  },

  async sendChatMessage(query: string, chatId: string): Promise<ChatResponse> {
    const response = await api.post('/api/v1/chat/query', {
      query,
      chat_id: chatId,
    })
    return response.data
  },

  async getChatContext(chatId: string): Promise<{ chat_id: string; context: ChatContext }> {
    const response = await api.get(`/api/v1/chat/${chatId}/context`)
    return response.data
  },

  async getChatSessions(): Promise<{ active_sessions: number; total_messages: number; sessions: ChatSession[] }> {
    const response = await api.get('/api/v1/chat/sessions')
    return response.data
  },

  async deleteChatSession(chatId: string): Promise<{ chat_id: string; message: string }> {
    const response = await api.delete(`/api/v1/chat/${chatId}`)
    return response.data
  },

  async cleanupExpiredSessions(): Promise<{ cleaned_sessions: number; message: string }> {
    const response = await api.post('/api/v1/chat/cleanup')
    return response.data
  },

  // API Key management
  async addApiKey(apiKey: string): Promise<{ message: string; total_keys: number }> {
    const response = await api.post('/api/v1/api-keys/add', {
      api_key: apiKey,
    })
    return response.data
  },

  async validateApiKey(apiKey: string): Promise<{ valid: boolean; message: string }> {
    const response = await api.post('/api/v1/api-keys/validate', {
      api_key: apiKey,
    })
    return response.data
  },

  async getApiKeyStatus(): Promise<ApiKeyStatus> {
    const response = await api.get('/api/v1/api-keys/status')
    return response.data
  },

  // Credit management
  async getCreditUsage(): Promise<CreditUsage> {
    const response = await api.get('/api/v1/credits')
    return response.data
  },

  async resetCreditTracking(): Promise<{ message: string }> {
    const response = await api.post('/api/v1/credits/reset')
    return response.data
  },
}

export default apiService
