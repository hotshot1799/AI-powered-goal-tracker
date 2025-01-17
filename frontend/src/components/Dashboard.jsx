import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut } from 'lucide-react';
import { AddGoalModal } from '@/components/AddGoalModal';
import { useAlert } from '@/context/AlertContext';
import LoadingSpinner from '@/components/LoadingSpinner';

const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { showAlert } = useAlert();
  const userId = localStorage.getItem('user_id');

  const fetchGoals = useCallback(async () => {
    if (!userId) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/goals/user/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.clear();
          navigate('/login');
          return;
        }
        throw new Error('Failed to fetch goals');
      }

      const data = await response.json();
      if (data?.success) {
        setGoals(data.goals || []);
      } else {
        throw new Error(data?.detail || 'Failed to fetch goals');
      }
    } catch (error) {
      showAlert(error.message, 'error');
    }
  }, [userId, navigate, showAlert]);

  const fetchSuggestions = useCallback(async () => {
    if (!userId) return;

    try {
      const response = await fetch(`${API_URL}/goals/suggestions/${userId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch suggestions');
      }

      const data = await response.json();
      if (data?.success) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      setSuggestions([
        "Start by creating your first goal",
        "Break down your goals into manageable tasks",
        "Track your progress regularly"
      ]);
    }
  }, [userId]);

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

        if (!response.ok) {
          throw new Error('Authentication failed');
        }

        const data = await response.json();
        if (!data?.success) {
          throw new Error('Authentication failed');
        }

        await Promise.all([fetchGoals(), fetchSuggestions()]);
      } catch (error) {
        localStorage.clear();
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, [userId, navigate, fetchGoals, fetchSuggestions]);

  const handleAddGoal = async (goalData) => {
    try {
      const response = await fetch(`${API_URL}/goals/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(goalData)
      });

      if (!response.ok) {
        throw new Error('Failed to create goal');
      }

      const data = await response.json();
      if (data?.success) {
        showAlert('Goal created successfully!', 'success');
        await fetchGoals(); // Fetch fresh goals instead of updating state directly
        return data.goal;
      } else {
        throw new Error(data?.detail || 'Failed to create goal');
      }
    } catch (error) {
      showAlert(error.message, 'error');
      throw error;
    }
  };

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

      const data = await response.json();
      if (data?.success) {
        localStorage.clear();
        navigate('/login');
      } else {
        throw new Error(data?.detail || 'Logout failed');
      }
    } catch (error) {
      showAlert('Failed to logout', 'error');
    }
  };

  if (loading) {
    return <LoadingSpinner />;
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