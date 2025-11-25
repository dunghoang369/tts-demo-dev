# Quick Reference: Cleanup Endpoint

## API Endpoint

**Trigger Manual Cleanup:**
```bash
curl -X POST http://localhost:5000/api/cleanup_old_news
```

**Response:**
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

## Automated Schedule

**Frequency:** Weekly  
**Day:** Sunday  
**Time:** 2:00 AM  
**Automatic:** Yes (APScheduler)

## What It Does

1. Finds articles older than 7 days
2. Deletes them in batches (500 per batch)
3. Updates `_metadata` document
4. Logs statistics
5. Returns deletion summary

## Files Modified

- **api/index.py**
  - Added `/api/cleanup_old_news` endpoint (~line 820)
  - Added `scheduled_cleanup()` function (~line 965)
  - Added weekly cron job to scheduler (~line 1063)

## Check Logs

```bash
# Check last cleanup
grep "Scheduled cleanup completed" backend.log

# Check for errors
grep "Error in scheduled cleanup" backend.log
```

## Modify Schedule

Edit `api/index.py` line ~1063:

```python
# Change to daily
scheduler.add_job(
    scheduled_cleanup,
    "cron",
    hour=3,  # 3:00 AM daily
    minute=0,
    id="daily_cleanup",
    replace_existing=True,
)
```

## Benefits

- ✅ Automatic database maintenance
- ✅ Keeps database clean (7-day window)
- ✅ Improves query performance
- ✅ Reduces storage costs
- ✅ No manual intervention needed

## Full Documentation

See **CLEANUP_ENDPOINT_GUIDE.md** for complete details, troubleshooting, and advanced usage.


