import axios from 'axios';

const api = axios.create({ baseURL: '/api/v1' });

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto logout on 401
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

/* ─── Auth ─── */
export const authService = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => {
    const form = new URLSearchParams();
    form.append('username', data.email);
    form.append('password', data.password);
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } });
  },
  me: () => api.get('/auth/me'),
};

/* ─── Resumes ─── */
export const resumeService = {
  upload: (formData) => api.post('/resumes/upload', formData),
  list: () => api.get('/resumes/'),
  get: (id) => api.get(`/resumes/${id}`),
  setPrimary: (id) => api.put(`/resumes/${id}/primary`),
  delete: (id) => api.delete(`/resumes/${id}`),
};

/* ─── Jobs ─── */
export const jobService = {
  create: (data) => api.post('/jobs/', data),
  list: (params) => api.get('/jobs/', { params }),
  get: (id) => api.get(`/jobs/${id}`),
  update: (id, data) => api.put(`/jobs/${id}`, data),
  patchStatus: (id, status) => api.patch(`/jobs/${id}/status`, { status }),
  stats: () => api.get('/jobs/stats'),
  delete: (id) => api.delete(`/jobs/${id}`),
};

/* ─── Matching ─── */
export const matchService = {
  analyze: (data) => api.post('/matching/analyze', data),
  history: (params) => api.get('/matching/history', { params }),
  get: (id) => api.get(`/matching/${id}`),
  delete: (id) => api.delete(`/matching/${id}`),
};
