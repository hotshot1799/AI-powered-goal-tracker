import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAlert } from '@/context/AlertContext';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowLeft } from 'lucide-react';

const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

const GoalDetails = () => {
  const { goalId } = useParams();
  const navigate = useNavigate();
  const { showAlert } = useAlert();
  const [goal, setGoal] = useState(null);
  const [progressUpdates, setProgressUpdates] = useState([]);
  const [newUpdate, setNewUpdate] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchGoalDetails();
    fetchProgressUpdates();
  }, [goalId]);

  const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    };
  };

  const fetchGoalDetails = async () => {
    try {
      const response = await fetch(`${API_URL}/goals/${goalId}`, {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to fetch goal details');
      }

      const data = await response.json();
      if (data.success) {
        setGoal(data.goal);
      } else {
        throw new Error(data.detail || 'Failed to fetch goal details');
      }
    } catch (error) {
      console.error('Error fetching goal details:', error);
      showAlert('Failed to fetch goal details', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressUpdates = async () => {
    try {
      const response = await fetch(`${API_URL}/progress/${goalId}`, {
        method: 'GET',
        headers: getAuthHeaders(),
        credentials: 'include'
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          return;
        }
        throw new Error('Failed to fetch progress updates');
      }

      const data = await response.json();
      if (data.success) {
        setProgressUpdates(data.updates || []);
      }
    } catch (error) {
      console.error('Error fetching progress updates:', error);
      showAlert('Failed to fetch progress updates', 'error');
    }
  };

  const handleSubmitUpdate = async (e) => {
    e.preventDefault();
    if (!newUpdate.trim() || submitting) return;

    setSubmitting(true);
    try {
      const response = await fetch(`${API_URL}/progress/${goalId}`, {
        method: 'POST',
        headers: getAuthHeaders(),
        credentials: 'include',
        body: JSON.stringify({ update_text: newUpdate })
      });

      if (!response.ok) {
        throw new Error('Failed to add progress update');
      }

      const data = await response.json();
      if (data.success) {
        setNewUpdate('');
        await fetchProgressUpdates();
        showAlert('Progress update added successfully', 'success');
      }
    } catch (error) {
      console.error('Error adding progress update:', error);
      showAlert('Failed to add progress update', 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button 
                variant="ghost" 
                onClick={() => navigate('/dashboard')}
                className="flex items-center text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Dashboard
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <Card className="mb-8">
          <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">{goal?.description}</h2>
            <div className="flex items-center gap-4 mb-6">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                {goal?.category}
              </span>
              <span className="text-gray-600">
                Target Date: {goal?.target_date ? new Date(goal.target_date).toLocaleDateString() : 'Not set'}
              </span>
            </div>

            <form onSubmit={handleSubmitUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Add Progress Update
                </label>
                <Textarea
                  value={newUpdate}
                  onChange={(e) => setNewUpdate(e.target.value)}
                  placeholder="Describe your progress..."
                  className="min-h-[100px]"
                />
              </div>
              <Button 
                type="submit" 
                disabled={submitting}
                className="w-full sm:w-auto"
              >
                {submitting ? 'Adding Update...' : 'Add Update'}
              </Button>
            </form>
          </div>
        </Card>

        <Card>
          <div className="p-6">
            <h3 className="text-xl font-semibold mb-4">Progress History</h3>
            {progressUpdates.length === 0 ? (
              <p className="text-gray-500 text-center py-4">
                No progress updates yet
              </p>
            ) : (
              <div className="space-y-4">
                {progressUpdates.map((update, index) => (
                  <div 
                    key={index} 
                    className="p-4 bg-gray-50 rounded-lg border border-gray-100"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-semibold text-sm">
                        Progress: {update.progress}%
                      </span>
                      <span className="text-sm text-gray-500">
                        {new Date(update.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p className="text-gray-700">{update.text}</p>
                    {update.analysis && (
                      <div className="mt-2 p-2 bg-blue-50 rounded">
                        <p className="text-sm text-blue-800">{update.analysis}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default GoalDetails;