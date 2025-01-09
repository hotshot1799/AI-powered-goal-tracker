import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut } from 'lucide-react';
import { AddGoalModal } from '@/components/Goals/AddGoalModal';

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const API_URL = import.meta.env.VITE_API_URL;
  const userId = localStorage.getItem('user_id');

  useEffect(() => {
    const checkAuth = async () => {
      if (!userId) {
        navigate('/login');
        return;
      }
  
      try {
        // Check if session is still valid
        const response = await fetch(`${API_URL}/api/v1/auth/me`, {
          credentials: 'include'
        });
  
        if (!response.ok) {
          // Session expired or invalid
          localStorage.clear();
          navigate('/login');
          return;
        }
  
        // Session is valid, fetch data
        await Promise.all([
          fetchGoals(),
          fetchSuggestions()
        ]);
      } catch (error) {
        console.error('Auth check failed:', error);
        navigate('/login');
      }
    };
  
    checkAuth();
  }, [userId, navigate]);

  const fetchSuggestions = async () => {
    if (!userId) {
      console.warn('No user ID found, skipping suggestions fetch');
      return;
    }
  
    try {
      console.log('Fetching suggestions for user:', userId);
      const response = await fetch(`${API_URL}/api/v1/goals/suggestions/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
  
      console.log('Suggestions response status:', response.status);
  
      // Log response headers for debugging
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
  
      // Get response text first
      const text = await response.text();
      console.log('Raw response:', text);
  
      // Try to parse it
      let data;
      try {
        data = text ? JSON.parse(text) : null;
        console.log('Parsed response:', data);
      } catch (error) {
        console.error('Failed to parse response:', error);
        throw new Error('Invalid response from server');
      }
  
      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthenticated
          localStorage.clear();
          window.location.href = '/login';
          return;
        }
        throw new Error(data?.detail || 'Failed to fetch suggestions');
      }
  
      if (data?.success) {
        setSuggestions(data.suggestions);
      } else {
        throw new Error(data?.detail || 'No suggestions available');
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      // Set default suggestions on error
      setSuggestions([
        "Start by creating your first goal",
        "Break down your goals into manageable tasks",
        "Track your progress regularly"
      ]);
    }
  };

  const fetchGoals = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/goals/user/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch goals');
      }

      const data = await response.json();
      if (data.success) {
        setGoals(data.goals || []);
      }
    } catch (error) {
      console.error('Error fetching goals:', error);
      setError('Failed to load goals');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
      localStorage.clear();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Goal Dashboard</h1>
        <div className="flex gap-4">
          <AddGoalModal onGoalAdded={(newGoal) => {
            setGoals(prev => [...prev, newGoal]);
          }} />
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </div>

      {/* AI Suggestions */}
      <Card className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
        <h2 className="text-xl font-semibold mb-4">AI Suggestions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow">
              <p className="text-gray-700">{suggestion}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.length === 0 ? (
          <div className="col-span-full text-center py-8">
            <p className="text-gray-500 mb-4">No goals yet. Let's create your first goal!</p>
            <AddGoalModal onGoalAdded={(newGoal) => {
              setGoals(prev => [...prev, newGoal]);
            }} />
          </div>
        ) : (
          goals.map(goal => (
            <Card key={goal.id} className="p-6">
              <div className="mb-4">
                <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  {goal.category}
                </span>
              </div>
              <p className="text-gray-700 mb-4">{goal.description}</p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>Target: {new Date(goal.target_date).toLocaleDateString()}</span>
                <span>Progress: {goal.progress || 0}%</span>
              </div>
              <div className="mt-4">
                <Button
                  onClick={() => navigate(`/goal/${goal.id}`)}
                  className="w-full"
                >
                  View Details
                </Button>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default Dashboard;