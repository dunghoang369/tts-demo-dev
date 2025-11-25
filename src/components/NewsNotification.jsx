import { useState, useEffect } from 'react';
import './NewsNotification.css';

/**
 * NewsNotification Component
 * Displays a banner when new news content is available
 * @param {boolean} show - Whether to show the notification
 * @param {function} onRefresh - Callback to refresh news
 */
function NewsNotification({ show, onRefresh }) {
  const [isVisible, setIsVisible] = useState(false);
  const [shouldRender, setShouldRender] = useState(false);

  useEffect(() => {
    if (show) {
      setShouldRender(true);
      // Small delay to trigger animation
      setTimeout(() => setIsVisible(true), 10);
    } else {
      setIsVisible(false);
      // Wait for animation to complete before unmounting
      setTimeout(() => setShouldRender(false), 300);
    }
  }, [show]);

  const handleRefresh = () => {
    setIsVisible(false);
    setTimeout(() => {
      onRefresh();
      setShouldRender(false);
    }, 300);
  };

  if (!shouldRender) {
    return null;
  }

  return (
    <div className={`news-notification ${isVisible ? 'visible' : ''}`}>
      <div className="news-notification-content">
        <span className="news-notification-icon">📰</span>
        <span className="news-notification-text">
          New news available! Click to refresh
        </span>
        <button 
          className="news-notification-button"
          onClick={handleRefresh}
        >
          Refresh Now
        </button>
      </div>
    </div>
  );
}

export default NewsNotification;


