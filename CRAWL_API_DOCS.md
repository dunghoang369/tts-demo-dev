# Automated News Crawl API Documentation

## Overview

The automated news crawl system fetches news articles from multiple categories, summarizes them using AI, and stores them in Firestore. It runs both on-demand via API and automatically on a schedule.

## Features

- **Manual Crawl**: Trigger news crawling via API endpoint
- **Automatic Crawl**: Background scheduler runs every 6 hours (configurable)
- **Multiple Categories**: Supports thoi-su, world, investment, sports
- **AI Summarization**: Each article is automatically summarized
- **Firestore Storage**: All processed articles stored in Firebase

## API Endpoint

### POST `/api/crawl_news`

Manually trigger news crawling, summarization, and upload to Firestore.

**Request Body:**
```json
{
  "categories": ["thoi-su", "world", "investment", "sports"],
  "limit": 5
}
```

**Parameters:**
- `categories` (optional): Array of news categories to crawl. Default: all categories
- `limit` (optional): Number of articles per category. Default: 5

**Response:**
```json
{
  "success": true,
  "processed": 20,
  "categories_processed": ["thoi-su", "world", "investment", "sports"],
  "fetch_date": "2025-11-24T22:28:54.480566",
  "details": [
    {
      "category": "Thời sự",
      "articles": 5,
      "uploaded": 5,
      "failed": 0
    },
    ...
  ]
}
```

## Example Usage

### Crawl all categories (default 5 articles each)
```bash
curl -X POST http://localhost:5000/api/crawl_news \
  -H "Content-Type: application/json"
```

### Crawl specific category
```bash
curl -X POST http://localhost:5000/api/crawl_news \
  -H "Content-Type: application/json" \
  -d '{"categories": ["thoi-su"], "limit": 5}'
```

### Crawl multiple categories with custom limit
```bash
curl -X POST http://localhost:5000/api/crawl_news \
  -H "Content-Type: application/json" \
  -d '{"categories": ["thoi-su", "world"], "limit": 10}'
```

## Background Scheduler

The system automatically crawls news on a daily schedule.

**Schedule:**
- **Initial crawl**: 30 seconds after server startup
- **Daily crawl**: Every day at 23:59 (11:59 PM)

**Configuration:**
- Categories: All (thoi-su, world, investment, sports)
- Articles per category: 5

**Scheduler Logs:**
The scheduler logs its activity:
- Startup: "Initial news crawl scheduled for HH:MM:SS"
- Startup: "Scheduler started. News will be crawled daily at 23:59"
- Each run: "Running scheduled news crawl..."
- Completion: "Scheduled crawl completed. Total processed: X"

## Processing Flow

1. **Fetch News**: Call external API to get latest articles
2. **Parse Data**: Extract title, content, publish time, URL
3. **Summarize**: Send full text to AI summarization API
4. **Store**: Upload processed article with summary to Firestore

**Data Stored in Firestore:**
- `title`: Article title
- `full_text`: Complete article text
- `summary`: AI-generated summary
- `publish_time`: Unix timestamp
- `url`: Article URL
- `category`: News category
- `fetch_date`: ISO timestamp when fetched

## Error Handling

- If an individual article fails to summarize, it's skipped and counted in `failed`
- Processing continues even if some articles fail
- Errors are logged with details

## Performance

- Processing time: ~25-30 seconds per article (summarization is the bottleneck)
- For 5 articles: ~2-3 minutes
- For 20 articles (4 categories × 5): ~10-12 minutes

## Firestore Collection Structure

```
news_articles/
├── _metadata (document)
│   ├── fetch_date
│   ├── total_items
│   ├── news_type
│   └── timestamp
├── {timestamp}_{hash} (document per article)
│   ├── title
│   ├── full_text
│   ├── summary
│   ├── publish_time
│   ├── url
│   ├── category
│   └── fetch_date
```

## Dependencies

- `httpx==0.27.0` - Async HTTP client
- `pandas==2.2.0` - Timestamp conversion
- `apscheduler==3.10.4` - Background scheduler
- `firebase-admin==6.5.0` - Firestore integration

## Notes

- The endpoint processes synchronously - it waits for all operations to complete
- Firebase credentials must be present at `firebase-credentials.json`
- The external APIs must be accessible (news API and summarization API)
- Each document ID is generated from publish_time + hash(title) to avoid duplicates

