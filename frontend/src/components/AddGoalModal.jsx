import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Plus } from 'lucide-react';

const AddGoalModal = ({ onGoalAdded }) => {
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    category: '',
    description: '',
    target_date: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('Submitting goal:', formData);
      
      const response = await fetch('https://ai-powered-goal-tracker.onrender.com/api/v1/goals/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(formData),
        credentials: 'include'
      });

      console.log('Response status:', response.status);
      console.log('Response URL:', response.url);

      const text = await response.text();
      console.log('Raw response:', text);

      if (!text) {
        throw new Error('Empty response from server');
      }

      try {
        const data = JSON.parse(text);
        console.log('Parsed data:', data);

        if (response.status === 201 && data?.success) {
          await onGoalAdded(data.goal);
          setOpen(false);
          setFormData({
            category: '',
            description: '',
            target_date: ''
          });
        } else {
          throw new Error(data?.detail || 'Failed to create goal');
        }
      } catch (parseError) {
        console.error('JSON Parse Error:', parseError);
        console.error('Raw text that failed to parse:', text);
        throw new Error('Invalid server response');
      }
    } catch (error) {
      console.error('Error creating goal:', error);
      setError(error.message || 'Failed to create goal');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    if (error) setError('');
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <Button 
        onClick={() => setOpen(true)}
        className="bg-blue-500 hover:bg-blue-600"
      >
        <Plus className="mr-2 h-4 w-4" /> Add Goal
      </Button>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Create New Goal</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="category">Category</Label>
              <Select
                onValueChange={(value) => handleChange('category', value)}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Health">Health</SelectItem>
                  <SelectItem value="Career">Career</SelectItem>
                  <SelectItem value="Education">Education</SelectItem>
                  <SelectItem value="Finance">Finance</SelectItem>
                  <SelectItem value="Personal">Personal</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Describe your goal..."
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                required
                className="h-24"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="target_date">Target Date</Label>
              <Input
                id="target_date"
                type="date"
                value={formData.target_date}
                onChange={(e) => handleChange('target_date', e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                required
              />
            </div>
          </div>

          {error && (
            <div className="text-red-500 text-sm">{error}</div>
          )}

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Goal'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export { AddGoalModal };