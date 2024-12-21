import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAlert } from '../../context/AlertContext';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const { login } = useAuth();
  const { showAlert } = useAlert();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
        credentials: 'include'
      });

      const data = await response.json();
      if (data.success) {
        login(data);
        showAlert('Login successful!');
        navigate('/dashboard');
      } else {
        throw new Error(data.detail || 'Login failed');
      }
    } catch (error) {
      showAlert(error.message, 'error');
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Username</label>
          <input
            type="text"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
          />
        </div>
        <button type="submit" className="login-btn">Login</button>
      </form>
    </div>
  );
};
