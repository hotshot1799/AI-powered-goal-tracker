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

  const login = async (username, password) => {
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        });

        // ✅ Log the full response
        console.log("Raw Response:", response);

        // ✅ Ensure response is not empty
        const text = await response.text();
        console.log("Response Text:", text);

        if (!response.ok) {
            throw new Error(`HTTP Error ${response.status}: ${text}`);
        }

        // ✅ Parse JSON only if text is not empty
        const data = text ? JSON.parse(text) : null;

        if (data?.success) {
            setUser({
                id: data.user_id?.toString() || "",  
                username: data.username
            });

            localStorage.setItem('user_id', data.user_id?.toString() || "");  
            localStorage.setItem('username', data.username);
            sessionStorage.setItem('user_id', data.user_id?.toString() || "");
            sessionStorage.setItem('username', data.username);
        } else {
            throw new Error(data?.detail || "Login failed");
        }
    } catch (error) {
        console.error("Login error:", error.message);
    }
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