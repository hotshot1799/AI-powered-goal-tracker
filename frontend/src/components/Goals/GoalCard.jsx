import React from 'react';
import { useNavigate } from 'react-router-dom';

const GoalCard = ({ goal, onDelete, onEdit }) => {
  const navigate = useNavigate();
  const progressColor = getProgressColor(goal.progress || 0);

  return (
    <div className="goal-card">
      <div className="goal-card-header" style={{ borderLeft: `4px solid ${progressColor}` }}>
        <div className="goal-category">{goal.category}</div>
        <div className="goal-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${goal.progress || 0}%`, backgroundColor: progressColor }}
            />
          </div>
          <span>{goal.progress || 0}%</span>
        </div>
      </div>
      <div className="goal-description">{goal.description}</div>
      <div className="goal-meta">
        <span>
          <i className="fas fa-calendar"></i> 
          {new Date(goal.target_date).toLocaleDateString()}
        </span>
      </div>
      <div className="goal-actions">
        <button onClick={() => navigate(`/goal/${goal.id}`)} className="action-button">
          <i className="fas fa-chart-line"></i> Track Progress
        </button>
        <button onClick={() => onEdit(goal)} className="action-button">
          <i className="fas fa-edit"></i> Edit
        </button>
        <button onClick={() => onDelete(goal.id)} className="action-button delete">
          <i className="fas fa-trash"></i> Delete
        </button>
      </div>
    </div>
  );
};
