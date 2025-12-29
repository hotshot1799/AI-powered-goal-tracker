import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
  TextInput,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { goalsAPI, progressAPI } from '../../services/api';
import { format } from 'date-fns';
import Slider from '@react-native-community/slider';

const GoalDetailScreen = ({ route, navigation }) => {
  const { goalId } = route.params;
  const [goal, setGoal] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [progressValue, setProgressValue] = useState(0);
  const [progressNote, setProgressNote] = useState('');
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchGoalDetails();
  }, []);

  const fetchGoalDetails = async () => {
    try {
      const response = await goalsAPI.getGoal(goalId);
      if (response.success) {
        setGoal(response.goal);
        setProgressValue(response.goal.progress || 0);
      }
    } catch (error) {
      console.error('Error fetching goal:', error);
      Alert.alert('Error', 'Failed to fetch goal details');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProgress = async () => {
    setUpdating(true);
    try {
      await progressAPI.addProgress(goalId, {
        progress_value: progressValue,
        note: progressNote || null,
      });

      Alert.alert('Success', 'Progress updated successfully!');
      setShowProgressModal(false);
      setProgressNote('');
      await fetchGoalDetails();
    } catch (error) {
      console.error('Error updating progress:', error);
      Alert.alert('Error', 'Failed to update progress');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteGoal = () => {
    Alert.alert(
      'Delete Goal',
      'Are you sure you want to delete this goal? This action cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await goalsAPI.deleteGoal(goalId);
              Alert.alert('Success', 'Goal deleted successfully');
              navigation.goBack();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete goal');
            }
          },
        },
      ]
    );
  };

  const getProgressColor = (progress) => {
    if (progress >= 70) return '#10B981';
    if (progress >= 30) return '#F59E0B';
    return '#EF4444';
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4F46E5" />
        </View>
      </SafeAreaView>
    );
  }

  if (!goal) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text>Goal not found</Text>
        </View>
      </SafeAreaView>
    );
  }

  const progressColor = getProgressColor(goal.progress || 0);

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scrollView}>
        {/* Goal Header */}
        <View style={styles.header}>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{goal.category}</Text>
          </View>
          <Text style={styles.description}>{goal.description}</Text>
          <View style={styles.dateContainer}>
            <Ionicons name="calendar-outline" size={16} color="#6B7280" />
            <Text style={styles.dateText}>
              Target: {format(new Date(goal.target_date), 'MMM dd, yyyy')}
            </Text>
          </View>
        </View>

        {/* Progress Section */}
        <View style={styles.progressSection}>
          <Text style={styles.sectionTitle}>Progress</Text>
          <View style={styles.progressContainer}>
            <Text style={styles.progressPercentage}>{Math.round(goal.progress || 0)}%</Text>
            <View style={styles.progressBarContainer}>
              <View style={styles.progressBarBackground}>
                <View
                  style={[
                    styles.progressBarFill,
                    {
                      width: `${goal.progress || 0}%`,
                      backgroundColor: progressColor,
                    },
                  ]}
                />
              </View>
            </View>
          </View>
        </View>

        {/* Actions */}
        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.updateButton}
            onPress={() => setShowProgressModal(true)}
          >
            <Ionicons name="trending-up" size={20} color="white" />
            <Text style={styles.updateButtonText}>Update Progress</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.deleteButton} onPress={handleDeleteGoal}>
            <Ionicons name="trash-outline" size={20} color="#EF4444" />
            <Text style={styles.deleteButtonText}>Delete Goal</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Update Progress Modal */}
      <Modal
        visible={showProgressModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowProgressModal(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Update Progress</Text>
              <TouchableOpacity onPress={() => setShowProgressModal(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <View style={styles.sliderContainer}>
              <Text style={styles.sliderLabel}>Progress: {Math.round(progressValue)}%</Text>
              <Slider
                style={styles.slider}
                value={progressValue}
                onValueChange={setProgressValue}
                minimumValue={0}
                maximumValue={100}
                step={1}
                minimumTrackTintColor="#4F46E5"
                maximumTrackTintColor="#E5E7EB"
              />
            </View>

            <TextInput
              style={styles.noteInput}
              placeholder="Add a note (optional)"
              value={progressNote}
              onChangeText={setProgressNote}
              multiline
              numberOfLines={3}
              textAlignVertical="top"
            />

            <TouchableOpacity
              style={styles.saveButton}
              onPress={handleUpdateProgress}
              disabled={updating}
            >
              {updating ? (
                <ActivityIndicator color="white" />
              ) : (
                <Text style={styles.saveButtonText}>Save Progress</Text>
              )}
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    backgroundColor: 'white',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  categoryBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#DBEAFE',
    borderRadius: 12,
    marginBottom: 12,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1D4ED8',
  },
  description: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111',
    marginBottom: 12,
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  dateText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 6,
  },
  progressSection: {
    backgroundColor: 'white',
    padding: 20,
    marginTop: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111',
    marginBottom: 16,
  },
  progressContainer: {
    alignItems: 'center',
  },
  progressPercentage: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#111',
    marginBottom: 16,
  },
  progressBarContainer: {
    width: '100%',
  },
  progressBarBackground: {
    height: 24,
    backgroundColor: '#E5E7EB',
    borderRadius: 12,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 12,
  },
  actions: {
    padding: 20,
  },
  updateButton: {
    flexDirection: 'row',
    backgroundColor: '#4F46E5',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  updateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  deleteButton: {
    flexDirection: 'row',
    backgroundColor: '#FEE2E2',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  deleteButtonText: {
    color: '#EF4444',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
  },
  modalContainer: {
    flex: 1,
    justifyContent: 'flex-end',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalContent: {
    backgroundColor: 'white',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111',
  },
  sliderContainer: {
    marginBottom: 20,
  },
  sliderLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111',
    marginBottom: 12,
    textAlign: 'center',
  },
  slider: {
    width: '100%',
    height: 40,
  },
  noteInput: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    minHeight: 100,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginBottom: 20,
  },
  saveButton: {
    backgroundColor: '#4F46E5',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default GoalDetailScreen;
