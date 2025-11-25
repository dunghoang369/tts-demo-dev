import { useState, useEffect } from 'react';
import './News.css';

function News() {
  const [selectedCategory, setSelectedCategory] = useState('breaking');
  const [articlesText, setArticlesText] = useState('');
  const [crawlDate, setCrawlDate] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch crawl date from articles_news.json
    fetch('/articles_news.json')
      .then(response => response.json())
      .then(data => {
        if (data.fetch_date) {
          setCrawlDate(data.fetch_date);
        }
      })
      .catch(error => console.error('Error loading crawl date:', error));

    // Fetch extracted articles text
    fetch('/extracted_articles.txt')
      .then(response => response.text())
      .then(text => {
        setArticlesText(text);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error loading articles:', error);
        setLoading(false);
      });
  }, []);

  const categories = [
    { id: 'breaking', name: 'Breaking News' },
    { id: 'world', name: 'World News' },
    { id: 'investment', name: 'Investment News' },
    { id: 'sports', name: 'Sports News' }
  ];

  return (
    <div className="news-container">
      <div className="news-header">
        <h1>News</h1>
        <select 
          className="category-dropdown"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      <div className="news-content">
        {selectedCategory === 'breaking' ? (
          <>
            {crawlDate && (
              <div className="crawl-date-tag">
                <span className="date-label">Crawled on:</span>
                <span className="date-value">{crawlDate}</span>
              </div>
            )}
            {loading ? (
              <div className="loading">Loading articles...</div>
            ) : (
              <div className="articles-text">
                {articlesText}
              </div>
            )}
          </>
        ) : (
          <div className="coming-soon">
            <h2>{categories.find(c => c.id === selectedCategory)?.name}</h2>
            <p>Coming soon...</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default News;

