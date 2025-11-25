# Automated Cleanup Endpoint - Documentation

## Overview

Added automated cleanup functionality to remove articles older than 7 days from Firebase, with both manual API endpoint and weekly scheduled execution.

## Features

### 1. Manual API Endpoint

**Endpoint:** `POST /api/cleanup_old_news`

**Description:** Manually trigger cleanup of articles older than 7 days

**Request:**
```bash
curl -X POST http://localhost:5000/api/cleanup_old_news
```

**Response (Success - Articles Deleted):**
```json
{
  "success": true,
  "deleted_count": 45,
  "message": "Successfully deleted 45 articles",
  "by_category": {
    "Thời sự": 12,
    "Thế giới": 10,
    "Kinh doanh": 15,
    "Thể thao": 8
  },
  "threshold_date": "2025-11-18 15:30:00"
}
```

**Response (Success - No Articles to Delete):**
```json
{
  "success": true,
  "deleted_count": 0,
  "message": "No articles older than 7 days found",
  "by_category": {},
  "threshold_date": "2025-11-18 15:30:00"
}
```

**Response (Error):**
```json
{
  "error": "Failed to cleanup old news",
  "message": "Error details here"
}
```

### 2. Automated Weekly Cleanup

**Schedule:** Every Sunday at 2:00 AM

**Function:** `scheduled_cleanup()`

**Behavior:**
- Runs automatically via APScheduler
- No user intervention needed
- Logs all operations
- Updates metadata after cleanup

## Implementation Details

### Backend Changes (api/index.py)

#### 1. New Endpoint: `/api/cleanup_old_news`

**Location:** Lines ~820-930

**Logic:**
```python
1. Calculate 7-day threshold
2. Query all articles ordered by publish_time
3. Filter articles older than 7 days
4. Group by category for summary
5. Delete in batches of 500 (Firestore limit)
6. Update _metadata document
7. Return statistics
```

#### 2. New Function: `scheduled_cleanup()`

**Location:** Lines ~965-1025

**Logic:**
```python
1. Calculate 7-day threshold
2. Query and filter old articles
3. Delete in batches
4. Update _metadata
5. Log completion
```

#### 3. Scheduler Job Added

**Location:** Startup event (~line 1063)

**Code:**
```python
scheduler.add_job(
    scheduled_cleanup,
    "cron",
    day_of_week="sun",  # Every Sunday
    hour=2,             # 2:00 AM
    minute=0,
    id="weekly_cleanup",
    replace_existing=True,
)
```

## Usage Examples

### Manual Cleanup via API

**Test locally:**
```bash
# Trigger cleanup
curl -X POST http://localhost:5000/api/cleanup_old_news

# With authentication (if required)
curl -X POST http://localhost:5000/api/cleanup_old_news \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**From JavaScript:**
```javascript
async function cleanupOldNews() {
  const response = await fetch('/api/cleanup_old_news', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });
  
  const result = await response.json();
  console.log(`Deleted ${result.deleted_count} articles`);
  return result;
}
```

**From Python:**
```python
import requests

response = requests.post('http://localhost:5000/api/cleanup_old_news')
result = response.json()
print(f"Deleted {result['deleted_count']} articles")
```

### Automated Cleanup Schedule

**Current Schedule:**
- **When:** Every Sunday at 2:00 AM
- **Why Sunday:** Low traffic time, before weekly start
- **Why 2:00 AM:** After daily crawl (23:59), minimal server load

**Modify Schedule:**

To change frequency or timing, edit `api/index.py`:

```python
# Daily cleanup instead of weekly
scheduler.add_job(
    scheduled_cleanup,
    "cron",
    hour=3,  # 3:00 AM every day
    minute=0,
    id="daily_cleanup",
    replace_existing=True,
)

# Twice weekly (Sunday and Wednesday)
scheduler.add_job(
    scheduled_cleanup,
    "cron",
    day_of_week="sun,wed",
    hour=2,
    minute=0,
    id="twice_weekly_cleanup",
    replace_existing=True,
)

# Monthly cleanup (1st day of month)
scheduler.add_job(
    scheduled_cleanup,
    "cron",
    day=1,
    hour=2,
    minute=0,
    id="monthly_cleanup",
    replace_existing=True,
)
```

## Logging

### Logs to Check

**Manual Cleanup:**
```
INFO:__main__:Starting cleanup of articles older than 7 days...
INFO:__main__:Threshold: 2025-11-18 15:30:00
INFO:__main__:Deleted 45/45 articles
INFO:__main__:Updated _metadata with cleanup information
INFO:__main__:Cleanup completed. Deleted 45 articles older than 7 days
```

**Scheduled Cleanup:**
```
INFO:__main__:Running scheduled cleanup of old articles...
INFO:__main__:Scheduled cleanup completed. Deleted 45 articles
```

**No Articles to Clean:**
```
INFO:__main__:No articles to cleanup
```

### View Logs

**In terminal (development):**
```bash
# Backend running with uvicorn shows logs in stdout
cd api
uvicorn index:app --reload
```

**In production:**
```bash
# Check systemd logs (if using systemd)
journalctl -u tts-backend -f

# Check Docker logs (if using Docker)
docker logs -f tts-backend

# Check log files
tail -f /var/log/tts-backend.log
```

## Monitoring

### Check Cleanup Status

**Via Metadata:**
```python
from firebase_admin import firestore

db = firestore.client()
metadata = db.collection("news_articles").document("_metadata").get()
data = metadata.to_dict()

