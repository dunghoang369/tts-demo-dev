// Authentication API Service for JWT

// Use relative path in production (Vercel), localhost in development
const API_BASE_URL = import.meta.env.DEV 
  ? 'http://localhost:5000' 
  : '';  // Relative path for production

/**
 * Get JWT token from sessionStorage
 * @returns {string|null} JWT token or null
 */
function getToken() {
  return sessionStorage.getItem('access_token');
}

/**
 * Store JWT token in sessionStorage
 * @param {string} token - JWT access token
 */
function setToken(token) {
  sessionStorage.setItem('access_token', token);
}

/**
 * Remove JWT token from sessionStorage
 */
function removeToken() {
  sessionStorage.removeItem('access_token');
}

/**
 * Login with username/email and password
 * @param {string} identifier - User's username or email
 * @param {string} password - User's password
 * @returns {Promise<{success: boolean, user?: object, error?: string}>}
 */
export async function login(identifier, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ identifier, password }),
    });

    const data = await response.json();
    
    if (data.success && data.access_token) {
      // Store JWT token in sessionStorage
      setToken(data.access_token);
      return { success: true, user: data.user };
    } else {
      return {
        success: false,
        error: data.detail || data.error || 'Login failed',
      };
    }
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: 'Network error. Please ensure the backend server is running.',
    };
  }
}

/**
 * Logout current user
 * @returns {Promise<{success: boolean}>}
 */
export async function logout() {
  try {
    const token = getToken();
    
    if (token) {
      await fetch(`${API_BASE_URL}/api/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    }
    
    // Remove token from storage
    removeToken();
    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    // Still remove token even if API call fails
    removeToken();
    return { success: true };
  }
}

/**
 * Check current session status by verifying JWT token
 * @returns {Promise<{authenticated: boolean, user?: object}>}
 */
export async function checkSession() {
  try {
    const token = getToken();
    
    if (!token) {
      return { authenticated: false, user: null };
    }

    const response = await fetch(`${API_BASE_URL}/api/session`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    const data = await response.json();
    
    // If token is invalid/expired, remove it
    if (!data.authenticated) {
      removeToken();
    }
    
    return data;
  } catch (error) {
    console.error('Session check error:', error);
    removeToken();
    return { authenticated: false, user: null };
  }
}
