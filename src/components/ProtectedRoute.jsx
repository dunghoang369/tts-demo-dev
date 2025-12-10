import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { useEffect, useRef } from 'react';

/**
 * ProtectedRoute component that checks user role before rendering children
 * @param {object} props
 * @param {React.ReactNode} props.children - The component to render if authorized
 * @param {string} props.requiredRole - The role required to access this route (e.g., 'premium')
 */
function ProtectedRoute({ children, requiredRole }) {
  const { user } = useAuth();
  const { showToast } = useToast();
  const hasShownToast = useRef(false);
  
  // If premium access is required and user doesn't have premium role, show toast and redirect
  useEffect(() => {
    if (requiredRole === 'premium' && user?.role !== 'premium' && !hasShownToast.current) {
      showToast('Bạn không có quyền truy cập trang này, vui lòng liên hệ admin để được cấp quyền', 'error', 4000);
      hasShownToast.current = true;
    }
  }, [requiredRole, user?.role, showToast]);
  
  if (requiredRole === 'premium' && user?.role !== 'premium') {
    return <Navigate to="/" replace />;
  }
  
  // User has required role or no specific role required
  return children;
}

export default ProtectedRoute;

