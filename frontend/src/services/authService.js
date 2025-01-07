// src/services/authService.js

const BASE_URL = import.meta.env.VITE_API_URL || '';

class AuthService {
  async login(username, password) {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      if (data.success) {
        localStorage.setItem('user_id', data.user_id.toString());
        localStorage.setItem('username', data.username);
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  async logout() {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Logout failed');
      }

      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
      return data;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }

  async register(userData) {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed');
      }

      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  async getCurrentUser() {
    try {
      const response = await fetch(`${BASE_URL}/api/v1/auth/me`, {
        credentials: 'include',
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get user');
      }

      return data;
    } catch (error) {
      console.error('Get current user error:', error);
      throw error;
    }
  }
}

export const authService = new AuthService();
