import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import ProtectedRoute from './components/ProtectedRoute';

// Lazy load components
const Login = React.lazy(() => import('./components/Auth/Login'));
const Register = React.lazy(() => import('./components/Auth/Register'));
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const GoalDetails = React.lazy(() => import('./components/Goals/GoalDetails'));

const App = () => {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <AlertProvider>
            <Suspense fallback={<LoadingSpinner />}>
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
            </Suspense>
          </AlertProvider>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
};

export default App;