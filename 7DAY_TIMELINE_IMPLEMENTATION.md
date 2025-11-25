# 7-Day News Timeline Implementation - Summary

## Overview
Successfully implemented a 7-day news timeline feature that displays news grouped by category with expandable daily entries.

## Changes Made

### 1. Backend API (`api/index.py`)

**Endpoint Modified:** `/api/get_news_by_categories`

**Key Changes:**
- Added 7-day filter using `timedelta(days=7)`
- Changed data structure from flat array to nested object grouped by category and date
- Each category contains an array of daily entries (up to 7 days)
- Filter query increased to 200 articles to ensure coverage across 7 days

**New Response Format:**
```json
{
  "categories": {
    "Breaking News": [
      {
        "date": "25/11/2025",
        "title": "Tin tức Thời sự - 25/11/2025",
        "content": "- Article1: summary\n\n- Article2: summary",
        "article_count": 5
      },
      {
        "date": "24/11/2025",
        "title": "Tin tức Thời sự - 24/11/2025",
        "content": "- Article3: summary",
        "article_count": 3
      }
    ],
    "World News": [...],
    "Investment News": [...],
    "Sport News": [...]
  },
  "last_updated": "2025-11-25T23:59:00"
}
```

**Logic:**
1. Calculate 7-day threshold: `seven_days_ago = datetime.now() - timedelta(days=7)`
2. Fetch last 200 articles ordered by `publish_time` DESC
3. Filter articles: `if publish_time < seven_days_timestamp: continue`
4. Group by category → date (nested dictionary)
5. Sort dates descending (newest first)
6. Merge article summaries per day
7. Build timeline entries with article count

### 2. News Service (`src/api/newsService.js`)

**Function Modified:** `getNewsByCategories()`

**Changes:**
- Changed return structure from `{categories: [], lastUpdated}` to `{categoriesGrouped: {}, lastUpdated}`
- `categoriesGrouped` is now an object with category keys, not an array
- Each category value is an array of day entries

### 3. useNewsPolling Hook (`src/hooks/useNewsPolling.js`)

**Changes:**
- Updated initial state: `newsData` now initialized as `{}` (object) instead of `[]` (array)
- Updated data check: `Object.keys(result.categoriesGrouped).length > 0`
- State updates now work with grouped object structure

### 4. App Component (`src/App.jsx`)

**Changes:**
- Removed manual `useEffect` for fetching news
- Now uses `useNewsPolling` hook which handles fetching and auto-refresh
- Updated NewsTags prop check: `Object.keys(newsData).length > 0`
- Removed fallback to mockNewsData (will show empty if no data)

### 5. NewsTags Component (`src/components/NewsTags.jsx`)

**Complete Rewrite - Key Features:**

**State Management:**
- `expandedCategory`: Tracks which category is currently expanded
- `selectedTag`: Tracks which day entry is selected (format: "category-date")

**Component Structure:**
```
news-tags
├── news-tags-header (title)
└── news-tags-timeline
    └── category-group (for each category)
        ├── category-header (clickable to expand/collapse)
        └── timeline-list (shows when expanded)
            └── day-tag (for each day)
                ├── day-tag-header (date + article count badge)
                └── day-tag-title (Vietnamese title)
```

**Behavior:**
- Click category header → expand/collapse timeline
- Click day entry → load that day's merged content into TTS editor
- Visual feedback: selected day gets purple background
- Skip days with no articles (don't show empty entries)

**Props Format:**
- `newsData`: Object where keys are category names (English) and values are arrays of day entries
- `onTagClick`: Callback receives merged content string

### 6. NewsTags CSS (`src/components/NewsTags.css`)

**Complete Redesign - New Styles:**

**Category Group:**
- Border with rounded corners
- Hover effect with accent color border
- Smooth transitions

**Category Header:**
- Gradient background (purple tint)
- Shows: icon + name + day count + expand arrow
- Changes appearance when expanded
- Bottom border when expanded

**Timeline List:**
- Indented inside category group
- Different background color to show hierarchy
- Gap between day entries

**Day Tags:**
- Left border accent (3px purple)
- Two-line layout: header (date + badge) and title
- Badge shows article count
- Hover: translate right + shadow
- Active: full purple background, white text, enhanced shadow

**Responsive:**
- Adjusted padding and font sizes for mobile
- Scrollable timeline with custom scrollbar

## How It Works

### Daily Crawl Flow:
1. Scheduler runs at 23:59 daily
2. Crawls new articles and stores in Firestore with `publish_time`
3. Updates `_metadata` document with `last_crawl_time`

### Frontend Display Flow:
1. User opens app → `useNewsPolling` hook fetches news
2. Backend filters articles from last 7 days
3. Groups by category and date
4. Frontend displays collapsible categories
5. User expands category → sees up to 7 days of entries
6. User clicks day → merged content loads into TTS editor

### Auto-Refresh Flow:
1. `useNewsPolling` polls API every 30 minutes (or 5 min around 22:00)
2. Compares `last_updated` timestamp
3. If changed → shows notification banner
4. User clicks "Refresh Now" → loads new data

### 7-Day Window:
- Today's articles appear immediately after crawl
- 8th day articles automatically drop off (filtered on backend)
- No manual cleanup needed

## Testing Checklist

✅ Backend returns grouped structure with 7-day filter
✅ Frontend displays collapsible categories
✅ Day entries are clickable and load content
✅ Article count badges show correct numbers
✅ Selected state persists and shows visually
✅ Empty categories don't show (only categories with articles)
✅ Dates sorted newest first
✅ Responsive design works on mobile

## Example Data Flow

**Backend Query:**
```python
# Fetch last 200 articles
# Filter: publish_time >= (now - 7 days)
# Group: category → date → articles[]
# Sort: dates descending per category
```

**API Response:**
```json
{
  "Breaking News": [
    {"date": "25/11/2025", "article_count": 5, ...},
    {"date": "24/11/2025", "article_count": 3, ...},
    {"date": "23/11/2025", "article_count": 2, ...}
  ]
}
```

**Frontend Display:**
```
📰 News (7 Days)

🔴 Breaking News (3 days) ▼
   25/11/2025 [5 articles]
   24/11/2025 [3 articles]
   23/11/2025 [2 articles]

🌍 World News (2 days) ▶
   (collapsed)
```

## Benefits

1. **User Experience:**
   - Clear timeline view
   - Easy navigation by date
   - Visual hierarchy (category → days)
   - Article count visibility

2. **Performance:**
   - Backend filters efficiently
   - Frontend only renders expanded categories
   - Smooth animations

3. **Maintainability:**
   - Clean separation of concerns
   - Automatic 7-day window
   - No manual date management

4. **Scalability:**
   - Can handle multiple articles per day
   - Expandable to more categories
   - Easy to adjust day range

## Future Enhancements (Optional)

- Add "Load More" for days beyond 7
- Show relative dates ("Today", "Yesterday", "3 days ago")
- Add date range picker
- Cache grouped data in localStorage
- Add search/filter within timeline


