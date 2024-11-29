import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useAlert } from '../../context/AlertContext';

const GoalDetails = () => {
  const { goalId } = useParams();
  const { user } = useAuth();
  const { showAlert } = useAlert();
  const navigate = useNavigate();
  const [goal, setGoal] = useState(null);
  const [progressUpdates, setProgressUpdates] = useState([]);
  const [newUpdate, setNewUpdate] = useState('');
  const [loading, setLoading] = useState(true);

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
      const response = await fetch(`/api/v1/goals/${goalId}`, {
        credentials: 'include'
      });
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
      const response = await fetch(`/api/v1/progress/${goalId}`, {
        credentials: 'include'
      });
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
    if (!newUpdate.trim()) return;

    try {
      const response = await fetch(`/api/v1/progress/${goalId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ update_text: newUpdate }),
        credentials: 'include'
      });

      const data = await response.json();
      if (data.success) {
        showAlert('Progress update added successfully');
        setNewUpdate('');
        await fetchProgressUpdates();
      } else {
        throw new Error(data.detail || 'Failed to add progress update');
      }
    } catch (error) {
      showAlert(error.message, 'error');
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="goal-details-container">
      <div className="goal-header">
        <h1>{goal?.description}</h1>
        <div className="goal-meta">
          <span>Category: {goal?.category}</span>
          <span>Target Date: {new Date(goal?.target_date).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="progress-update-form">
        <h2>Add Progress Update</h2>
        <form onSubmit={handleSubmitUpdate}>
          <div className="form-group">
            <textarea
              value={newUpdate}
              onChange={(e) => setNewUpdate(e.target.value)}
              placeholder="Describe your progress..."
              rows={4}
            />
          </div>
          <button type="submit" className="submit-btn">Add Update</button>
        </form>
      </div>

      <div className="progress-history">
        <h2>Progress History</h2>
        {progressUpdates.length === 0 ? (
          <p className="no-updates">No progress updates yet</p>
        ) : (
          <div className="updates-list">
            {progressUpdates.map((update, index) => (
              <div key={index} className="update-card">
                <div className="update-header">
                  <span className="progress-value">{update.progress}% Complete</span>
                  <span className="update-date">
                    {new Date(update.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="update-text">{update.text}</p>
                {update.analysis && (
                  <div className="analysis">
                    <h4>AI Analysis</h4>
                    <p>{update.analysis}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GoalDetails;
