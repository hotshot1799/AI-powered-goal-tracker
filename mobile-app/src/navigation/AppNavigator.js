import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';

import { useAuth } from '../context/AuthContext';

// Auth Screens
import LoginScreen from '../screens/Auth/LoginScreen';
import RegisterScreen from '../screens/Auth/RegisterScreen';

// App Screens
import DashboardScreen from '../screens/Dashboard/DashboardScreen';
import GoalDetailScreen from '../screens/Goals/GoalDetailScreen';
import AddGoalScreen from '../screens/Goals/AddGoalScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

// Auth Stack
const AuthStack = () => (
  <Stack.Navigator
    screenOptions={{
      headerShown: false,
    }}
  >
    <Stack.Screen name="Login" component={LoginScreen} />
    <Stack.Screen name="Register" component={RegisterScreen} />
  </Stack.Navigator>
);

// Main App Tabs
const AppTabs = () => (
  <Tab.Navigator
    screenOptions={({ route }) => ({
      tabBarIcon: ({ focused, color, size }) => {
        let iconName;

        if (route.name === 'Dashboard') {
          iconName = focused ? 'home' : 'home-outline';
        }

        return <Ionicons name={iconName} size={size} color={color} />;
      },
      tabBarActiveTintColor: '#4F46E5',
      tabBarInactiveTintColor: 'gray',
      headerShown: false,
    })}
  >
    <Tab.Screen name="Dashboard" component={DashboardScreen} />
  </Tab.Navigator>
);

// Main App Stack
const AppStack = () => (
  <Stack.Navigator>
    <Stack.Screen
      name="Main"
      component={AppTabs}
      options={{ headerShown: false }}
    />
    <Stack.Screen
      name="GoalDetail"
      component={GoalDetailScreen}
      options={{
        headerTitle: 'Goal Details',
        headerBackTitle: 'Back',
      }}
    />
    <Stack.Screen
      name="AddGoal"
      component={AddGoalScreen}
      options={{
        presentation: 'modal',
        headerTitle: 'New Goal',
      }}
    />
  </Stack.Navigator>
);

const AppNavigator = () => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return null; // Or a loading screen
  }

  return (
    <NavigationContainer>
      {isAuthenticated ? <AppStack /> : <AuthStack />}
    </NavigationContainer>
  );
};

export default AppNavigator;
