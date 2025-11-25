# 7-Day News Timeline - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    React Frontend                        │    │
│  │                   (http://localhost:5173)                │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                           │    │
│  │  ┌──────────────┐    ┌──────────────┐   ┌───────────┐  │    │
│  │  │   App.jsx    │───→│ NewsTags.jsx │←──│ .css file │  │    │
│  │  │              │    │              │   └───────────┘  │    │
│  │  │ - Polling    │    │ - Categories │                  │    │
│  │  │ - Notif.     │    │ - Timeline   │                  │    │
│  │  └──────┬───────┘    │ - Selection  │                  │    │
│  │         │            └──────────────┘                  │    │
│  │         ↓                                               │    │
│  │  ┌──────────────────┐        ┌────────────────┐       │    │
│  │  │ useNewsPolling   │←──────→│ newsService.js │       │    │
│  │  │                  │        │                │       │    │
│  │  │ - Fetch news     │        │ - API calls    │       │    │
│  │  │ - Check updates  │        │ - Parse data   │       │    │
│  │  │ - Show notif.    │        └────────┬───────┘       │    │
│  │  └──────────────────┘                 │               │    │
│  │                                        ↓               │    │
│  └────────────────────────────────────────┼───────────────┘    │
│                                            │                    │
└────────────────────────────────────────────┼────────────────────┘
                                             │
                                             │ HTTP /api/*
                                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Vite Dev Server                           │
│                   (Proxy: /api → localhost:5000)                 │
└────────────────────────────────────────┬────────────────────────┘
                                         │
                                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                   (http://localhost:5000)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      api/index.py                          │  │
│  ├───────────────────────────────────────────────────────────┤  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  Endpoint: /api/get_news_by_categories           │    │  │
│  │  │                                                   │    │  │
│  │  │  1. Calculate 7-day threshold                    │    │  │
│  │  │     └─ seven_days_ago = now - timedelta(7)       │    │  │
│  │  │                                                   │    │  │
│  │  │  2. Query Firestore (limit 200)                  │    │  │
│  │  │     └─ order_by publish_time DESC                │    │  │
│  │  │                                                   │    │  │
│  │  │  3. Filter articles >= seven_days_ago            │    │  │
│  │  │                                                   │    │  │
│  │  │  4. Group by category → date                     │    │  │
│  │  │     └─ articles_by_category_and_date[cat][date]  │    │  │
│  │  │                                                   │    │  │
│  │  │  5. Sort dates descending                        │    │  │
│  │  │                                                   │    │  │
│  │  │  6. Merge summaries per day                      │    │  │
│  │  │     └─ "- Title: Summary\n\n"                    │    │  │
│  │  │                                                   │    │  │
│  │  │  7. Build response with English category names   │    │  │
│  │  │                                                   │    │  │
│  │  │  8. Add last_updated from _metadata              │    │  │
│  │  │                                                   │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  Endpoint: /api/crawl_news                       │    │  │
│  │  │  - Manual trigger for testing                    │    │  │
│  │  │  - Called by scheduler at 23:59                  │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐    │  │
│  │  │  APScheduler                                     │    │  │
│  │  │  - Daily cron: 23:59                             │    │  │
│  │  │  - Calls process_and_upload_news()               │    │  │
│  │  └──────────────────────────────────────────────────┘    │  │
│  │                                                            │  │
│  └────────────────────────┬───────────────────────────────────┘  │
│                           │                                       │
└───────────────────────────┼───────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Google Firestore                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Collection: news_articles                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Document 1                                              │    │
│  │ - article_id: 4964943                                   │    │
│  │ - title: "Bắc Ninh, Thái Nguyên..."                    │    │
│  │ - summary: "HĐND ba tỉnh..."                           │    │
│  │ - category: "Thời sự"                                   │    │
│  │ - publish_time: 1763370055                              │    │
│  │ - url: "https://..."                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Document: _metadata                                     │    │
│  │ - last_crawl_time: "2025-11-25T23:59:00"                │    │
│  │ - total_articles: 150                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow: Daily Crawl

```
23:59 Daily Cron
      ↓
APScheduler triggers
      ↓
process_and_upload_news()
      ↓
┌─────────────────────────┐
│ Fetch from external API │
│ - thoi-su, the-gioi,    │
│   kinh-doanh, the-thao  │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Summarize each article  │
│ - Call summarize API    │
│ - Generate summaries    │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Upload to Firestore     │
│ - news_articles/doc_id  │
│ - Update _metadata      │
└─────────────────────────┘
```

## Data Flow: Frontend Refresh

```
User opens app
      ↓
useNewsPolling hook initializes
      ↓
Fetch initial news
      ↓
newsService.getNewsByCategories()
      ↓
HTTP GET /api/get_news_by_categories
      ↓
Backend filters & groups (7 days)
      ↓
Returns JSON response
      ↓
Frontend parses categoriesGrouped
      ↓
App.jsx updates newsData state
      ↓
NewsTags renders categories (collapsed)
      ↓
┌─────────────────────────────────┐
│ User clicks category header     │
└───────────┬─────────────────────┘
            ↓
Category expands, shows 7 days
      ↓
┌─────────────────────────────────┐
│ User clicks day entry           │
└───────────┬─────────────────────┘
            ↓
onTagClick(content) called
      ↓
App.jsx sets editorText
      ↓
TextEditor displays merged content
      ↓
User can synthesize to audio
```

## Data Flow: Auto-Refresh

```
useNewsPolling sets interval
      ↓
Every 30 min (or 5 min near 22:00)
      ↓
fetchNews() called
      ↓
newsService.getNewsByCategories()
      ↓
Compare lastUpdated timestamps
      ↓
┌─────────────────────┐   ┌──────────────────┐
│ No change           │   │ New timestamp    │
└─────────────────────┘   └────────┬─────────┘
                                   ↓
                          setHasNewContent(true)
                                   ↓
                          NewsNotification banner slides down
                                   ↓
                          ┌────────────────────────┐
                          │ User clicks "Refresh"  │
                          └────────┬───────────────┘
                                   ↓
                          refreshNews() called
                                   ↓
                          Update newsData state
                                   ↓
                          NewsTags re-renders with new data
                                   ↓
                          Banner dismisses
```

## Component Hierarchy

```
App.jsx
├── NewsNotification (banner, top of page)
│   ├── show={hasNewContent}
│   └── onRefresh={refreshNews}
│
├── TextEditor (main content area)
│   ├── externalText={editorText}
│   └── onTextChange={setEditorText}
│
├── NewsTags (sidebar)
│   ├── newsData={newsData}
│   └── onTagClick={handleTagClick}
│       │
│       └── For each category in newsData:
│           │
│           ├── CategoryHeader (collapsible)
│           │   ├── Icon (🔴 🌍 💰 ⚽)
│           │   ├── Name (Breaking News, etc.)
│           │   ├── Day count (3 days)
│           │   └── Expand icon (▶ ▼)
│           │
│           └── TimelineList (when expanded)
│               │
│               └── For each day in timeline:
│                   │
│                   └── DayTag (clickable)
│                       ├── Date (25/11/2025)
│                       ├── Badge ([5 articles])
│                       └── Title (Tin tức Thời sự - 25/11/2025)
│
├── TextNorm (normalized text display)
│
└── SettingsPanel (TTS settings)
```

## State Management

```
App.jsx State:
├── newsData: {}                      ← From useNewsPolling
├── hasNewContent: false              ← From useNewsPolling
├── isLoading: false                  ← From useNewsPolling
├── editorText: ""                    ← Set by handleTagClick
├── normalizedText: ""                ← Set by TTS API response
└── [TTS settings...]                 ← voice, model, rate, etc.

NewsTags.jsx State:
├── expandedCategory: null            ← "Breaking News" | null
└── selectedTag: null                 ← "Breaking News-25/11/2025" | null

useNewsPolling.js State:
├── newsData: {}                      ← {category: [days...]}
├── hasNewContent: false              ← Detected via timestamp comparison
├── lastUpdated: null                 ← Timestamp string
└── isLoading: false                  ← Fetch in progress
```

## API Endpoints

```
GET /api/get_news_by_categories
├── Query params: none
├── Returns: {categories: {}, last_updated: ""}
└── Used by: Frontend polling, initial load

POST /api/crawl_news
├── Body: {categories: [...], limit: 5}
├── Returns: {message: "", processed: N}
└── Used by: Manual trigger, APScheduler

GET /api/health
├── Returns: {status: "ok"}
└── Used by: Health checks

POST /api/tts/synthesize
├── Body: {text, voice, model, rate, max_word_per_sent}
├── Returns: {normalized_text, audio_url}
└── Used by: TextEditor synthesis
```

## Database Schema

```
Firestore Collection: news_articles
├── Document: {article_id}_{hash}
│   ├── article_id: number
│   ├── title: string
│   ├── summary: string
│   ├── category: string ("Thời sự", "Thế giới", "Kinh doanh", "Thể thao")
│   ├── publish_time: number (Unix timestamp)
│   ├── url: string
│   └── crawled_at: string (ISO timestamp)
│
└── Document: _metadata
    ├── last_crawl_time: string (ISO timestamp)
    ├── total_articles: number
    └── categories_processed: array
```

## Response Transformation

### Backend Query Result
```python
articles_by_category_and_date = {
    "Thời sự": {
        "25/11/2025": [article1, article2, ...],
        "24/11/2025": [article3, article4, ...]
    },
    "Thế giới": {...}
}
```

### Backend Response
```json
{
  "categories": {
    "Breaking News": [
      {
        "date": "25/11/2025",
        "title": "Tin tức Thời sự - 25/11/2025",
        "content": "- Article1: Summary...\n\n- Article2: Summary...",
        "article_count": 5
      }
    ]
  },
  "last_updated": "2025-11-25T23:59:00"
}
```

### Frontend State
```javascript
newsData = {
  "Breaking News": [
    {date: "25/11/2025", title: "...", content: "...", article_count: 5},
    {date: "24/11/2025", title: "...", content: "...", article_count: 3}
  ],
  "World News": [...]
}
```

## Timeline Example

```
Day 1 (Nov 25):
  ├── Daily cron runs at 23:59
  ├── Crawls 5 articles per category
  ├── Uploads to Firestore
  └── Updates _metadata.last_crawl_time

Day 2 (Nov 26):
  ├── User opens app
  ├── Frontend fetches last 7 days
  ├── Shows: Nov 25, Nov 26 (2 days)
  └── Daily cron adds Nov 26 articles

Day 3-7 (Nov 27-Dec 1):
  ├── Each day adds new articles
  ├── Timeline grows: 3 days, 4 days, ..., 7 days
  └── All 7 days visible

Day 8 (Dec 2):
  ├── Daily cron adds Dec 2 articles
  ├── Frontend shows: Nov 26 - Dec 2 (7 days)
  └── Nov 25 articles no longer appear (8 days old)
```

## Performance Considerations

### Backend
- Query limit: 200 articles (ensures coverage)
- Filter in code: `publish_time >= seven_days_timestamp`
- No DB cleanup needed (filter at query time)
- Response size: ~50-100KB JSON

### Frontend
- Initial load: Fetch once on mount
- Polling: 30 min intervals (low overhead)
- Rendering: Only expanded categories render children
- Max elements: 4 categories × 7 days = 28 items
- No virtualization needed (small dataset)

### Network
- API calls: ~2-3 per session (initial + refresh)
- Payload: Compressed JSON (~50KB)
- Polling: Smart intervals (30 min normal, 5 min peak)
- Cache: localStorage for last_updated

---

**Architecture Status:** ✅ Complete and Optimized


