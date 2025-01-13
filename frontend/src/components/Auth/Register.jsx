import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAlert } from '@/context/AlertContext';
// Import styled components
import {
  BoxContainer,
  FormContainer,
  Input,
  LineText,
  BoldLink,
  SubmitButton,
} from "./common";

const Register = () => {
  // Keep your existing state and hooks
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { showAlert } = useAlert();

  // Keep your existing handleSubmit function
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          email: formData.email,
          password: formData.password
        }),
        credentials: 'include'
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        showAlert('Registration successful! Please log in.');
        navigate('/login');
      } else {
        throw new Error(data.detail || 'Registration failed');
      }
    } catch (error) {
      setError(error.message || 'Registration failed. Please try again.');
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
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value.trim() })}
            required
          />
          
          <Input 
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value.trim() })}
            required
          />
          
          <Input 
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
            minLength={6}
          />
          
          <Input 
            type="password"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            required
            minLength={6}
          />
          
          <SubmitButton 
            type="submit" 
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </SubmitButton>
          
          <LineText>
            Already have an account?{" "}
            <BoldLink href="/login">
              Sign in
            </BoldLink>
          </LineText>
        </FormContainer>
      </BoxContainer>
    </div>
  );
};

export default Register;