import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Log the authentication state and location
  console.log('[ProtectedRoute]: Rendering component');
  console.log('[ProtectedRoute]: Auth state:', { user, loading });
  console.log('[ProtectedRoute]: Current location:', location);

  if (loading) {
    console.log('[ProtectedRoute]: Loading user authentication...');
    return <LoadingSpinner />;
  }

  if (!user) {
    console.log('[ProtectedRoute]: User is not authenticated. Redirecting to login.');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('[ProtectedRoute]: User is authenticated. Rendering children.');
  return <>{children}</>; // Ensure this is valid JSX
};

export default ProtectedRoute;