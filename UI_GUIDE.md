# 7-Day News Timeline - UI Guide

## Visual Layout

```
┌─────────────────────────────────────────────┐
│  📰  News (7 Days)                          │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 🔴 Breaking News (3 days)  ▼        │   │
│  ├─────────────────────────────────────┤   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ 25/11/2025      [5 articles]  │  │ ← Day entry (clickable)
│  │  │ Tin tức Thời sự - 25/11/2025  │  │
│  │  └───────────────────────────────┘  │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ 24/11/2025      [3 articles]  │  │
│  │  │ Tin tức Thời sự - 24/11/2025  │  │
│  │  └───────────────────────────────┘  │   │
│  │  ┌───────────────────────────────┐  │   │
│  │  │ 23/11/2025      [2 articles]  │  │ ← Selected (purple bg)
│  │  │ Tin tức Thời sự - 23/11/2025  │  │
│  │  └───────────────────────────────┘  │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 🌍 World News (2 days)  ▶           │   │ ← Collapsed
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 💰 Investment News (4 days)  ▶      │   │ ← Collapsed
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ ⚽ Sport News (5 days)  ▶            │   │ ← Collapsed
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

## Interaction Flow

### 1. Initial State
- All categories are collapsed (▶ icon)
- No day entries visible
- User sees category names and day counts

### 2. Expanding a Category
**Action:** Click on "🔴 Breaking News (3 days) ▶"

**Result:**
- Icon changes to ▼
- Timeline list slides down
- Shows all days with articles (up to 7)
- Each day entry shows:
  - Date (25/11/2025)
  - Article count badge ([5 articles])
  - Vietnamese title (Tin tức Thời sự - 25/11/2025)

### 3. Selecting a Day
**Action:** Click on "25/11/2025 [5 articles]"

**Result:**
- Day entry turns purple (selected state)
- Content loads into TTS text editor
- Content format:
  ```
  - Article Title 1: Summary text here...
  
  - Article Title 2: Summary text here...
  
  - Article Title 3: Summary text here...
  ```

### 4. Collapsing a Category
**Action:** Click on expanded category header

**Result:**
- Icon changes back to ▶
- Timeline list slides up
- Selection persists (will show again when re-expanded)

## Color Scheme

### Category Header
- Background: Light purple gradient (`rgba(124, 92, 255, 0.1)`)
- Hover: Slightly darker gradient
- Expanded: Darker gradient with bottom border

### Day Entry (Normal)
- Background: Input background color
- Border: Standard border + 3px purple left accent
- Text: Normal text color

### Day Entry (Hover)
- Background: Light purple (`rgba(124, 92, 255, 0.1)`)
- Border: Full purple
- Transform: Slide right 6px
- Shadow: Purple glow

### Day Entry (Selected/Active)
- Background: Full purple (`var(--accent-color)`)
- Text: White
- Badge: White with transparency
- Shadow: Enhanced purple glow
- Transform: Slide right 6px (persists)

## Responsive Behavior

### Desktop (>968px)
- Full vertical layout
- Max height: 600px with scrollbar
- All features visible

### Tablet (641px - 968px)
- Reduced max height: 400px
- Slightly smaller padding

### Mobile (<640px)
- Max height: 350px
- Reduced font sizes:
  - Category header: 13px
  - Icons: 16px
  - Day tags: 12px
- Compact padding

## Data Flow Diagram

```
Backend (api/index.py)
    ↓
Filter last 7 days
Group by category → date
    ↓
API Response:
{
  "Breaking News": [
    {date, title, content, article_count},
    {date, title, content, article_count}
  ]
}
    ↓
Frontend (newsService.js)
    ↓
useNewsPolling hook
    ↓
App.jsx state (newsData)
    ↓
NewsTags component
    ↓
Render category groups
    ↓
User clicks day entry
    ↓
onTagClick(content)
    ↓
TextEditor receives content
    ↓
User can synthesize to audio
```

## Example Content Display

When user clicks "25/11/2025 [5 articles]", the TTS editor shows:

```
- Bắc Ninh, Thái Nguyên, Quảng Trị có tân chủ tịch tỉnh: HĐND ba tỉnh Thái Nguyên, Bắc Ninh và Quảng Trị ngày 17/11 đã bầu ông Vương Quốc Tuấn, Phạm Hoàng Sơn và Lê Hồng Vinh giữ chức Chủ tịch UBND tỉnh nhiệm kỳ 2021-2026.

- Chủ tịch Cà Mau làm Phó bí thư Tỉnh ủy Đồng Tháp: Ông Phạm Thành Ngại, Chủ tịch UBND tỉnh Cà Mau được điều động giữ chức Phó bí thư Tỉnh ủy Đồng Tháp và giới thiệu để bầu làm Chủ tịch UBND.

- Đề xuất lao động tự nộp bảo hiểm thất nghiệp khi doanh nghiệp không đóng đủ: Lao động có thể chọn tự đóng vào Quỹ Bảo hiểm thất nghiệp khi doanh nghiệp không đóng đủ để giải quyết quyền lợi...

[... more articles ...]
```

## Animation Details

### Category Expand/Collapse
- Duration: 0.3s
- Easing: ease
- Properties: height, opacity

### Day Entry Hover
- Duration: 0.2s
- Easing: ease
- Properties: background, border-color, transform, box-shadow

### Notification Banner
- Duration: 0.3s
- Easing: ease-in-out
- Properties: transform (translateY)

## Accessibility

- All interactive elements are `<button>` tags (keyboard accessible)
- Semantic HTML structure
- Hover states for visual feedback
- Active states for selection clarity
- Readable font sizes
- Sufficient color contrast

## Performance Optimizations

- Only expanded categories render day entries
- Virtualization not needed (max 7 days × 4 categories = 28 items)
- CSS transitions (GPU accelerated)
- React state updates are batched
- API polling respects intervals (30min normal, 5min peak)


