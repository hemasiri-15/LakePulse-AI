import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

const api = axios.create({
  baseURL: `${BASE}/api`,
  timeout: 15000,
})

// Inject bearer token on every request
api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('lp_token')
  if (token) cfg.headers.Authorization = `Bearer ${token}`
  return cfg
})

// Auto-logout on 401
api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('lp_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authAPI = {
  login:   (username, password) =>
    api.post('/auth/token', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  me:      ()             => api.get('/auth/me'),
  apiKey:  ()             => api.post('/auth/api-key'),
}

// ── Lakes ─────────────────────────────────────────────────────────────────────
export const lakesAPI = {
  list:       ()          => api.get('/lakes'),
  get:        id          => api.get(`/lakes/${id}`),
  create:     data        => api.post('/lakes', data),
  updateScore:(id, score) => api.put(`/lakes/${id}/score`, { score }),
}

// ── Sensors ───────────────────────────────────────────────────────────────────
export const sensorsAPI = {
  ingest:   data          => api.post('/sensors/ingest', data),
  latest:   lakeId        => api.get(`/sensors/${lakeId}/latest`),
  history:  (lakeId, params) => api.get(`/sensors/${lakeId}/history`, { params }),
}

// ── Predictions ───────────────────────────────────────────────────────────────
export const predictionsAPI = {
  latest:   lakeId        => api.get(`/predictions/${lakeId}/latest`),
  create:   data          => api.post('/predictions', data),
}

// ── Alerts ────────────────────────────────────────────────────────────────────
export const alertsAPI = {
  list:       params      => api.get('/alerts', { params }),
  get:        id          => api.get(`/alerts/${id}`),
  create:     data        => api.post('/alerts', data),
  escalate:   id          => api.put(`/alerts/${id}/escalate`),
  resolve:    id          => api.put(`/alerts/${id}/resolve`),
}

// ── Reports ───────────────────────────────────────────────────────────────────
export const reportsAPI = {
  list:       params      => api.get('/reports', { params }),
  create:     data        => api.post('/reports', data),
  updateStatus:(id, status) => api.put(`/reports/${id}/status`, { status }),
}

// ── Satellite ─────────────────────────────────────────────────────────────────
export const satelliteAPI = {
  latest:   lakeId        => api.get(`/satellite/${lakeId}/latest`),
  history:  (lakeId, params) => api.get(`/satellite/${lakeId}/history`, { params }),
  shrinkage:lakeId        => api.get(`/satellite/${lakeId}/shrinkage`),
  alerts:   ()            => api.get('/satellite/alerts'),
  ingest:   data          => api.post('/satellite/ingest', data),
}

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminAPI = {
  stats:      ()          => api.get('/admin/stats'),
  seed:       ()          => api.post('/admin/seed'),
  seedReadings:()         => api.post('/admin/seed/readings'),
  deleteLake: id          => api.delete(`/admin/lakes/${id}`),
  scoreAll:   ()          => api.post('/admin/score/all'),
}

export default api