print(f"Last cleanup: {data.get('last_cleanup_time')}")
print(f"Last deleted: {data.get('last_cleanup_deleted')} articles")
```

**Via API (if you add a status endpoint):**
```bash
curl http://localhost:5000/api/cleanup_status
```

### Alert on Issues

**Option 1: Log Monitoring**
- Set up log aggregation (e.g., ELK, Datadog)
- Alert on error keywords in cleanup logs

**Option 2: Status Endpoint**
- Create `/api/cleanup_status` endpoint
- Check last cleanup time
- Alert if cleanup hasn't run in > 8 days

**Option 3: Metadata Monitoring**
- Periodically query Firestore _metadata
- Compare `last_cleanup_time` with current time
- Send alert if stale

## Performance Considerations

### Batch Size
- **Current:** 500 articles per batch
- **Why:** Firestore batch write limit
- **Impact:** ~100ms per batch

### Execution Time
- **Small dataset (< 100 articles):** < 1 second
- **Medium dataset (100-500 articles):** 1-3 seconds
- **Large dataset (500+ articles):** 1 second per 500 articles

### Database Impact
- **Read operations:** 1 query + N document reads (N = total articles)
- **Write operations:** N/500 batch writes + 1 metadata update
- **Cost:** Minimal (batch operations are efficient)

## Best Practices

### 1. Monitor First Week
- Check logs daily after initial deployment
- Verify cleanup runs successfully
- Confirm correct articles are deleted

### 2. Backup Before First Run
```bash
# Export Firestore data before first automated cleanup
gcloud firestore export gs://YOUR_BUCKET/backup-$(date +%Y%m%d)
```

### 3. Adjust Schedule as Needed
- Start with weekly
- Move to daily if database grows quickly
- Move to monthly if data volume is low

### 4. Test Manually First
```bash
# Test the endpoint before relying on automation
curl -X POST http://localhost:5000/api/cleanup_old_news
```

## Troubleshooting

### Issue: Cleanup Not Running

**Symptoms:**
- No cleanup logs
- Articles older than 7 days still present

**Checks:**
1. Verify scheduler is started:
   ```
   grep "Scheduler started" backend.log
   ```
2. Check for scheduler errors:
   ```
   grep "Failed to start scheduler" backend.log
   ```
3. Verify job is registered:
   ```python
   from apscheduler.schedulers.background import BackgroundScheduler
   scheduler = BackgroundScheduler()
   jobs = scheduler.get_jobs()
   print([job.id for job in jobs])  # Should include 'weekly_cleanup'
   ```

**Solutions:**
- Restart backend server
- Check APScheduler logs
- Verify cron syntax is correct

### Issue: Cleanup Fails Midway

**Symptoms:**
- Error logs during cleanup
- Partial deletion

**Causes:**
- Firebase permission issues
- Network timeout
- Firestore quota exceeded

**Solutions:**
- Check Firebase IAM roles
- Increase timeout in httpx client
- Implement retry logic
- Check Firestore quotas

### Issue: Wrong Articles Deleted

**Symptoms:**
- Recent articles missing
- Wrong threshold applied

**Checks:**
1. Verify server timezone:
   ```python
   from datetime import datetime
   print(datetime.now())  # Should match your timezone
   ```
2. Check `publish_time` field format in Firestore
3. Verify 7-day calculation logic

**Solutions:**
- Set explicit timezone in code
- Verify timestamp format consistency
- Add safety check (never delete articles < 6 days old)

## Comparison: API Endpoint vs Script

| Feature | API Endpoint | Standalone Script |
|---------|--------------|-------------------|
| **Execution** | HTTP POST request | Command line |
| **Dry-run** | No | Yes (default) |
| **Confirmation** | No | Yes (requires "DELETE") |
| **Automation** | Via scheduler | Via cron |
| **Response** | JSON | Terminal output |
| **Best for** | Production automation | Manual/testing |

## Migration from Script to API

If you were using the standalone `cleanup_old_articles.py`:

**Before:**
```bash
# Cron job
0 2 * * 0 cd /path/to/tts && python cleanup_old_articles.py --execute
```

**After:**
```bash
# Use API endpoint instead
0 2 * * 0 curl -X POST http://localhost:5000/api/cleanup_old_news
```

**Benefits:**
- No separate script to maintain
- Consistent with other backend operations
- Automatic via APScheduler (no external cron needed)
- Returns structured JSON response
- Can be called from frontend if needed

## Security Considerations

### 1. Authentication (Optional)

If you want to protect the endpoint:

```python
@app.post("/api/cleanup_old_news")
async def cleanup_old_news(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Verify token
    token = credentials.credentials
    payload = verify_token(token)
    
    # Rest of cleanup logic...
```

### 2. Rate Limiting

Prevent abuse with rate limiting:

```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/cleanup_old_news")
@limiter.limit("5/hour")  # Max 5 calls per hour
async def cleanup_old_news():
    # Cleanup logic...
```

### 3. IP Whitelist

Restrict to internal IPs only:

```python
ALLOWED_IPS = ["127.0.0.1", "10.0.0.0/8"]

@app.post("/api/cleanup_old_news")
async def cleanup_old_news(request: Request):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Cleanup logic...
```

## Summary

✅ **Added:** POST `/api/cleanup_old_news` endpoint
✅ **Added:** `scheduled_cleanup()` function
✅ **Added:** Weekly cron job (Sunday 2:00 AM)
✅ **Features:** 
  - Batch deletion (500 per batch)
  - Category statistics
  - Metadata updates
  - Comprehensive logging
✅ **Benefits:**
  - Automated database maintenance
  - Consistent 7-day window
  - Improved query performance
  - Reduced storage costs

**Next Steps:**
1. Test the endpoint manually
2. Monitor first automated run (next Sunday)
3. Adjust schedule if needed
4. Set up alerting for failures


