# 7-Day News Timeline - Testing Guide

## Prerequisites

1. **Backend Running:**
   ```bash
   cd /Users/dung.hoang2/dunghc/tts/api
   source ../venv/bin/activate
   uvicorn index:app --reload --host 0.0.0.0 --port 5000
   ```

2. **Frontend Running:**
   ```bash
   cd /Users/dung.hoang2/dunghc/tts
   npm run dev
   ```

3. **Firestore Data:**
   - Ensure Firebase credentials are configured
   - Database has articles in `news_articles` collection
   - Articles have `publish_time`, `category`, `title`, `summary` fields

## Test Cases

### Test 1: Backend API Structure

**Purpose:** Verify the API returns the new grouped structure

**Steps:**
1. Open terminal
2. Run: `curl -s http://localhost:5000/api/get_news_by_categories | python3 -m json.tool`

**Expected Output:**
```json
{
  "categories": {
    "Breaking News": [
      {
        "date": "25/11/2025",
        "title": "Tin tức Thời sự - 25/11/2025",
        "content": "- Article...",
        "article_count": 5
      }
    ],
    "World News": [...],
    "Investment News": [...],
    "Sport News": [...]
  },
  "last_updated": "2025-11-25T23:59:00"
}
```

**Success Criteria:**
- ✅ `categories` is an object (not array)
- ✅ Each category key has an array of day entries
- ✅ Each day entry has: date, title, content, article_count
- ✅ `last_updated` timestamp is present

---

### Test 2: 7-Day Filter

**Purpose:** Verify only articles from last 7 days are returned

**Setup:**
1. Note current date: `date` (e.g., Nov 25, 2025)
2. Calculate 7 days ago: Nov 18, 2025

**Steps:**
1. Query API: `curl -s http://localhost:5000/api/get_news_by_categories`
2. Check all `date` fields in response
3. Parse dates and compare with 7-day window

**Expected:**
- All dates should be >= Nov 18, 2025
- No articles older than 7 days appear

**Success Criteria:**
- ✅ No dates older than 7 days
- ✅ Recent articles (within 7 days) are included
- ✅ Articles from exactly 7 days ago are included
- ✅ Articles from 8+ days ago are excluded

---

### Test 3: Frontend Display - Initial Load

**Purpose:** Verify the UI renders correctly on page load

**Steps:**
1. Open browser to `http://localhost:5173`
2. Log in if needed
3. Look at the News panel (right side)

**Expected:**
- Header shows "📰 News (7 Days)"
- All 4 categories are listed (collapsed):
  - 🔴 Breaking News (X days) ▶
  - 🌍 World News (X days) ▶
  - 💰 Investment News (X days) ▶
  - ⚽ Sport News (X days) ▶
- Day counts show in parentheses
- No day entries visible initially

**Success Criteria:**
- ✅ All categories visible
- ✅ Day counts are accurate
- ✅ Icons display correctly
- ✅ No console errors
- ✅ No "No news available" message (unless database is empty)

---

### Test 4: Expand Category

**Purpose:** Verify expand/collapse functionality

**Steps:**
1. Click on "🔴 Breaking News (3 days) ▶"
2. Observe the animation

**Expected:**
- Icon changes from ▶ to ▼
- Timeline list slides down smoothly
- Day entries appear (up to 7):
  ```
  25/11/2025  [5 articles]
  Tin tức Thời sự - 25/11/2025
  
  24/11/2025  [3 articles]
  Tin tức Thời sự - 24/11/2025
  ```
- Each entry shows date, article count badge, and title

**Success Criteria:**
- ✅ Smooth animation (300ms)
- ✅ All days within 7-day window appear
- ✅ Days sorted newest first (descending)
- ✅ Article counts are correct
- ✅ Titles include Vietnamese category name + date

---

### Test 5: Select Day Entry

**Purpose:** Verify clicking a day loads content into TTS editor

**Steps:**
1. Expand "Breaking News"
2. Click on "25/11/2025 [5 articles]"
3. Check the TTS text editor (left side)

**Expected:**
- Day entry turns purple (selected state)
- TTS editor populates with merged content:
  ```
  - Article Title 1: Summary text...
  
  - Article Title 2: Summary text...
  
  - Article Title 3: Summary text...
  ```
- Content includes all articles from that day
- Format: "- Title: Summary\n\n"

**Success Criteria:**
- ✅ Visual selection (purple background)
- ✅ Content appears in editor
- ✅ Content is properly formatted
- ✅ All articles from that day are included
- ✅ Previous editor content is replaced

---

### Test 6: Multiple Category Interaction

**Purpose:** Verify multiple categories can be expanded simultaneously

**Steps:**
1. Expand "Breaking News"
2. Expand "World News"
3. Expand "Investment News"

**Expected:**
- All three categories show their timelines
- Each maintains its own expanded state
- Scrollbar appears if content exceeds max height (600px)
- No interference between categories

**Success Criteria:**
- ✅ Multiple categories can be expanded at once
- ✅ Each category's timeline is independent
- ✅ Scrolling works smoothly
- ✅ No layout issues or overlaps

