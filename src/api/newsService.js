/**
 * News Service
 * Handles fetching latest news from the backend API
 */

const API_BASE_URL = '/api';

/**
 * Fetch the latest 5 news articles merged into a Breaking News entry
 * @returns {Promise<Object>} Breaking News object with merged summaries
 */
export async function getLatestNews() {
  try {
    const response = await fetch(`${API_BASE_URL}/get_latest_news`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching latest news:', error);
    throw error;
  }
}

/**
 * Fetch the latest news and return as an array (for compatibility with mockNewsData format)
 * @returns {Promise<Array>} Array containing single Breaking News entry
 */
export async function getLatestNewsArray() {
  try {
    const breakingNews = await getLatestNews();
    return [breakingNews];
  } catch (error) {
    console.error('Error fetching latest news array:', error);
    // Return empty array on error
    return [];
  }
}

/**
 * Fetch news from all categories, grouped by 7-day timeline
 * @returns {Promise<Object>} Object with categoriesGrouped (nested structure) and lastUpdated timestamp
 */
export async function getNewsByCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/get_news_by_categories`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('News by categories response:', data);
    
    // Extract last_updated timestamp and store in localStorage
    const lastUpdated = data.last_updated;
    if (lastUpdated) {
      localStorage.setItem('news_last_updated', lastUpdated);
    }
    
    // Return grouped structure: categories is now an object with category keys
    // Each category contains an array of day entries
    return {
      categoriesGrouped: data.categories || {},
      lastUpdated: lastUpdated
    };
  } catch (error) {
    console.error('Error fetching news by categories:', error);
    // Return empty result on error
    return {
      categoriesGrouped: {},
      lastUpdated: null
    };
  }
}

