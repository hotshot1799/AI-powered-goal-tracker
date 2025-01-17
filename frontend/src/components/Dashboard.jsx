import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut } from 'lucide-react';
import { AddGoalModal } from '@/components/AddGoalModal';
import { useAlert } from '@/context/AlertContext';

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { showAlert } = useAlert();

  // Backend API URL
  const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';
  const userId = localStorage.getItem('user_id');

  const fetchGoals = async () => {
    try {
      console.log('Fetching goals for user:', userId);
      const response = await fetch(`${API_URL}/goals/user/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries([...response.headers]));
      
      const text = await response.text();
      console.log('Raw response text:', text);

      if (!text || text.trim() === '') {
        console.error('Received empty response');
        throw new Error('Server returned an empty response');
      }

      try {
        const data = JSON.parse(text);
        console.log('Parsed data:', data);

        if (!response.ok) {
          if (response.status === 401) {
            localStorage.clear();
            navigate('/login');
            return;
          }
          throw new Error(data?.detail || `Server error: ${response.status}`);
        }

        if (data?.success) {
          setGoals(data.goals || []);
        } else {
          throw new Error(data?.detail || 'Failed to fetch goals');
        }
      } catch (parseError) {
        console.error('JSON Parse Error:', parseError);
        console.error('Raw text that failed to parse:', text);
        throw new Error('Invalid response format from server');
      }
    } catch (error) {
      console.error('Error in fetchGoals:', error);
      setError(error.message || 'Failed to load goals');
      showAlert(error.message || 'Failed to load goals', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async () => {
    if (!userId) {
      console.warn('No user ID found, skipping suggestions fetch');
      return;
    }
  
    try {
      console.log('Fetching suggestions for user:', userId);
      const response = await fetch(`${API_URL}/goals/suggestions/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
  
      console.log('Suggestions response status:', response.status);
      
      const text = await response.text();
      console.log('Raw suggestions response:', text);
  
      if (!text) {
        throw new Error('Empty response from server');
      }

      const data = JSON.parse(text);
      console.log('Parsed suggestions response:', data);
  
      if (!response.ok) {
        if (response.status === 401) {
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
      setSuggestions([
        "Start by creating your first goal",
        "Break down your goals into manageable tasks",
        "Track your progress regularly"
      ]);
    }
  };

  const handleAddGoal = async (goalData) => {
    try {
      console.log('Making request to:', 'https://ai-powered-goal-tracker.onrender.com/api/v1/goals/create');
      const response = await fetch('https://ai-powered-goal-tracker.onrender.com/api/v1/goals/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(goalData)
      });
  
      console.log('Response status:', response.status);
      console.log('Response URL:', response.url);  // This will show us the actual URL being used
  
      const text = await response.text();
      console.log('Raw add goal response:', text);
  
      if (!text) {
        throw new Error('Empty response from server');
      }
  
      const data = JSON.parse(text);
      console.log('Parsed goal response:', data);
  
      if (response.status === 201 && data?.success) {
        setGoals(prev => [...prev, data.goal]);
        showAlert('Goal created successfully!', 'success');
        return data.goal;
      } else {
        throw new Error(data?.detail || 'Failed to create goal');
      }
    } catch (error) {
      console.error('Error creating goal:', error);
      showAlert(error.message || 'Failed to create goal', 'error');
      throw error;
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      if (!userId) {
        navigate('/login');
        return;
      }
  
      try {
        const response = await fetch(`${API_URL}/auth/me`, {
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
  
        const text = await response.text();
        console.log('Auth check response:', text);

        if (!text) {
          throw new Error('Empty response from server');
        }

        const data = JSON.parse(text);

        if (!response.ok || !data?.success) {
          localStorage.clear();
          navigate('/login');
          return;
        }
  
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

  const handleLogout = async () => {
    try {
      const response = await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      const text = await response.text();
      console.log('Logout response:', text);

      if (!text) {
        throw new Error('Empty response from server');
      }

      const data = JSON.parse(text);

      if (data?.success) {
        localStorage.clear();
        navigate('/login');
      } else {
        throw new Error(data?.detail || 'Logout failed');
      }
    } catch (error) {
      console.error('Logout error:', error);
      showAlert('Failed to logout', 'error');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Goal Dashboard</h1>
        <div className="flex gap-4">
          <AddGoalModal onGoalAdded={handleAddGoal} />
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
            <AddGoalModal onGoalAdded={handleAddGoal} />
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