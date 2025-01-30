import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import * as SecureStore from 'expo-secure-store';

export const authService = {
  async login(username: string, password: string) {
    try {
      const response = await axios.post(`${API_BASE_URL}${API_ENDPOINTS.auth.login}`, {
        username,
        password,
        device_type: 'android',
        device_id: await SecureStore.getItemAsync('deviceId'),
      });

      if (response.data.success) {
        await SecureStore.setItemAsync('token', response.data.token);
        await SecureStore.setItemAsync('user', JSON.stringify(response.data.user));
      }

      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  async logout() {
    await SecureStore.deleteItemAsync('token');
    await SecureStore.deleteItemAsync('user');
  },

  async refreshToken() {
    const token = await SecureStore.getItemAsync('token');
    try {
      const response = await axios.post(
        `${API_BASE_URL}${API_ENDPOINTS.auth.refreshToken}`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.success) {
        await SecureStore.setItemAsync('token', response.data.token);
      }
      
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
}; 