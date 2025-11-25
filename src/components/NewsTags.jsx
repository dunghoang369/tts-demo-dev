import { useState } from 'react';
import './NewsTags.css';

function NewsTags({ newsData, onTagClick }) {
  const [expandedCategory, setExpandedCategory] = useState(null);
  const [selectedTag, setSelectedTag] = useState(null);

  const handleCategoryClick = (category) => {
    setExpandedCategory(expandedCategory === category ? null : category);
  };

  const handleDayClick = (category, date, content) => {
    const tagKey = `${category}-${date}`;
    setSelectedTag(tagKey);
    onTagClick(content);
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'Breaking News': return '🔴';
      case 'World News': return '🌍';
      case 'Investment News': return '💰';
      case 'Sport News': return '⚽';
      default: return '📰';
    }
  };

  // newsData is now an object: { "Breaking News": [{date, title, content, article_count}, ...], ... }
  const categories = Object.keys(newsData);

  return (
    <div className="news-tags">
      <div className="news-tags-header">
        <span className="news-tags-icon">📰</span>
        <h3 className="news-tags-title">News (7 Days)</h3>
      </div>

      <div className="news-tags-timeline">
        {categories.length === 0 && (
          <div className="no-news-message">
            No news available
          </div>
        )}

        {categories.map((category) => {
          const timeline = newsData[category] || [];
          const isExpanded = expandedCategory === category;

          return (
            <div key={category} className="category-group">
              <button
                className={`category-header ${isExpanded ? 'expanded' : ''}`}
                onClick={() => handleCategoryClick(category)}
              >
                <span className="category-icon">{getCategoryIcon(category)}</span>
                <span className="category-name">{category}</span>
                <span className="category-count">({timeline.length} days)</span>
                <span className="expand-icon">{isExpanded ? '▼' : '▶'}</span>
              </button>

              {isExpanded && (
                <div className="timeline-list">
                  {timeline.length === 0 && (
                    <div className="no-news-day">No news in last 7 days</div>
                  )}

                  {timeline.map((dayEntry, index) => {
                    const tagKey = `${category}-${dayEntry.date}`;
                    const isSelected = selectedTag === tagKey;

                    return (
                      <button
                        key={index}
                        className={`day-tag ${isSelected ? 'active' : ''}`}
                        onClick={() => handleDayClick(category, dayEntry.date, dayEntry.content)}
                        title={dayEntry.title}
                      >
                        <div className="day-tag-header">
                          <span className="day-tag-date">{dayEntry.date}</span>
                          <span className="day-tag-badge">{dayEntry.article_count} articles</span>
                        </div>
                        <div className="day-tag-title">{dayEntry.title}</div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default NewsTags;
