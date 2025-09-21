import axios from 'axios'

const api = axios.create({
  baseURL: 'https://api.gakshop.com/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

export const modelsApi = {
  getModels: () => api.get('/models').then(r => r.data),
  createModel: (data: any) => api.post('/models', data).then(r => r.data),
  updateModel: (id: number, data: any) => api.put(`/models/${id}`, data).then(r => r.data),
  deleteModel: (id: number) => api.delete(`/models/${id}`).then(r => r.data),
  getModelFiles: (id: number) => api.get(`/models/${id}/files`).then(r => r.data),
  uploadFile: (modelId: number, data: any) => api.post(`/models/${modelId}/files`, data).then(r => r.data),
}

export const ticketsApi = {
  getTickets: () => api.get('/tickets').then(r => r.data),
  createTicket: (data: any) => api.post('/tickets', data).then(r => r.data),
  getTicket: (id: number) => api.get(`/tickets/${id}`).then(r => r.data),
  getMessages: (id: number) => api.get(`/tickets/${id}/messages`).then(r => r.data),
  sendMessage: (id: number, data: any) => api.post(`/tickets/${id}/messages`, data).then(r => r.data),
}

export const adminApi = {
  getStats: () => api.get('/admin/stats').then(r => r.data),
}

export const authApi = {
  verify: () => api.post('/auth/verify').then(r => r.data),
}
