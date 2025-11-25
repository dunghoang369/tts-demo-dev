import { useState, useEffect, useCallback, useRef } from 'react';
import { getNewsByCategories } from '../api/newsService';

/**
 * Custom hook for polling news with smart intervals
 * - Polls every 30 minutes during normal hours
 * - Polls every 5 minutes around crawl time (23:00-00:30)
 * - Detects new content by comparing last_updated timestamps
 */
export function useNewsPolling() {
  const [newsData, setNewsData] = useState({});
  const [hasNewContent, setHasNewContent] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const pollingIntervalRef = useRef(null);

  /**
   * Determine polling interval based on current time
   * @returns {number} Interval in milliseconds
   */
  const getPollingInterval = useCallback(() => {
    const hour = new Date().getHours();
    // Between 23:00-00:30, check every 5 minutes
    if (hour === 23 || hour === 0) {
      return 5 * 60 * 1000; // 5 minutes
    }
    // Otherwise, check every 30 minutes
    return 30 * 60 * 1000; // 30 minutes
  }, []);

  /**
   * Fetch news from API
   */
  const fetchNews = useCallback(async (isManual = false) => {
    try {
      setIsLoading(true);
      const result = await getNewsByCategories();
      
      console.log('Fetched news:', result);
      
      if (result.categoriesGrouped && Object.keys(result.categoriesGrouped).length > 0) {
        // Check if this is new content
        const newTimestamp = result.lastUpdated;
        
        if (lastUpdated && newTimestamp && newTimestamp !== lastUpdated && !isManual) {
          console.log('New content detected!', { old: lastUpdated, new: newTimestamp });
          setHasNewContent(true);
        }
        
        // Only update news data if manual refresh or no notification pending
        if (isManual || !hasNewContent) {
          setNewsData(result.categoriesGrouped);
          setLastUpdated(newTimestamp);
          if (isManual) {
            setHasNewContent(false);
          }
        }
      }
    } catch (error) {
      console.error('Failed to fetch news in polling:', error);
    } finally {
      setIsLoading(false);
    }
  }, [lastUpdated, hasNewContent]);

  /**
   * Manual refresh callback for user-triggered refresh
   */
  const refreshNews = useCallback(async () => {
    await fetchNews(true);
  }, [fetchNews]);

  /**
   * Set up polling with smart intervals
   */
  useEffect(() => {
    // Initial fetch
    fetchNews();

    // Set up polling
    const startPolling = () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }

      const interval = getPollingInterval();
      console.log(`Setting up polling with interval: ${interval / 1000 / 60} minutes`);
      
      pollingIntervalRef.current = setInterval(() => {
        fetchNews();
      }, interval);
    };

    startPolling();

    // Check every hour if we need to adjust polling interval
    const intervalCheckTimer = setInterval(() => {
      const currentInterval = getPollingInterval();
      const isCurrentlySame = pollingIntervalRef.current?._idleTimeout === currentInterval;
      
      if (!isCurrentlySame) {
        console.log('Time changed, adjusting polling interval');
        startPolling();
      }
    }, 60 * 60 * 1000); // Check every hour

    // Cleanup
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      clearInterval(intervalCheckTimer);
    };
  }, [fetchNews, getPollingInterval]);

  /**
   * Refresh on tab focus if data is stale
   */
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && lastUpdated) {
        const now = new Date().getTime();
        const lastUpdateTime = new Date(lastUpdated).getTime();
        const thirtyMinutes = 30 * 60 * 1000;
        
        // If data is older than 30 minutes, refresh
        if (now - lastUpdateTime > thirtyMinutes) {
          console.log('Tab focused and data is stale, refreshing...');
          fetchNews(true);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [lastUpdated, fetchNews]);

  return {
    newsData,
    hasNewContent,
    isLoading,
    refreshNews,
  };
}

