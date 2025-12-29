import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../context/AuthContext';
import { goalsAPI } from '../../services/api';
import GoalCard from '../../components/GoalCard';

const DashboardScreen = ({ navigation }) => {
  const { user, logout } = useAuth();
  const [goals, setGoals] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchGoals = useCallback(async () => {
    try {
      const response = await goalsAPI.getGoals(user.id);
      if (response.success) {
        setGoals(response.goals || []);
      }
    } catch (error) {
      console.error('Error fetching goals:', error);
      Alert.alert('Error', 'Failed to fetch goals');
    }
  }, [user.id]);

  const fetchSuggestions = useCallback(async () => {
    try {
      const response = await goalsAPI.getSuggestions(user.id);
      if (response.success) {
        setSuggestions(response.suggestions || []);
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
      setSuggestions([
        'Start by creating your first goal',
        'Break down your goals into manageable tasks',
        'Track your progress regularly',
      ]);
    }
  }, [user.id]);

  const loadData = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchGoals(), fetchSuggestions()]);
    setLoading(false);
  }, [fetchGoals, fetchSuggestions]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  }, [loadData]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', () => {
      fetchGoals();
    });
    return unsubscribe;
  }, [navigation, fetchGoals]);

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Logout', onPress: logout, style: 'destructive' },
    ]);
  };

  const renderHeader = () => (
    <View>
      {/* AI Suggestions */}
      {suggestions.length > 0 && (
        <View style={styles.suggestionsContainer}>
          <View style={styles.suggestionsHeader}>
            <Ionicons name="bulb" size={20} color="#F59E0B" />
            <Text style={styles.suggestionsTitle}>AI Suggestions</Text>
          </View>
          {suggestions.map((suggestion, index) => (
            <View key={index} style={styles.suggestionItem}>
              <Ionicons name="sparkles" size={14} color="#4F46E5" />
              <Text style={styles.suggestionText}>{suggestion}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Section Header */}
      <View style={styles.sectionHeader}>
        <Text style={styles.sectionTitle}>My Goals</Text>
        <TouchableOpacity onPress={() => navigation.navigate('AddGoal')}>
          <Ionicons name="add-circle" size={28} color="#4F46E5" />
        </TouchableOpacity>
      </View>
    </View>
  );

  const renderEmptyState = () => (
    <View style={styles.emptyState}>
      <Ionicons name="checkbox-outline" size={80} color="#D1D5DB" />
      <Text style={styles.emptyTitle}>No Goals Yet</Text>
      <Text style={styles.emptyText}>
        Create your first goal to start tracking your progress
      </Text>
      <TouchableOpacity
        style={styles.createButton}
        onPress={() => navigation.navigate('AddGoal')}
      >
        <Text style={styles.createButtonText}>Create Goal</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4F46E5" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {user.username}!</Text>
          <Text style={styles.subtitle}>Track your goals</Text>
        </View>
        <TouchableOpacity onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={24} color="#EF4444" />
        </TouchableOpacity>
      </View>

      {/* Goals List */}
      <FlatList
        data={goals}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <GoalCard
            goal={item}
            onPress={() => navigation.navigate('GoalDetail', { goalId: item.id })}
          />
        )}
        ListHeaderComponent={renderHeader}
        ListEmptyComponent={renderEmptyState}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      />
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
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111',
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  suggestionsContainer: {
    margin: 16,
    padding: 16,
    backgroundColor: 'white',
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#4F46E5',
  },
  suggestionsHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  suggestionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8,
    color: '#111',
  },
  suggestionItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  suggestionText: {
    flex: 1,
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111',
  },
  listContent: {
    paddingBottom: 20,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111',
    marginTop: 16,
  },
  emptyText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 8,
    marginBottom: 24,
  },
  createButton: {
    backgroundColor: '#4F46E5',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  createButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DashboardScreen;
