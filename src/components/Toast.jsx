import { useEffect } from 'react';
import './Toast.css';

/**
 * Toast Notification Component
 * @param {object} props
 * @param {string} props.message - The message to display
 * @param {string} props.type - The type of toast ('error', 'success', 'info', 'warning')
 * @param {function} props.onClose - Callback when toast is closed
 * @param {number} props.duration - Duration in ms before auto-close (default: 4000)
 */
function Toast({ message, type = 'info', onClose, duration = 4000 }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  return (
    <div className={`toast toast-${type}`} onClick={onClose}>
      <div className="toast-content">
        <span className="toast-icon">
          {type === 'error' && '🚫'}
          {type === 'success' && '✓'}
          {type === 'info' && 'ℹ️'}
          {type === 'warning' && '⚠️'}
        </span>
        <span className="toast-message">{message}</span>
      </div>
      <button className="toast-close" onClick={onClose} aria-label="Close">
        ×
      </button>
    </div>
  );
}

export default Toast;


