import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// Создаем экземпляр axios
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Интерцептор для добавления токена авторизации
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Токен истек или недействителен
      localStorage.removeItem('token')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

// Типы для API
export interface Model {
  id: number
  name: string
  code: string
  brand?: string
  category?: string
  year_from?: number
  year_to?: number
  description?: string
  image_url?: string
  is_active: boolean
  year_range: string
  has_files: boolean
  created_at: string
  updated_at?: string
}

export interface File {
  id: number
  model_id: number
  title: string
  file_type: string
  size_bytes: number
  is_public: boolean
  version?: string
  tags?: any
  size_mb: number
  is_image: boolean
  is_document: boolean
  is_archive: boolean
  created_at: string
  updated_at?: string
}

export interface Ticket {
  id: number
  user_id: number
  model_id?: number
  subject: string
  description: string
  priority: 'low' | 'normal' | 'high'
  status: 'open' | 'in_progress' | 'resolved' | 'closed'
  assignee_id?: number
  is_open: boolean
  is_closed: boolean
  created_at: string
  updated_at?: string
  closed_at?: string
}

export interface TicketMessage {
  id: number
  ticket_id: number
  author_id: number
  body: string
  attachments?: any[]
  is_internal_note: boolean
  created_at: string
  author: {
    id: number
    full_name: string
    role: string
  }
}

export interface User {
  id: number
  telegram_user_id: number
  username?: string
  first_name?: string
  last_name?: string
  language_code: string
  role: 'user' | 'admin'
  is_blocked: boolean
  full_name: string
  is_admin: boolean
  created_at: string
  updated_at?: string
}

// API функции
export const modelsApi = {
  getModels: async (params?: any) => {
    const response = await api.get('/models', { params })
    return response.data
  },
  
  getModel: async (id: number) => {
    const response = await api.get(`/models/${id}`)
    return response.data
  },
  
  createModel: async (data: any) => {
    const response = await api.post('/models', data)
    return response.data
  },
  
  updateModel: async (id: number, data: any) => {
    const response = await api.put(`/models/${id}`, data)
    return response.data
  },
  
  deleteModel: async (id: number) => {
    const response = await api.delete(`/models/${id}`)
    return response.data
  }
}

export const filesApi = {
  getFiles: async (params?: any) => {
    const response = await api.get('/files', { params })
    return response.data
  },
  
  getFile: async (id: number) => {
    const response = await api.get(`/files/${id}`)
    return response.data
  },
  
  getDownloadUrl: async (id: number, expiresInMinutes = 15) => {
    const response = await api.get(`/files/${id}/download-url`, {
      params: { expires_in_minutes: expiresInMinutes }
    })
    return response.data
  },
  
  uploadFile: async (modelId: number, file: File, title: string, version?: string) => {
    const formData = new FormData()
    formData.append('file', file as any)
    formData.append('title', title)
    if (version) formData.append('version', version)
    
    const response = await api.post(`/files/`, formData, {
      params: { model_id: modelId },
      headers: { 'Content-Type': 'multipart/form-data' }
    } as any)
    return response.data
  },
  
  updateFile: async (id: number, data: any) => {
    const response = await api.put(`/files/${id}`, data)
    return response.data
  },
  
  deleteFile: async (id: number) => {
    const response = await api.delete(`/files/${id}`)
    return response.data
  }
}

export const ticketsApi = {
  getTickets: async (params?: any) => {
    const response = await api.get('/tickets', { params })
    return response.data
  },
  
  getTicket: async (id: number) => {
    const response = await api.get(`/tickets/${id}`)
    return response.data
  },
  
  createTicket: async (data: any) => {
    const response = await api.post('/tickets', data)
    return response.data
  },
  
  updateTicket: async (id: number, data: any) => {
    const response = await api.put(`/tickets/${id}`, data)
    return response.data
  },
  
  getTicketMessages: async (id: number) => {
    const response = await api.get(`/tickets/${id}/messages`)
    return response.data
  },
  
  createTicketMessage: async (id: number, data: any) => {
    const response = await api.post(`/tickets/${id}/messages`, data)
    return response.data
  },
  
  getTicketStats: async () => {
    const response = await api.get('/tickets/stats')
    return response.data
  },

  // Model files API
  uploadModelFile: async (modelId: number, file: File, comment?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (comment) formData.append('comment', comment)
    
    const response = await api.post(`/models/${modelId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },

  getModelFiles: async (modelId: number) => {
    const response = await api.get(`/models/${modelId}/files`)
    return response.data
  },

  deleteModelFile: async (modelId: number, fileId: number) => {
    const response = await api.delete(`/models/${modelId}/files/${fileId}`)
    return response.data
  }
}

export const adminApi = {
  getUsers: async (params?: any) => {
    const response = await api.get('/admin/users', { params })
    return response.data
  },
  
  updateUser: async (id: number, data: any) => {
    const response = await api.put(`/admin/users/${id}`, data)
    return response.data
  },
  
  getAdminStats: async () => {
    const response = await api.get('/admin/stats')
    return response.data
  }
}
