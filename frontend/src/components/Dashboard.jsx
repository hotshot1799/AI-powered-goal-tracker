import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LogOut, Trash2, Eye, ExternalLink } from 'lucide-react';
import { AddGoalModal } from '@/components/AddGoalModal';
import { useAlert } from '@/context/AlertContext';
import LoadingSpinner from '@/components/LoadingSpinner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

const Dashboard = () => {
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, goalId: null });
  const navigate = useNavigate();
  const { showAlert } = useAlert();
  const userId = localStorage.getItem('user_id');

  const fetchGoals = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!userId || !token) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/goals/user/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'include'
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
      }
    } catch (error) {
      showAlert(error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userId, navigate, showAlert]);

  const fetchSuggestions = useCallback(async () => {
    const token = localStorage.getItem('token');
    if (!userId || !token) return;
  
    try {
      const response = await fetch(`${API_URL}/goals/suggestions/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      });
  
      if (!response.ok) {
        console.error('Suggestions response:', await response.text());
        throw new Error('Failed to fetch suggestions');
      }
  
      const data = await response.json();
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([
        "Start by creating your first goal",
        "Break down your goals into manageable tasks",
        "Track your progress regularly"
      ]);
    }
  }, [userId]);

  const handleDelete = async (goalId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch(`${API_URL}/goals/${goalId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to delete goal');
      }

      const data = await response.json();
      if (data?.success) {
        showAlert('Goal deleted successfully', 'success');
        await fetchGoals();
      }
    } catch (error) {
      showAlert(error.message, 'error');
    } finally {
      setDeleteDialog({ open: false, goalId: null });
    }
  };

  const handleLogout = async () => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        },
        credentials: 'include'
      });
      localStorage.clear();
      navigate('/login');
    } catch (error) {
      showAlert('Failed to logout', 'error');
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
  
      try {
        const authResponse = await fetch(`${API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json'
          },
          credentials: 'include'
        });
  
        if (!authResponse.ok) {
          throw new Error('Authentication failed');
        }
  
        // Fetch data sequentially instead of using Promise.all
        await fetchGoals();
        await fetchSuggestions();
        
      } catch (error) {
        console.error('Auth error:', error);
        localStorage.clear();
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
  
    checkAuth();
  }, [fetchGoals, fetchSuggestions, navigate]);

  const renderGoalCard = (goal) => {
    const progressColor = goal.progress >= 70 ? 'bg-green-100 text-green-800' :
                         goal.progress >= 30 ? 'bg-yellow-100 text-yellow-800' :
                         'bg-red-100 text-red-800';

    return (
      <Card key={goal.id} className="p-6 hover:shadow-lg transition-shadow duration-200">
        <div className="flex justify-between items-start mb-4">
          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
            {goal.category}
          </span>
          <span className={`inline-block px-3 py-1 rounded-full text-sm ${progressColor}`}>
            {goal.progress || 0}% Complete
          </span>
        </div>
        
        <h3 className="font-semibold text-lg mb-2 text-gray-800">
          {goal.description}
        </h3>
        
        <div className="text-sm text-gray-500 mb-4">
          Target Date: {new Date(goal.target_date).toLocaleDateString()}
        </div>
        
        <div className="flex justify-between gap-2 mt-4">
          <Button
            variant="outline"
            onClick={() => navigate(`/goal/${goal.id}`)}
            className="flex-1"
          >
            <Eye className="w-4 h-4 mr-2" /> View Details
          </Button>
          <Button
            variant="destructive"
            onClick={() => setDeleteDialog({ open: true, goalId: goal.id })}
            className="flex-1"
          >
            <Trash2 className="w-4 h-4 mr-2" /> Delete
          </Button>
        </div>
      </Card>
    );
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Goal Dashboard</h1>
          <p className="text-gray-600 mt-2">Track and manage your personal goals</p>
        </div>
        <div className="flex gap-4">
          <AddGoalModal onGoalAdded={fetchGoals} />
          <Button variant="outline" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </div>

      {/* AI Suggestions */}
      <Card className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-indigo-50">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">AI Suggestions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {suggestions.map((suggestion, index) => (
            <div key={index} className="bg-white p-4 rounded-lg shadow-sm">
              <p className="text-gray-700">{suggestion}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Goals Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {goals.length === 0 ? (
          <div className="col-span-full text-center py-12 bg-white rounded-lg">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Goals Yet</h3>
            <p className="text-gray-500 mb-4">Create your first goal to start tracking your progress</p>
            <AddGoalModal onGoalAdded={fetchGoals} />
          </div>
        ) : (
          goals.map(renderGoalCard)
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialog.open} onOpenChange={(open) => setDeleteDialog({ open, goalId: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Goal</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this goal? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialog({ open: false, goalId: null })}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => handleDelete(deleteDialog.goalId)}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Dashboard;