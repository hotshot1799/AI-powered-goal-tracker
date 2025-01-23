import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user_id');
    if (storedUser) {
      setUser({
        id: storedUser,
        username: localStorage.getItem('username')
      });
    }
    setLoading(false);
  }, []);

  const login = async (credentials) => {
    try {
      if (!credentials.username || !credentials.password) {
        throw new Error('Username and password are required');
      }
  
      const response = await fetch('https://ai-powered-goal-tracker.onrender.com/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(credentials)
      });
  
      const data = await response.json();
  
      if (!data.success) {
        throw new Error(data.detail || 'Login failed');
      }
  
      const userData = {
        id: data.user_id.toString(),
        username: data.username
      };
  
      setUser(userData);
      localStorage.setItem('user_id', userData.id);
      localStorage.setItem('username', userData.username);
      return true;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await fetch('https://ai-powered-goal-tracker.onrender.com/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } finally {
      setUser(null);
      localStorage.removeItem('user_id');
      localStorage.removeItem('username');
      navigate('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};