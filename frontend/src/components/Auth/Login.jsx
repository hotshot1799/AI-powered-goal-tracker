// Login.jsx 
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
// Import styled components
import {
  BoxContainer,
  FormContainer,
  Input,
  LineText,
  MutedLink,
  BoldLink,
  SubmitButton,
} from "./common";

const Login = () => {
  // Keep your existing state and hooks
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  // Keep your existing handleSubmit function
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
        credentials: 'include'
      });

      const data = await response.json();
      
      if (response.ok && data?.success) {
        login(data);
        navigate('/dashboard');
      } else {
        throw new Error(data?.detail || 'Login failed');
      }
    } catch (error) {
      setError(error.message || 'Failed to log in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
      <BoxContainer>
        <FormContainer onSubmit={handleSubmit}>
          {error && (
            <div className="p-3 rounded bg-red-50 text-red-500 text-sm mb-4">
              {error}
            </div>
          )}
          
          <Input 
            type="text"
            placeholder="Username"
            value={credentials.username}
            onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
            required
          />
          
          <Input 
            type="password"
            placeholder="Password"
            value={credentials.password}
            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
            required
          />

          <MutedLink href="#">Forgot your password?</MutedLink>
          
          <SubmitButton 
            type="submit" 
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </SubmitButton>
          
          <LineText>
            Don't have an account?{" "}
            <BoldLink href="/register">
              Sign up
            </BoldLink>
          </LineText>
        </FormContainer>
      </BoxContainer>
    </div>
  );
};

export default Login;