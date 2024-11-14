// Global state management
let currentUserId = null;
let currentUsername = null;

// Initialize auth state
function initAuth() {
    currentUserId = localStorage.getItem('user_id');
    currentUsername = localStorage.getItem('username');
    console.log('Auth state initialized:', { currentUserId, currentUsername });
    return { currentUserId, currentUsername };
}

// Document ready handler with improved auth check
document.addEventListener('DOMContentLoaded', function() {
    const { currentUserId, currentUsername } = initAuth();
    console.log('DOM loaded, checking auth state:', { currentUserId, currentUsername });
    
    if (window.location.pathname === '/dashboard') {
        if (!currentUserId || !currentUsername) {
            console.log('No auth data found, redirecting to login');
            window.location.replace('/');
            return;
        }
        // Only fetch goals and display username if we're on dashboard
        fetchGoals();
        displayUsername();
    }
});

// Authentication Functions
function register() {
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;

    if (!username || !email || !password) {
        showErrorMessage('Please fill in all fields');
        return;
    }

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username,
            email,
            password
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Registration successful! Please log in.');
            setTimeout(() => {
                window.location.replace('/');
            }, 1500);
        } else {
            showErrorMessage(data.error || 'Registration failed. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Registration failed. Please try again.');
    });
}

function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showErrorMessage('Please enter both username and password');
        return;
    }

    console.log('Attempting login with username:', username);

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => {
        console.log('Login response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Login response:', data);
        
        if (data.success && data.user_id) {
            // Update both local state and localStorage
            currentUserId = data.user_id.toString();
            currentUsername = username;
            
            localStorage.setItem('user_id', currentUserId);
            localStorage.setItem('username', username);
            
            // Verify storage
            console.log('Auth data stored:', {
                currentUserId,
                currentUsername,
                localStorage: {
                    user_id: localStorage.getItem('user_id'),
                    username: localStorage.getItem('username')
                }
            });

            showSuccessMessage('Login successful!');
            
            // Use replace instead of href for better navigation
            setTimeout(() => {
                window.location.replace('/dashboard');
            }, 500);
        } else {
            throw new Error(data.error || 'Login failed');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showErrorMessage(error.message || 'Login failed. Please try again.');
    });
}

function logout() {
    console.log('Logging out, clearing auth state');
    
    // Clear both local state and storage
    currentUserId = null;
    currentUsername = null;
    localStorage.clear();
    
    // Verify clearance
    console.log('Auth state after logout:', {
        currentUserId,
        currentUsername,
        localStorage: {
            user_id: localStorage.getItem('user_id'),
            username: localStorage.getItem('username')
        }
    });

    // Use replace for better navigation
    window.location.replace('/');
}
// Goal Management Functions
function openAddGoalModal() {
    if (!checkAuth()) return;
    
    const modal = document.getElementById('add-goal-modal');
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeAddGoalModal() {
    const modal = document.getElementById('add-goal-modal');
    if (modal) {
        modal.style.display = 'none';
        // Clear form fields
        document.getElementById('goal-category').value = '';
        document.getElementById('goal-description').value = '';
        document.getElementById('goal-target-date').value = '';
    }
}

function createGoal(event) {
    event.preventDefault();
    
    if (!checkAuth()) return;

    const createButton = document.getElementById('create-goal-btn');
    const category = document.getElementById('goal-category').value;
    const description = document.getElementById('goal-description').value;
    const targetDate = document.getElementById('goal-target-date').value;

    if (!category || !description || !targetDate) {
        showErrorMessage('Please fill in all fields');
        return;
    }

    if (createButton) {
        createButton.disabled = true;
        createButton.textContent = 'Creating...';
    }

    const goalData = {
        user_id: currentUserId,
        category: category,
        description: description,
        target_date: targetDate
    };

    console.log('Creating goal:', goalData);

    fetch('/set_goal', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(goalData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            showSuccessMessage('Goal created successfully!');
            closeAddGoalModal();
            fetchGoals();
        } else {
            throw new Error(data.error || 'Failed to create goal');
        }
    })
    .catch(error => {
        console.error('Error creating goal:', error);
        showErrorMessage(error.message);
    })
    .finally(() => {
        if (createButton) {
            createButton.disabled = false;
            createButton.textContent = 'Create Goal';
        }
    });
}

function fetchGoals() {
    if (!checkAuth()) return;

    console.log('Fetching goals for user:', currentUserId);

    fetch(`/get_goals/${currentUserId}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Received goals:', data);
        
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
        } else {
            throw new Error(data.error || 'Failed to fetch goals');
        }
    })
    .catch(error => {
        console.error('Error fetching goals:', error);
        showErrorMessage('Failed to fetch goals: ' + error.message);
    });
}

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
            <button onclick="updateGoal(${goal.id})" class="action-button">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button onclick="deleteGoal(${goal.id})" class="action-button delete">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>
    `;
    return card;
}

// Utility Functions
function checkAuth() {
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');
    
    console.log('Checking auth state:', { userId, username });
    
    if (!userId || !username) {
        console.log('Auth check failed, redirecting to login');
        showErrorMessage('Please login to continue');
        window.location.replace('/');
        return false;
    }
    
    return true;
}

function displayUsername() {
    const username = currentUsername || localStorage.getItem('username');
    const usernameElement = document.getElementById('username-display');
    
    if (usernameElement && username) {
        usernameElement.textContent = `Welcome, ${username}!`;
        console.log('Username displayed:', username);
    }
}

function getProgressColor(progress) {
    if (progress < 30) return '#ff4444';  // Red for low progress
    if (progress < 70) return '#ffbb33';  // Orange for medium progress
    return '#00C851';  // Green for good progress
}

function showSuccessMessage(message) {
    console.log('Success:', message);
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
    console.log('Error:', message);
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
window.onclick = function(event) {
    const modal = document.getElementById('add-goal-modal');
    if (event.target == modal) {
        closeAddGoalModal();
    }
}
