import axios from "axios";

const API_URL = "/api/v1/auth";

export const register = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}/register`, userData);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const login = async (credentials) => {
  try {
    const response = await axios.post(`${API_URL}/login`, credentials);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const requestPasswordReset = async (email) => {
  try {
    const response = await axios.post(`${API_URL}/request-password-reset`, { email });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const resetPassword = async (token, newPassword) => {
  try {
    const response = await axios.post(`${API_URL}/reset-password`, { token, new_password: newPassword });
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const verifyEmail = async (token) => {
  try {
    const response = await axios.get(`${API_URL}/verify-email?token=${token}`);
    return response.data;
  } catch (error) {
    throw error.response.data;
  }
};

export const logout = async () => {
  try {
    await axios.post(`${API_URL}/logout`);
    return { success: true };
  } catch (error) {
    throw error.response.data;
  }
};