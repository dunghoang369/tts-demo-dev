import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute component that checks user role before rendering children
 * @param {object} props
 * @param {React.ReactNode} props.children - The component to render if authorized
 * @param {string} props.requiredRole - The role required to access this route (e.g., 'premium')
 */
function ProtectedRoute({ children, requiredRole }) {
  const { user } = useAuth();
  
  // If premium access is required and user doesn't have premium role, redirect to landing
  if (requiredRole === 'premium' && user?.role !== 'premium') {
    return <Navigate to="/" replace />;
  }
  
  // User has required role or no specific role required
  return children;
}

export default ProtectedRoute;

