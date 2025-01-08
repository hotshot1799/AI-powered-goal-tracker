import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';

// Regular imports instead of lazy loading for core components
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Dashboard from './components/Dashboard';
import GoalDetails from './components/Goals/GoalDetails';
import ProtectedRoute from './components/ProtectedRoute';

const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <AlertProvider>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />

              {/* Protected routes */}
              <Route 
                path="/dashboard" 
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/goal/:goalId" 
                element={
                  <ProtectedRoute>
                    <GoalDetails />
                  </ProtectedRoute>
                } 
              />

              {/* Redirect root to dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />

              {/* 404 route */}
              <Route
                path="*"
                element={
                  <div className="flex min-h-screen items-center justify-center">
                    <div className="text-center">
                      <h1 className="text-4xl font-bold text-gray-900">404 - Not Found</h1>
                      <p className="mt-2 text-gray-600">The page you're looking for doesn't exist.</p>
                    </div>
                  </div>
                }
              />
            </Routes>
          </AlertProvider>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
};

export default App;