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
} from "@/components/Auth/common";

const Register = () => {
  // State for form data, loading, and error
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

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Send registration request to the server
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

      // Log the response for debugging
      console.log('Response:', response);

      // Get the response as text first
      const text = await response.text();
      console.log('Response Text:', text); // Log the response text

      // Check if the response is OK (status code 200-299)
      if (!response.ok) {
        // If the response is not OK, throw an error with the status code
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Attempt to parse the response text as JSON
      let data;
      try {
        data = JSON.parse(text);
      } catch (jsonError) {
        // If parsing fails, throw an error
        throw new Error('Invalid JSON response from server');
      }

      // Check if registration was successful
      if (data.success) {
        showAlert('Registration successful! Please log in.');
        navigate('/login');
      } else {
        throw new Error(data.detail || 'Registration failed');
      }
    } catch (error) {
      // Handle errors
      setError(error.message || 'Registration failed. Please try again.');
    } finally {
      // Reset loading state
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50">
      <BoxContainer>
        <FormContainer onSubmit={handleSubmit}>
          {/* Display error message if any */}
          {error && (
            <div className="p-3 rounded bg-red-50 text-red-500 text-sm mb-4">
              {error}
            </div>
          )}
          
          {/* Username Input */}
          <Input 
            type="text"
            placeholder="Username"
            value={formData.username}
            onChange={(e) => setFormData({ ...formData, username: e.target.value.trim() })}
            required
          />
          
          {/* Email Input */}
          <Input 
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value.trim() })}
            required
          />
          
          {/* Password Input */}
          <Input 
            type="password"
            placeholder="Password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
            minLength={6}
          />
          
          {/* Confirm Password Input */}
          <Input 
            type="password"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            required
            minLength={6}
          />
          
          {/* Submit Button */}
          <SubmitButton 
            type="submit" 
            disabled={loading}
          >
            {loading ? 'Creating Account...' : 'Sign Up'}
          </SubmitButton>
          
          {/* Link to Login Page */}
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