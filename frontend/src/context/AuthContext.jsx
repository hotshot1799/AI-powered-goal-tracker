import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user data exists in localStorage
    const storedUser = localStorage.getItem('user_id');
    if (storedUser) {
      setUser({
        id: localStorage.getItem('user_id'),
        username: localStorage.getItem('username')
      });
    }
    setLoading(false);
  }, []);

  const login = (userData) => {
    const userInfo = {
      id: userData.user_id,
      username: userData.username
    };
    setUser(userInfo);
    localStorage.setItem('user_id', userData.user_id.toString());
    localStorage.setItem('username', userData.username);
  };

  const logout = async () => {
    try {
      const response = await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      
      if (response.ok) {
        setUser(null);
        localStorage.removeItem('user_id');
        localStorage.removeItem('username');
      }
    } catch (error) {
      console.error('Logout error:', error);
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
  if (context === null) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};