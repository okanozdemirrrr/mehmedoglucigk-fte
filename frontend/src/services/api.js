import axios from 'axios';

const resolveApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }

  if (typeof window !== 'undefined' && window.location.hostname.includes('vercel.app')) {
    return 'https://mehmedoglu-b2b-api.onrender.com/api/';
  }

  return 'http://localhost:8000/api/';
};

const api = axios.create({
  baseURL: resolveApiBaseUrl(),
});

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

export default api;
