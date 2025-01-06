import React, { useState } from 'react';
import { useAlert } from '../../context/AlertContext';

const AddGoalModal = ({ isOpen, onClose, onGoalAdded }) => {
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    target_date: ''
  });
  const { showAlert } = useAlert();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/v1/goals/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
        credentials: 'include'
      });

      const data = await response.json();
      if (data.success) {
        showAlert('Goal created successfully!');
        onGoalAdded(data.goal);
        onClose();
        setFormData({ category: '', description: '', target_date: '' });
      } else {
        throw new Error(data.detail || 'Failed to create goal');
      }
    } catch (error) {
      showAlert(error.message, 'error');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Add New Goal</h2>
          <span className="close" onClick={onClose}>&times;</span>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="category">Category</label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              required
            >
              <option value="">Select a category</option>
              <option value="Health">Health</option>
              <option value="Career">Career</option>
              <option value="Education">Education</option>
              <option value="Finance">Finance</option>
              <option value="Personal">Personal</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows={3}
            />
          </div>
          <div className="form-group">
            <label htmlFor="target_date">Target Date</label>
            <input
              type="date"
              id="target_date"
              name="target_date"
              value={formData.target_date}
              onChange={handleChange}
              required
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div className="modal-footer">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Goal
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddGoalModal;
