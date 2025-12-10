import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children, allowedRoles }) {
  const { user } = useAuth();

  // Check if user has required role
  if (!user || !user.role) {
    return <Navigate to="/" replace />;
  }

  // Check if user's role is in the allowed roles list
  if (!allowedRoles.includes(user.role)) {
    // User doesn't have permission
    console.warn(`Access denied: User role "${user.role}" not in allowed roles:`, allowedRoles);
    return <Navigate to="/" replace />;
  }

  // User has permission, render the protected component
  return children;
}

export default ProtectedRoute;

