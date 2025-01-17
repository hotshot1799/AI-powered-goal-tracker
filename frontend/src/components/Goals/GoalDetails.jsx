import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useAlert } from '@/context/AlertContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import LoadingSpinner from '@/components/LoadingSpinner';

const API_URL = 'https://ai-powered-goal-tracker.onrender.com/api/v1';

const GoalDetails = () => {
  const { goalId } = useParams();
  const { user } = useAuth();
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  const [goal, setGoal] = useState(null);
  const [progressUpdates, setProgressUpdates] = useState([]);
  const [newUpdate, setNewUpdate] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchGoalDetails();
    fetchProgressUpdates();
  }, [goalId, user]);

  const fetchGoalDetails = async () => {
    try {
      const response = await fetch(`${API_URL}/goals/${goalId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
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
      showAlert(error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchProgressUpdates = async () => {
    try {
      const response = await fetch(`${API_URL}/progress/${goalId}`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch progress updates');
      }

      const data = await response.json();
      if (data.success) {
        setProgressUpdates(data.updates);
      }
    } catch (error) {
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
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ update_text: newUpdate })
      });

      if (!response.ok) {
        throw new Error('Failed to add progress update');
      }

      const data = await response.json();
      if (data.success) {
        showAlert('Progress update added successfully', 'success');
        setNewUpdate('');
        await fetchProgressUpdates();
      } else {
        throw new Error(data.detail || 'Failed to add progress update');
      }
    } catch (error) {
      showAlert(error.message, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>{goal?.description}</CardTitle>
          <div className="text-sm text-gray-500">
            <span>Category: {goal?.category}</span>
            <span className="mx-2">•</span>
            <span>Target: {new Date(goal?.target_date).toLocaleDateString()}</span>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmitUpdate} className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold mb-2">Add Progress Update</h3>
              <Textarea
                value={newUpdate}
                onChange={(e) => setNewUpdate(e.target.value)}
                placeholder="Describe your progress..."
                className="min-h-[100px]"
                disabled={submitting}
              />
            </div>
            <Button type="submit" disabled={submitting}>
              {submitting ? 'Adding Update...' : 'Add Update'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Progress History</CardTitle>
        </CardHeader>
        <CardContent>
          {progressUpdates.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No progress updates yet</p>
          ) : (
            <div className="space-y-4">
              {progressUpdates.map((update, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-semibold">
                      Progress: {update.progress}%
                    </span>
                    <span className="text-sm text-gray-500">
                      {new Date(update.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-gray-700">{update.text}</p>
                  {update.analysis && (
                    <div className="mt-2 p-2 bg-blue-50 rounded">
                      <h4 className="text-sm font-semibold text-blue-700">AI Analysis</h4>
                      <p className="text-sm text-blue-600">{update.analysis}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GoalDetails;