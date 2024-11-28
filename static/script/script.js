let currentUserId = null;
let currentUsername = null;

const DEBUG = true;  // Toggle debugging

function debugLog(context, message, data = null) {
    if (!DEBUG) return;
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${context}: ${message}`;
    if (data) {
        console.log(logMessage, data);
    } else {
        console.log(logMessage);
    }
}

function showSuccessMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success';
    alertDiv.textContent = message;

    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        document.body.appendChild(alertContainer);
    }

    alertContainer.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 3000);
}

function showErrorMessage(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.textContent = message;
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container';
        document.body.appendChild(alertContainer);
    }

    alertContainer.appendChild(alertDiv);
    setTimeout(() => alertDiv.remove(), 5000);
}

function displayUsername() {
    const username = sessionStorage.getItem('username') || localStorage.getItem('username');
    if (username) {
        const usernameElement = document.getElementById('username-display');
        if (usernameElement) {
            usernameElement.textContent = username;
        }
    }
}

async function fetchWithAuth(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            credentials: 'include',
            headers: {
                ...options.headers,
                'Content-Type': 'application/json',
            }
        });
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }

        return response;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded');

    if (window.location.pathname === '/dashboard') {
        console.log('On dashboard page');

        // Check if user is logged in
        const userId = localStorage.getItem('user_id');
        const username = localStorage.getItem('username');

        if (!userId || !username) {
            console.log('No user data found');
            window.location.href = '/login';
            return;
        }

        console.log('User data found:', { userId, username });
        currentUserId = userId;
        currentUsername = username;

        // Initialize dashboard
        displayUsername();
        fetchGoals();
    }
});

// Authentication Functions
async function login() {
    console.log('Starting login process...');  // Log function entry

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showErrorMessage('Please enter both username and password');
        return;
    }

    try {
        console.log('Sending login request...');  // Log before API call
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            }),
            credentials: 'include'
        });

        console.log('Received login response:', response);  // Log response object

        const data = await response.json();
        console.log('Login response data:', data);  // Log response data

        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Login failed');
        }

        if (data.success) {
            localStorage.setItem('user_id', data.user_id.toString());
            localStorage.setItem('username', username);
            sessionStorage.setItem('user_id', data.user_id.toString());
            sessionStorage.setItem('username', username);

            currentUserId = data.user_id.toString();
            currentUsername = username;

            showSuccessMessage('Login successful!');
            console.log('Login successful, redirecting to dashboard...');  // Log success
            window.location.href = '/dashboard';
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        console.error('Error during login:', error);  // Log error with details
        showErrorMessage(error.message || 'Login failed. Please check your credentials.');
    }
}
async function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    try {
        const response = await fetch('/api/v1/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password
            }),
            credentials: 'include'
        });
        const data = await response.json();
        if (response.ok && data.success) {
            showSuccessMessage('Registration successful! Please log in.');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            throw new Error(data.detail || 'Registration failed');
        }
    } catch (error) {
        showErrorMessage(error.message || 'Registration failed');
    }
}

async function logout() {
    try {
        await fetch('/api/v1/auth/logout', {
            method: 'POST',
            credentials: 'include'
        });
        localStorage.clear();
        sessionStorage.clear();
        currentUserId = null;
        currentUsername = null;
        window.location.href = '/';
    } catch (error) {
        showErrorMessage('Logout failed');
    }
}

// Goal Management Functions
function openAddGoalModal() {
    const user = verifyUser();
    if (!user) {
        showErrorMessage('Please login to create goals');
        return;
    }

    const modal = document.getElementById('add-goal-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function verifyUser() {
    const userId = sessionStorage.getItem('user_id') || localStorage.getItem('user_id');
    const username = sessionStorage.getItem('username') || localStorage.getItem('username');

    console.log('Verifying user:', { userId, username });

    if (!userId || !username) {
        console.log('No user data found');
        return false;
    }

    return {
        userId: userId,
        username: username
    };
}


function closeAddGoalModal() {
    const modal = document.getElementById('add-goal-modal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('goal-category').value = '';
        document.getElementById('goal-description').value = '';
        document.getElementById('goal-target-date').value = '';
    }
}

function showEditModal(goalId) {
    fetch(`/api/v1/goals/${goalId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                throw new Error(data.detail || 'Failed to fetch goal details');
            }

            const modal = document.getElementById('edit-goal-modal');
            const form = document.getElementById('edit-goal-form');

            // Populate form fields
            document.getElementById('edit-category').value = data.goal.category;
            document.getElementById('edit-description').value = data.goal.description;
            document.getElementById('edit-target-date').value = data.goal.target_date;

            // Show modal
            modal.style.display = 'block';

            // Update form submission handler
            form.onsubmit = async (e) => {
                e.preventDefault();
                await updateGoal(goalId);
            };
        })
        .catch(error => {
            showErrorMessage(error.message);
        });
}

