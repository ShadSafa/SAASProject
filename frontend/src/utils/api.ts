import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create Axios instance
export const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,  // Include httpOnly cookies automatically
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (for future token attachment if needed)
api.interceptors.request.use(
  (config) => {
    // httpOnly cookies are automatically included by browser
    // If using localStorage tokens (NOT RECOMMENDED), attach here:
    // const token = localStorage.getItem('access_token');
    // if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth state
      console.error('Unauthorized request - user may need to log in');
    }
    return Promise.reject(error);
  }
);

export default api;
