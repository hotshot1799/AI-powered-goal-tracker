import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => ({
    id: localStorage.getItem('user_id'),
    username: localStorage.getItem('username')
  }));

  const login = (userData) => {
    localStorage.setItem('user_id', userData.user_id.toString());
    localStorage.setItem('username', userData.username);
    setUser({ id: userData.user_id, username: userData.username });
  };

  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        credentials: 'include'
      });
      localStorage.clear();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
