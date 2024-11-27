let currentUserId = null;
let currentUsername = null;

// Initialize auth state
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

// Authentication Functions
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showErrorMessage('Please enter both username and password');
        return;
    }

    try {
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
        
        const data = await response.json();
        
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
            window.location.href = '/dashboard';
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
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
    
    const category = document.getElementById('goal-category').value;
    const description = document.getElementById('goal-description').value;
    const targetDate = document.getElementById('goal-target-date').value;

    try {
        const response = await fetch('/api/v1/goals/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                category: category,
                description: description,
                target_date: targetDate
            })
        });

        const data = await response.json();
        if (data.success) {
            showSuccessMessage('Goal created successfully!');
            closeAddGoalModal();
            fetchGoals();
        } else {
            throw new Error(data.detail || 'Failed to create goal');
        }
    } catch (error) {
        showErrorMessage(error.message);
    }
}

async function fetchGoals() {
    const user = verifyUser();
    if (!user) {
        console.log('No user found');  // Debug log
        return;
    }

    console.log('Fetching goals for user:', user.userId);  // Debug log

    try {
        const response = await fetch(`/api/v1/goals/user/${user.userId}`, {
            credentials: 'include'  // Important for session cookies
        });

        console.log('Response status:', response.status);  // Debug log
        console.log('Response headers:', response.headers);  // Debug log

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received goals data:', data);  // Debug log

        const goalsContainer = document.getElementById('goals-container');
        if (!goalsContainer) {
            console.error('Goals container not found');
            return;
        }

        goalsContainer.innerHTML = '';

        if (data.success && data.goals) {
            if (data.goals.length === 0) {
                goalsContainer.innerHTML = '<p class="no-goals">No goals found. Create your first goal!</p>';
                return;
            }

            data.goals.forEach(goal => {
                goalsContainer.appendChild(createGoalCard(goal));
            });
        }
    } catch (error) {
        console.error('Error fetching goals:', error);
    }
}

// Make sure this runs when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Page loaded');  // Debug log
    if (window.location.pathname === '/dashboard') {
        console.log('On dashboard page');  // Debug log
        const user = verifyUser();
        console.log('User data:', user);  // Debug log
        fetchGoals();
    }
});

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

async function updateProgress(goalId, updateText) {
    try {
        const response = await fetch(`/api/v1/progress/${goalId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                update_text: updateText
            })
        });
        
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Failed to update progress');
        
        showSuccessMessage('Progress updated successfully');
        return data;
    } catch (error) {
        showErrorMessage('Failed to update progress: ' + error.message);
        throw error;
    }
}

async function fetchProgressHistory(goalId) {
    try {
        const response = await fetch(`/api/v1/progress/${goalId}`);
        if (!response.ok) throw new Error('Failed to fetch progress history');
        
        const data = await response.json();
        return data.updates;
    } catch (error) {
        showErrorMessage('Failed to fetch progress history: ' + error.message);
        return [];
    }
}

async function fetchAISuggestions() {
    const user = verifyUser();
    if (!user) return;

    try {
        const response = await fetch(`/api/v1/goals/suggestions/${user.userId}`);
        if (!response.ok) throw new Error('Failed to fetch suggestions');

        const data = await response.json();
        const suggestionsContainer = document.getElementById('suggestions-container');
        
        if (suggestionsContainer && data.success) {
            suggestionsContainer.innerHTML = data.suggestions
                .map(suggestion => `<div class="suggestion">${suggestion}</div>`)
                .join('');
        }
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        // Don't show error message for suggestions as they're not critical
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
    if (progress < 30) return '#ff4444';  // Red for low progress
    if (progress < 70) return '#ffbb33';  // Orange for medium progress
    return '#00C851';  // Green for good progress
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

// Event Listeners

document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    
    if (currentPath === '/dashboard') {
        const user = verifyUser();
        if (!user) {
            window.location.href = '/login';
            return;
        }
        displayUsername();
        fetchGoals();
        fetchAISuggestions();

        // Add periodic refresh
        setInterval(fetchGoals, 30000); // Refresh every 30 seconds
    }

    // Add auto-logout on session expiry
    const checkSession = setInterval(() => {
        const user = verifyUser();
        if (!user && window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    }, 60000); // Check every minute
});
