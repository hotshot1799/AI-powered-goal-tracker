import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { LogIn, User, Lock, ArrowRight } from 'lucide-react';

const Login = () => {
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(credentials),
        credentials: 'include',
      });

      const text = await response.text();
      console.log('Raw response:', text);

      if (!text) {
        throw new Error('Empty response from server');
      }

      const data = JSON.parse(text);
      
      if (data?.success) {
        login(data);
        navigate('/dashboard');
      } else {
        throw new Error(data?.detail || 'Login failed');
      }
    } catch (error) {
      console.error('Detailed error:', error);
      setError(error.message || 'Failed to log in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md transform transition-all duration-300 ease-in-out">
        <Card className="backdrop-blur-sm bg-white/90 shadow-2xl rounded-xl hover:shadow-xl transition-all duration-300">
          <CardHeader className="space-y-1 pb-0">
            <div className="flex justify-center mb-6 mt-2">
              <div className="bg-indigo-600 p-4 rounded-full shadow-lg transform transition-transform duration-300 hover:scale-105">
                <LogIn className="h-6 w-6 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold text-center text-gray-800">
              Welcome Back
            </CardTitle>
            <CardDescription className="text-center text-gray-600">
              Sign in to continue to your goals
            </CardDescription>
          </CardHeader>

          <CardContent className="pt-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 text-red-600 p-4 rounded-lg text-sm font-medium border-l-4 border-red-500 animate-fadeIn">
                  {error}
                </div>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="username" className="text-gray-700 font-medium">
                  Username
                </Label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors duration-200" />
                  </div>
                  <Input
                    id="username"
                    name="username"
                    type="text"
                    placeholder="Enter your username"
                    value={credentials.username}
                    onChange={handleInputChange}
                    className="pl-10 h-12 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 bg-white/50 backdrop-blur-sm transition-all duration-200"
                    autoComplete="username"
                    disabled={loading}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 font-medium">
                  Password
                </Label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors duration-200" />
                  </div>
                  <Input
                    id="password"
                    name="password"
                    type="password"
                    placeholder="Enter your password"
                    value={credentials.password}
                    onChange={handleInputChange}
                    className="pl-10 h-12 rounded-lg border-gray-200 focus:border-indigo-500 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 bg-white/50 backdrop-blur-sm transition-all duration-200"
                    autoComplete="current-password"
                    disabled={loading}
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transform transition-all duration-200 hover:-translate-y-0.5"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Signing in...
                  </span>
                ) : (
                  <span className="flex items-center justify-center">
                    Sign in
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </span>
                )}
              </Button>
            </form>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4 pb-6">
            <div className="relative w-full">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">
                  New to Goal Tracker?
                </span>
              </div>
            </div>
            <Link 
              to="/register" 
              className="inline-flex items-center justify-center text-indigo-600 hover:text-indigo-800 font-medium transition-colors duration-200"
            >
              Create an account
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </CardFooter>
        </Card>

        {/* Floating decoration elements */}
        <div className="absolute top-20 left-10 w-20 h-20 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
        <div className="absolute top-20 right-10 w-20 h-20 bg-yellow-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-20 h-20 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
      </div>
    </div>
  );
};

export default Login;