---

### Test 7: Collapse Category

**Purpose:** Verify collapsing works correctly

**Steps:**
1. Expand "Breaking News"
2. Select a day entry (turns purple)
3. Collapse "Breaking News"
4. Re-expand "Breaking News"

**Expected:**
- Category collapses smoothly
- Icon changes back to ▶
- When re-expanded, previous selection is still visible (purple)
- Content remains in TTS editor

**Success Criteria:**
- ✅ Smooth collapse animation
- ✅ Selection state persists
- ✅ TTS editor content unchanged
- ✅ Re-expansion shows same timeline

---

### Test 8: Hover Effects

**Purpose:** Verify visual feedback on hover

**Steps:**
1. Expand a category
2. Hover over category header (without clicking)
3. Hover over a day entry (without clicking)

**Expected:**
- **Category Header Hover:**
  - Background darkens slightly
  - Smooth transition
  
- **Day Entry Hover:**
  - Background turns light purple
  - Border turns full purple
  - Entry slides right 6px
  - Purple shadow appears
  - Cursor changes to pointer

**Success Criteria:**
- ✅ Hover states are visible and smooth
- ✅ Transitions are 200ms (not jarring)
- ✅ Colors match design spec
- ✅ Transform is subtle (6px)

---

### Test 9: Empty Category

**Purpose:** Verify handling of categories with no articles in 7 days

**Setup:**
1. Ensure one category has no articles in last 7 days (or manually filter in code for testing)

**Steps:**
1. Expand the empty category

**Expected:**
- Category expands normally
- Shows message: "No news in last 7 days"
- No day entries visible
- Message is styled in muted color, italic

**Success Criteria:**
- ✅ Empty state message displays
- ✅ No errors in console
- ✅ Other categories unaffected

---

### Test 10: API Polling and Notification

**Purpose:** Verify auto-refresh and notification system

**Setup:**
1. Open app in browser
2. Wait for initial load

**Steps:**
1. Wait 30 minutes (or modify polling interval to 1 min for testing)
2. Trigger a manual crawl:
   ```bash
   curl -X POST http://localhost:5000/api/crawl_news \
     -H "Content-Type: application/json" \
     -d '{"categories":["thoi-su"], "limit":5}'
   ```
3. Wait for next polling cycle (max 30 min, or 5 min if near 22:00)

**Expected:**
- Notification banner slides down from top
- Shows: "📰 New news available! Click to refresh"
- "Refresh Now" button is clickable
- Banner is purple gradient

**Success Criteria:**
- ✅ Polling runs automatically
- ✅ Detects new `last_updated` timestamp
- ✅ Notification appears smoothly
- ✅ Clicking "Refresh Now" loads new data
- ✅ Banner disappears after refresh

---

### Test 11: Refresh News Data

**Purpose:** Verify clicking "Refresh Now" updates the timeline

**Steps:**
1. Trigger notification (see Test 10)
2. Note current day entries in a category
3. Click "Refresh Now" in notification banner
4. Re-expand the same category

