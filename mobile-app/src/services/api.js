import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Update this URL to match your backend
const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear auth data on unauthorized
      await AsyncStorage.multiRemove(['auth_token', 'user_id', 'username']);
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },

  register: async (username, email, password) => {
    const response = await api.post('/auth/register', { username, email, password });
    return response.data;
  },

  logout: async () => {
    const response = await api.post('/auth/logout');
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Goals endpoints
export const goalsAPI = {
  getGoals: async (userId) => {
    const response = await api.get(`/goals/user/${userId}`);
    return response.data;
  },

  getGoal: async (goalId) => {
    const response = await api.get(`/goals/${goalId}`);
    return response.data;
  },

  createGoal: async (goalData) => {
    const response = await api.post('/goals/create', goalData);
    return response.data;
  },

  updateGoal: async (goalData) => {
    const response = await api.put('/goals/update', goalData);
    return response.data;
  },

  deleteGoal: async (goalId) => {
    const response = await api.delete(`/goals/${goalId}`);
    return response.data;
  },

  getSuggestions: async (userId) => {
    const response = await api.get(`/goals/suggestions/${userId}`);
    return response.data;
  },
};

// Progress endpoints
export const progressAPI = {
  getProgress: async (goalId) => {
    const response = await api.get(`/progress/${goalId}`);
    return response.data;
  },

  addProgress: async (goalId, progressData) => {
    const response = await api.post(`/progress/${goalId}`, progressData);
    return response.data;
  },
};

export default api;
