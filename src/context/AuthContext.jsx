import { createContext, useState, useContext, useEffect } from 'react';
import { login as apiLogin, logout as apiLogout, checkSession } from '../api/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  // Check JWT token on mount
  useEffect(() => {
    const verifySession = async () => {
      try {
        const { authenticated, user } = await checkSession();
        if (authenticated && user) {
          setUser(user);
          setAuthenticated(true);
        } else {
          setUser(null);
          setAuthenticated(false);
        }
      } catch (error) {
        console.error('Session verification failed:', error);
        setUser(null);
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };

    verifySession();
  }, []);

  const login = async (identifier, password) => {
    const response = await apiLogin(identifier, password);
    
    if (response.success && response.user) {
      setUser(response.user);
      setAuthenticated(true);
      return { success: true };
    } else {
      throw new Error(response.error || 'Login failed');
    }
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
    setAuthenticated(false);
  };

  const value = {
    user,
    authenticated,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}


