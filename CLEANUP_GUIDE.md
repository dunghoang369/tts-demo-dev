# Cleanup Old Articles Script - Usage Guide

## Overview

The `cleanup_old_articles.py` script removes articles older than 7 days from your Firestore database to keep it clean and optimize performance.

## Features

- ✅ Removes articles older than 7 days
- ✅ Dry-run mode by default (safe testing)
- ✅ Shows detailed summary before deletion
- ✅ Groups articles by category
- ✅ Batch deletion (efficient)
- ✅ Updates metadata with cleanup info
- ✅ Confirmation prompt in live mode

## Installation

No additional dependencies needed - uses existing Firebase setup.

## Usage

### 1. Dry Run (Recommended First)

**Test what would be deleted without actually deleting:**

```bash
cd /Users/dung.hoang2/dunghc/tts
python cleanup_old_articles.py
```

**Output Example:**
```
============================================================
Cleanup Articles Older Than 7 Days
============================================================
Current time: 2025-11-25 15:30:00
7 days ago: 2025-11-18 15:30:00
Threshold timestamp: 1731942600.0
Mode: DRY RUN (no actual deletion)
============================================================

Found 45 articles to delete:
------------------------------------------------------------
  Thời sự: 12 articles
  Thế giới: 10 articles
  Kinh doanh: 15 articles
  Thể thao: 8 articles
------------------------------------------------------------

First 10 articles to delete:
------------------------------------------------------------
1. [Thời sự] Bắc Ninh, Thái Nguyên, Quảng Trị có tân chủ tịch...
   Published: 2025-11-10 14:30:00
2. [Thế giới] Ukraine receives new military aid package...
   Published: 2025-11-11 09:15:00
...
------------------------------------------------------------

⚠️  DRY RUN: No articles were actually deleted.
To perform actual deletion, run with --execute flag
```

### 2. Execute Deletion

**Actually delete the articles:**

```bash
python cleanup_old_articles.py --execute
```

**You'll be prompted for confirmation:**
```
⚠️  WARNING: This will permanently delete 45 articles!
Type 'DELETE' to confirm: DELETE
```

**Then deletion proceeds:**
```
🗑️  Deleting 45 articles...
  Deleted 45/45 articles...

✅ Successfully deleted 45 articles older than 7 days
✅ Updated _metadata with cleanup information
```

### 3. Custom Days Threshold

**Delete articles older than a different number of days:**

```bash
# Delete articles older than 14 days
python cleanup_old_articles.py --days 14 --execute

# Delete articles older than 30 days
python cleanup_old_articles.py --days 30 --execute
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--execute` | Actually delete articles (default is dry-run) | `False` |
| `--days N` | Delete articles older than N days | `7` |

## Safety Features

### 1. Dry Run by Default
- Script runs in dry-run mode unless `--execute` is specified
- Shows exactly what would be deleted
- No data is modified

### 2. Confirmation Prompt
- In live mode, requires typing "DELETE" to confirm
- Prevents accidental deletions
- Can be cancelled with Ctrl+C

### 3. Batch Processing
- Deletes in batches of 500 (Firestore limit)
- Shows progress during deletion
- Handles large datasets efficiently

### 4. Metadata Update
- Updates `_metadata` document with cleanup info
- Records last cleanup time
- Records number of articles deleted

## When to Run

### Manual Execution
Run periodically to clean up old data:
```bash
# Weekly cleanup
python cleanup_old_articles.py --execute
```

### Automated via Cron (Linux/Mac)
Add to crontab to run automatically:
```bash
# Run every day at 2:00 AM
0 2 * * * cd /Users/dung.hoang2/dunghc/tts && python cleanup_old_articles.py --execute >> logs/cleanup.log 2>&1
```

### Automated via APScheduler (Python)
Add to `api/index.py` scheduler:
```python
# Run cleanup daily at 1:00 AM
scheduler.add_job(
    run_cleanup_script,
    'cron',
    hour=1,
    minute=0,
    id='daily_cleanup',
)
```

## Output Details

### Summary Section
Shows overview of articles to delete:
- Total count
- Breakdown by category
- Current time and threshold

### Article List
Shows first 10 articles:
- Category
- Title (truncated)
- Publication date

### Deletion Progress
In execute mode:
- Real-time progress
- Batch completion status
- Final count

## Error Handling

### Firebase Credentials Not Found
```
Error: Firebase credentials not found at /path/to/firebase-credentials.json
```
**Solution:** Ensure `firebase-credentials.json` exists in project root

### No Articles to Delete
```
✅ No articles older than 7 days found. Database is clean!
```
**Result:** Script exits successfully, no action needed

### Deletion Cancelled
```
❌ Deletion cancelled
```
**Result:** User typed something other than "DELETE"

### Firestore Error
```
❌ Error during cleanup: [error message]
```
**Solution:** Check Firebase credentials and permissions

## Examples

### Example 1: First-Time Run
```bash
# Check what would be deleted
python cleanup_old_articles.py

# Review output, then execute
python cleanup_old_articles.py --execute
```

### Example 2: Aggressive Cleanup
```bash
# Remove articles older than 3 days
python cleanup_old_articles.py --days 3 --execute
```

### Example 3: Monthly Cleanup
```bash
# Keep only last 30 days
python cleanup_old_articles.py --days 30 --execute
```

## Impact on Frontend

### Before Cleanup
- Database has 200 articles (7 days + older)
- Query fetches 200 articles, filters 7 days in code
- Slower queries

### After Cleanup
- Database has only 7 days worth (e.g., 50 articles)
- Query fetches 50 articles, all relevant
- Faster queries
- Less storage used

### No Impact On
- Frontend display (still shows 7 days)
- User experience (same timeline view)
- API response format

## Best Practices

1. **Test First**: Always run dry-run before execute
2. **Regular Schedule**: Run daily or weekly
3. **Monitor Logs**: Check output for errors
4. **Backup Important**: Consider backing up before first run
5. **Adjust Days**: Use 7 days to match frontend filter

## Troubleshooting

### Script Hangs
- Check Firestore connection
- Verify network connectivity
- Check Firebase quota limits

### Permission Denied
- Ensure Firebase credentials have delete permissions
- Check IAM roles in Firebase console

### Partial Deletion
- Script handles batch failures gracefully
- Re-run to complete deletion
- Check Firestore logs

## Advanced Usage

### Import as Module
```python
from cleanup_old_articles import cleanup_old_articles

# Run programmatically
deleted = cleanup_old_articles(dry_run=False)
print(f"Deleted {deleted} articles")
```

### Custom Threshold
Modify the script to use different criteria:
```python
# Delete by category
if category == "Sport News" and age > 3:
    delete_article()
```

## Monitoring

### Check Metadata
```python
import firebase_admin
from firebase_admin import firestore

db = firestore.client()
metadata = db.collection("news_articles").document("_metadata").get().to_dict()
print(f"Last cleanup: {metadata.get('last_cleanup_time')}")
print(f"Deleted: {metadata.get('last_cleanup_deleted')}")
```

### Query Article Count
```python
articles = db.collection("news_articles").stream()
count = sum(1 for doc in articles if doc.id != "_metadata")
print(f"Total articles: {count}")
```

## Summary

- ✅ Safe dry-run mode by default
- ✅ Detailed output and confirmation
- ✅ Efficient batch processing
- ✅ Keeps database clean
- ✅ Optimizes query performance
- ✅ Matches frontend 7-day filter

**Recommended:** Run weekly with `--execute` flag to maintain optimal database size.


