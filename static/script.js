// Global state management
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

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('Current path:', window.location.pathname);
    
    if (window.location.pathname === '/dashboard') {
        const user = verifyUser();
        if (!user) {
            showErrorMessage('Please login to continue');
            window.location.href = '/';
            return;
        }
        console.log('User verified:', user);
        displayUsername();
        fetchGoals();
    }
});

// Authentication Functions
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showErrorMessage('Please enter both username and password');
        return;
    }

    console.log('Attempting login...');

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
            // Store user data in both localStorage and sessionStorage
            localStorage.setItem('user_id', data.user_id.toString());
            localStorage.setItem('username', username);
            sessionStorage.setItem('user_id', data.user_id.toString());
            sessionStorage.setItem('username', username);
            
            // Set global variables
            currentUserId = data.user_id.toString();
            currentUsername = username;
            
            console.log('Stored user data:', {
                localStorage: {
                    user_id: localStorage.getItem('user_id'),
                    username: localStorage.getItem('username')
                },
                sessionStorage: {
                    user_id: sessionStorage.getItem('user_id'),
                    username: sessionStorage.getItem('username')
                }
            });

            showSuccessMessage('Login successful!');
            window.location.href = '/dashboard';
        } else {
            throw new Error(data.error || 'Login failed');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showErrorMessage('Login failed. Please check your credentials.');
    });
}

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
            username: username,
            email: email,
            password: password
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage('Registration successful! Please log in.');
            setTimeout(() => {
                window.location.href = '/';
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

function logout() {
    console.log('Logging out...');
    // Clear all storage
    localStorage.clear();
    sessionStorage.clear();
    currentUserId = null;
    currentUsername = null;
    window.location.href = '/';
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
        // Clear form fields
        document.getElementById('goal-category').value = '';
        document.getElementById('goal-description').value = '';
        document.getElementById('goal-target-date').value = '';
    }
}

function createGoal(event) {
    event.preventDefault();
    
    const user = verifyUser();
    if (!user) {
        showErrorMessage('Please login to create goals');
        return;
    }

    const category = document.getElementById('goal-category').value;
    const description = document.getElementById('goal-description').value;
    const targetDate = document.getElementById('goal-target-date').value;

    if (!category || !description || !targetDate) {
        showErrorMessage('Please fill in all fields');
        return;
    }

    const createButton = document.getElementById('create-goal-btn');
    if (createButton) {
        createButton.disabled = true;
        createButton.textContent = 'Creating...';
    }

    const goalData = {
        user_id: user.userId,
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
        console.log('Response status:', response.status);
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
    const user = verifyUser();
    if (!user) {
        return;
    }

    console.log('Fetching goals for user:', user.userId);

    fetch(`/get_goals/${user.userId}`)
    .then(response => {
        console.log('Response status:', response.status);
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
function displayUsername() {
    const user = verifyUser();
    if (!user) return;
    
    const usernameElement = document.getElementById('username-display');
    if (usernameElement) {
        usernameElement.textContent = `Welcome, ${user.username}!`;
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
