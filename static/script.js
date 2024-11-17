// Global state management
let currentUserId = null;
let currentUsername = null;

// Auth verification function
function verifyAuth() {
    const isAuthenticated = sessionStorage.getItem('isAuthenticated') === 'true';
    const userId = localStorage.getItem('user_id');
    const username = localStorage.getItem('username');
    
    console.log('Verifying auth:', { isAuthenticated, userId, username });
    
    return isAuthenticated && userId && username;
}

// Initialize auth state
function initAuth() {
    currentUserId = localStorage.getItem('user_id');
    currentUsername = localStorage.getItem('username');
    const isAuthenticated = sessionStorage.getItem('isAuthenticated') === 'true';
    
    console.log('Auth state initialized:', { 
        currentUserId, 
        currentUsername,
        isAuthenticated 
    });
    
    return { currentUserId, currentUsername, isAuthenticated };
}

// Document ready handler with improved auth check
document.addEventListener('DOMContentLoaded', function() {
    const { currentUserId, currentUsername, isAuthenticated } = initAuth();
    console.log('DOM loaded, checking auth state:', { 
        currentUserId, 
        currentUsername,
        isAuthenticated,
        path: window.location.pathname 
    });
    
    if (window.location.pathname === '/dashboard') {
        if (!verifyAuth()) {
            console.log('Auth verification failed, redirecting to login');
            showErrorMessage('Please login to access the dashboard');
            window.location.replace('/');
            return;
        }
        console.log('Auth verified, initializing dashboard');
        fetchGoals();
        displayUsername();
    }
});

// Update login function
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
            // Store auth data
            sessionStorage.setItem('isAuthenticated', 'true');
            localStorage.setItem('user_id', data.user_id.toString());
            localStorage.setItem('username', username);
            
            // Set global variables
            currentUserId = data.user_id.toString();
            currentUsername = username;
            
            console.log('Auth data stored:', {
                currentUserId,
                currentUsername,
                localStorage: {
                    user_id: localStorage.getItem('user_id'),
                    username: localStorage.getItem('username')
                },
                sessionStorage: {
                    isAuthenticated: sessionStorage.getItem('isAuthenticated')
                }
            });

            showSuccessMessage('Login successful!');
            
            // Add longer delay for state to persist
            setTimeout(() => {
                window.location.replace('/dashboard');
            }, 1000);
        } else {
            throw new Error(data.error || 'Login failed');
        }
    })
    .catch(error => {
        console.error('Login error:', error);
        showErrorMessage(error.message || 'Login failed. Please try again.');
    });
}

// Update logout function
function logout() {
    console.log('Logging out, clearing auth state');
    
    // Clear all storage
    localStorage.clear();
    sessionStorage.clear();
    
    // Clear global variables
    currentUserId = null;
    currentUsername = null;
    
    console.log('Auth state after logout:', {
        currentUserId,
        currentUsername,
        localStorage: {
            user_id: localStorage.getItem('user_id'),
            username: localStorage.getItem('username')
        },
        sessionStorage: {
            isAuthenticated: sessionStorage.getItem('isAuthenticated')
        }
    });

    window.location.replace('/');
}

// Update checkAuth function
function checkAuth() {
    if (!verifyAuth()) {
        console.log('Auth check failed, redirecting to login');
        showErrorMessage('Please login to continue');
        window.location.replace('/');
        return false;
    }
    return true;
}