async function createGoal(event) {
    event.preventDefault();
    debugLog('createGoal', 'Starting goal creation');

    const category = document.getElementById('goal-category').value;
    const description = document.getElementById('goal-description').value;
    const targetDate = document.getElementById('goal-target-date').value;

    userId= localStorage.getItem('user_id');
    debugLog('createGoal', 'Form data', { category, description, targetDate });
    try {
        const response = await fetch('/api/v1/goals/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId,
                category: category,
                description: description,
                target_date: targetDate
            }),
            credentials: 'include'
        });
        debugLog('createGoal', 'Response received', {
            status: response.status,
            statusText: response.statusText
        });
        const data = await response.json();
        debugLog('createGoal', 'Response data', data);

        if (data.success) {
            showSuccessMessage('Goal created successfully!');
            closeAddGoalModal();
            debugLog('createGoal', 'Success, fetching updated goals');
            await fetchGoals();
        } else {
            throw new Error(data.detail || 'Failed to create goal');
        }
    } catch (error) {
        debugLog('createGoal', 'ERROR in goal creation', {
            message: error.message,
            stack: error.stack
        });
        showErrorMessage(error.message);
    }
}

let isLoadingGoals = false; // Flag to track loading state

async function fetchGoals() {
    // Get user from local storage
    const userId = localStorage.getItem('user_id');
    if (!userId) {
        console.error('No user ID found');
        return;
    }

    // Prevent multiple simultaneous fetches
    if (isLoadingGoals) return; 
    
    try {
        isLoadingGoals = true; // Set loading flag
        const goalsContainer = document.getElementById('goals-container');
        if (!goalsContainer) {
            console.error('Goals container not found');
            return;
        }

        // Show loading state
        goalsContainer.innerHTML = '<div class="loading">Loading goals...</div>';

        console.log('Fetching goals...'); // Log before API call
        const response = await fetch(`/api/v1/goals/user/${userId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            credentials: 'include'  // Important for session cookies
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received goals data:', data); // Log received data

        // Clear container
        goalsContainer.innerHTML = '';

        // Check if we have valid data
        if (data.success && Array.isArray(data.goals)) {
            if (data.goals.length === 0) {
                goalsContainer.innerHTML = `
                    <div class="no-goals">
                        <p>No goals found</p>
                        <button onclick="openAddGoalModal()" class="add-goal-btn">
                            Create Your First Goal
                        </button>
                    </div>`;
                return;
            }

            // Create and append goal cards
            data.goals.forEach(goal => {
                goalsContainer.appendChild(createGoalCard(goal));
            });

            console.log('Goals displayed on the dashboard'); // Log successful completion
        } else {
            throw new Error('Invalid goals data received');
        }
    } catch (error) {
        console.error('Error fetching goals:', error);
        const goalsContainer = document.getElementById('goals-container');
        if (goalsContainer) {
            goalsContainer.innerHTML = `
                <div class="error-state">
                    <p>Error loading goals</p>
                    <button onclick="fetchGoals()" class="retry-btn">
                        Try Again
                    </button>
                </div>`;
        }
    } finally {
        isLoadingGoals = false; // Reset loading flag
    }
}

async function updateGoal(goalId) {
    try {
        const response = await fetch('/api/v1/goals/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: goalId,
                category: document.getElementById('edit-category').value,
                description: document.getElementById('edit-description').value,
                target_date: document.getElementById('edit-target-date').value
            })
        });
        const data = await response.json();

        if (data.success) {
            closeEditModal();
            showSuccessMessage('Goal updated successfully');
            fetchGoals();  // Refresh goals list
        } else {
            throw new Error(data.detail || 'Failed to update goal');
        }
    } catch (error) {
        showErrorMessage('Failed to update goal: ' + error.message);
    }
}
function closeEditModal() {
    const modal = document.getElementById('edit-goal-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function viewGoalDetails(goalId) {
    window.location.href = `/goal/${goalId}`;
}

async function fetchAISuggestions(goalId) {
  try {
    const response = await fetch(`/api/v1/goals/suggestions/${goalId}`);
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log('AI Suggestions:', data);
    // Update the UI with the suggestions
  } catch (error) {
    console.error('Error fetching suggestions:', error);
    // Handle the error, e.g., display an error message to the user
  }
}

async function deleteGoal(goalId) {
    if (confirm('Are you sure you want to delete this goal?')) {
        try {
            const response = await fetch(`/api/v1/goals/${goalId}`, {
                method: 'DELETE'
            });
            const data = await response.json();
            if (data.success) {
                showSuccessMessage('Goal deleted successfully');
                fetchGoals();
            } else {
                throw new Error(data.detail || 'Failed to delete goal');
            }
        } catch (error) {
            showErrorMessage('Failed to delete goal: ' + error.message);
        }
    }
}

// UI Helper Functions
function createGoalCard(goal) {
    const card = document.createElement('div');
    card.className = 'goal-card';
    const progressColor = getProgressColor(goal.progress || 0);

    card.innerHTML = `
        <div class="goal-card-header" style="border-left: 4px solid ${progressColor}">
            <div class="goal-category">${goal.category}</div>
            <div class="goal-progress">
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${goal.progress || 0}%; background-color: ${progressColor}"></div>
                </div>
                <span>${goal.progress || 0}%</span>
            </div>
        </div>
        <div class="goal-description">${goal.description}</div>
        <div class="goal-meta">
            <span><i class="fas fa-calendar"></i> ${new Date(goal.target_date).toLocaleDateString()}</span>
        </div>
        <div class="goal-actions">
            <button onclick="viewGoalDetails(${goal.id})" class="action-button">
                <i class="fas fa-chart-line"></i> Track Progress
            </button>
            <button onclick="showEditModal(${goal.id})" class="action-button">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button onclick="deleteGoal(${goal.id})" class="action-button delete">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>
    `;
    return card;
}

function getProgressColor(progress) {
    if (progress < 30) return '#ff4444';
    if (progress < 70) return '#ffbb33';
    return '#00C851';
}