**Expected:**
- Banner slides up and disappears
- News data refreshes
- New day entries appear (if daily crawl added today's news)
- Old 8th-day entries are gone
- Timeline updates without page reload

**Success Criteria:**
- ✅ Banner dismisses smoothly
- ✅ Data updates in background
- ✅ No page reload required
- ✅ New entries show correct date/count
- ✅ 7-day window is maintained

---

### Test 12: Responsive Design - Mobile

**Purpose:** Verify layout works on mobile devices

**Steps:**
1. Open browser dev tools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or similar
4. Reload page

**Expected:**
- News panel adjusts to mobile width
- Font sizes are readable
- Category headers are compact
- Day entries fit within screen
- Touch targets are large enough (min 44px)
- Scrolling works smoothly

**Success Criteria:**
- ✅ No horizontal overflow
- ✅ Text is readable (not too small)
- ✅ Buttons are tappable
- ✅ Layout adapts gracefully
- ✅ Performance is smooth

---

### Test 13: Multiple Day Entries - Same Category

**Purpose:** Verify handling of multiple days with varying article counts

**Expected Data:**
```
Breaking News
  25/11/2025 [5 articles]
  24/11/2025 [3 articles]
  23/11/2025 [1 article]
  22/11/2025 [7 articles]
  21/11/2025 [2 articles]
  20/11/2025 [4 articles]
  19/11/2025 [6 articles]
```

**Steps:**
1. Expand "Breaking News"
2. Verify all 7 days appear
3. Click on day with 1 article
4. Click on day with 7 articles

**Expected:**
- All days display regardless of article count
- Badge shows correct count for each day
- Content length varies based on article count
- Single article: shorter content
- Seven articles: longer merged content

**Success Criteria:**
- ✅ All days within 7-day window appear
- ✅ Article counts are accurate
- ✅ Content scales appropriately
- ✅ No maximum article limit per day

---

### Test 14: Date Sorting

**Purpose:** Verify days are sorted newest first

**Steps:**
1. Expand any category
2. Read dates from top to bottom

**Expected:**
- Dates descend chronologically:
  ```
  25/11/2025  (newest)
  24/11/2025
  23/11/2025
  ...
  19/11/2025  (oldest in 7-day window)
  ```

**Success Criteria:**
- ✅ Newest date at top
- ✅ Oldest date at bottom
- ✅ Chronological order maintained
- ✅ No date duplicates

---

### Test 15: Content Format

**Purpose:** Verify merged content is properly formatted

**Steps:**
1. Select any day entry
2. Check TTS editor content

**Expected Format:**
```
- Article Title 1: Summary sentence for article 1...

- Article Title 2: Summary sentence for article 2...

- Article Title 3: Summary sentence for article 3...
```

**Rules:**
- Dash + space before title
- Colon after title
- Space before summary
- Double newline between articles
- No trailing newlines after last article

**Success Criteria:**
- ✅ Format matches exactly
- ✅ No missing dashes or colons
- ✅ Spacing is consistent
- ✅ Content is readable

---

### Test 16: Performance - Large Dataset

**Purpose:** Verify performance with maximum data (7 days × 4 categories)

**Setup:**
- Ensure database has articles for all 7 days across all 4 categories
- ~28 day entries total (7 per category)

**Steps:**
1. Open app
2. Expand all 4 categories
3. Scroll up and down
4. Click multiple day entries rapidly

**Expected:**
- Initial load: < 2 seconds
- Expand animation: smooth (no lag)
- Scrolling: 60fps
- Click response: immediate (<100ms)
- No memory leaks

**Success Criteria:**
- ✅ Fast initial load
- ✅ Smooth animations
- ✅ Responsive interactions
- ✅ No console warnings
- ✅ Memory usage stable

---

### Test 17: Edge Case - No News in Database

**Purpose:** Verify graceful handling when database is empty

**Setup:**
- Empty Firestore `news_articles` collection (or use test environment)

**Steps:**
1. Load app
2. Check News panel

**Expected:**
- Header shows "📰 News (7 Days)"
- Message displays: "No news available"
- No category groups appear
- No errors in console
- Other app features still work

**Success Criteria:**
- ✅ Empty state message
- ✅ No JavaScript errors
- ✅ No broken UI elements
- ✅ App remains functional

---

### Test 18: Browser Compatibility

**Purpose:** Verify cross-browser support

**Browsers to Test:**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Steps:**
1. Open app in each browser
2. Test core functionality:
   - Expand/collapse
   - Select day
   - Hover effects
   - Notification

**Expected:**
- Consistent appearance
- All features work
- Animations are smooth
- No browser-specific bugs

**Success Criteria:**
- ✅ Chrome: Full functionality
- ✅ Firefox: Full functionality
- ✅ Safari: Full functionality
- ✅ Edge: Full functionality

---

## Automated Testing (Future)

### Unit Tests
```javascript
// Example test structure
describe('NewsTags Component', () => {
  test('renders categories correctly', () => {...});
  test('expands category on click', () => {...});
  test('selects day entry on click', () => {...});
  test('calls onTagClick with correct content', () => {...});
});
```

### Integration Tests
```javascript
describe('News Timeline Integration', () => {
  test('fetches and displays 7-day data', () => {...});
  test('filters articles older than 7 days', () => {...});
  test('updates on polling interval', () => {...});
});
```

### E2E Tests (Playwright/Cypress)
```javascript
test('complete user flow', async () => {
  await page.goto('http://localhost:5173');
  await page.click('text=Breaking News');
  await page.click('text=25/11/2025');
  await expect(page.locator('.text-editor')).toContainText('Article');
});
```

---

## Troubleshooting

### Issue: Categories not displaying
**Check:**
- Backend is running on port 5000
- Firestore has articles in `news_articles` collection
- Articles have required fields (publish_time, category, title, summary)
- Browser console for errors

### Issue: Day entries not showing
**Check:**
- Articles are within last 7 days (check `publish_time` timestamps)
- Category names match: "Thời sự", "Thế giới", "Kinh doanh", "Thể thao"
- Backend logs for filtering/grouping errors

### Issue: Selection not working
**Check:**
- `onTagClick` prop is passed to NewsTags
- Content field is not empty
- React state is updating (check React DevTools)

### Issue: Notification not appearing
**Check:**
- `useNewsPolling` hook is active
- `last_updated` timestamp changes after crawl
- Polling interval (30 min normal, 5 min near 22:00)
- Browser tab is active (some browsers throttle background tabs)

---

## Success Metrics

### Functional
- ✅ All 18 test cases pass
- ✅ No console errors
- ✅ No linting warnings
- ✅ 7-day filter works correctly

### Performance
- ✅ Initial load < 2s
- ✅ Animations smooth (60fps)
- ✅ Click response < 100ms
- ✅ Memory usage stable

### User Experience
- ✅ Intuitive navigation
- ✅ Visual feedback clear
- ✅ Mobile responsive
- ✅ Accessible (keyboard navigation)

### Data Integrity
- ✅ Dates sorted correctly
- ✅ Article counts accurate
- ✅ Content formatted properly
- ✅ 7-day window maintained


