import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut, LineChart, Trash2, Edit } from 'lucide-react';
import { AddGoalModal } from './AddGoalModal';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGoals();
    fetchSuggestions();
  }, []);

  const fetchGoals = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const response = await fetch(`/api/v1/goals/user/${userId}`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        setGoals(data.goals);
      } else {
        throw new Error(data.detail || 'Failed to fetch goals');
      }
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      const response = await fetch(`/api/v1/goals/suggestions/${userId}`, {
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        setSuggestions(data.suggestions);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const handleDeleteGoal = async (goalId) => {
    if (!confirm('Are you sure you want to delete this goal?')) return;
    
    try {
      const response = await fetch(`/api/v1/goals/${goalId}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        setGoals(goals.filter(goal => goal.id !== goalId));
      }
    } catch (error) {
      console.error('Error deleting goal:', error);
    }
  };

  const getProgressColor = (progress) => {
    if (progress < 30) return 'bg-red-500';
    if (progress < 70) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Goal Dashboard</h1>
        <div className="flex gap-4">
          <AddGoalModal onGoalAdded={(newGoal) => {
            setGoals(prev => [...prev, newGoal]);
          }} />
          <Button variant="outline" onClick={() => window.location.href = '/logout'}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </div>

      {/* AI Insights & Suggestions */}
      <Card className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            AI Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {suggestions.length === 0 ? (
              <div className="col-span-3 text-center py-4">
                <p className="text-gray-500">Create your first goal to get AI-powered suggestions!</p>
              </div>
            ) : (
              suggestions.map((suggestion, index) => (
                <Card key={index} className="border border-blue-100 shadow-sm">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          {index === 0 ? '🎯' : index === 1 ? '📈' : '💡'}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-700 leading-relaxed">{suggestion}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.map(goal => (
          <Card key={goal.id} className="relative">
            <CardHeader>
              <div className="flex justify-between items-center">
                <span className="px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                  {goal.category}
                </span>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => handleDeleteGoal(goal.id)}>
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Edit className="h-4 w-4 text-blue-500" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 mb-4">{goal.description}</p>
              <div className="space-y-2">
                <div className="flex justify-between text-sm text-gray-500">
                  <span>Progress</span>
                  <span>{goal.progress}%</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full">
                  <div 
                    className={`h-full rounded-full ${getProgressColor(goal.progress)}`}
                    style={{ width: `${goal.progress}%` }}
                  ></div>
                </div>
                <div className="flex justify-between items-center mt-4">
                  <span className="text-sm text-gray-500">
                    Target: {new Date(goal.target_date).toLocaleDateString()}
                  </span>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => window.location.href = `/goal/${goal.id}`}
                  >
                    <LineChart className="mr-2 h-4 w-4" />
                    Details
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;