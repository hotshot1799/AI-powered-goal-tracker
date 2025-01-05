import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AlertProvider } from './context/AlertContext';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import ProtectedRoute from './components/ProtectedRoute';
import Dashboard from './components/Dashboard';

// Lazy load components for better performance
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
                <Route 
                  path="/" 
                  element={<Navigate to="/dashboard" replace />} 
                />

                {/* 404 route */}
                <Route 
                  path="*" 
                  element={
                    <div className="not-found">
                      <h1>404 - Page Not Found</h1>
                      <p>The page you're looking for doesn't exist.</p>
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
