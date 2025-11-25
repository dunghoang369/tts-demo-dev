# Quick Start - FastAPI + JWT Authentication

## What Changed? 🚀

The backend has been migrated from **Flask + Sessions** to **FastAPI + JWT Tokens**:
- ✅ Faster performance with async support
- ✅ Automatic API documentation at `/docs`
- ✅ JWT token-based authentication (stateless)
- ✅ Better type safety with Pydantic
- ✅ Same user experience

## How to Use

### 1. Start the Backend

```bash
source venv/bin/activate
python backend/server.py
```

Server runs on: **http://localhost:5000**
API docs: **http://localhost:5000/docs**

### 2. Start the Frontend

```bash
npm run dev
```

Frontend runs on: **http://localhost:5173**

### 3. Login

Visit http://localhost:5173 and login with:

**Username/Password:**
- admin / admin123
- demo / demo123

**Email/Password:**
- admin@namisense.ai / admin123
- user@namisense.ai / password123

## Key Differences

### Authentication Method

**Before (Flask):**
- Server-side sessions
- Cookies automatically handled
- Session stored on server

**After (FastAPI):**
- JWT tokens
- Token stored in sessionStorage
- Stateless (no server-side storage)

### Token Storage

**Where:** `sessionStorage` (browser)
**Persistence:** Cleared on browser close
**Security:** Sent in Authorization header

### API Responses

**Login Response Now Includes Token:**
```json
{
  "success": true,
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@namisense.ai"
  }
}
```

**Token Required for Protected Endpoints:**
```http
GET /api/session
Authorization: Bearer eyJhbGci...
```

## New Features

### 1. Interactive API Documentation

Visit **http://localhost:5000/docs** to:
- See all API endpoints
- Test endpoints directly
- View request/response schemas
- Download OpenAPI spec

### 2. Better Error Messages

FastAPI provides structured errors:
```json
{
  "detail": "Only namisense.ai email addresses are allowed"
}
```

With proper HTTP status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden

### 3. JWT Token

Tokens contain user information:
```json
{
  "sub": "admin",
  "email": "admin@namisense.ai",
  "exp": 1735000000
}
```

**Token expires in 24 hours**

## Testing

### Test Login (Terminal)

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@namisense.ai", "password": "admin123"}'
```

**Response:**
```json
{
  "success": true,
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {...}
}
```

### Test Token Verification

```bash
TOKEN="your-token-here"
curl http://localhost:5000/api/session \
  -H "Authorization: Bearer $TOKEN"
```

### Check API Docs

```bash
open http://localhost:5000/docs
```

## Browser DevTools

### View Token

1. Open DevTools (F12)
2. Go to "Application" or "Storage" tab
3. Expand "Session Storage"
4. Click `http://localhost:5173`
5. See `access_token`

### Clear Token (Logout)

Token is automatically removed on:
- Logout button click
- Browser/tab close
- Manual deletion from sessionStorage

## Demo Accounts (Unchanged)

### Username/Password
| Username | Password   |
|----------|------------|
| admin    | admin123   |
| demo     | demo123    |
| user     | password   |

### Email/Password
| Email                    | Password      |
|--------------------------|---------------|
| admin@namisense.ai       | admin123      |
| user@namisense.ai        | password123   |
| demo@namisense.ai        | demo123       |

## Troubleshooting

### Backend won't start?

```bash
cd /Users/dung.hoang2/dunghc/tts
source venv/bin/activate
pip install -r backend/requirements.txt
python backend/server.py
```

### "Not authenticated" error?

- Token may be expired (24h)
- Token may be invalid
- Check sessionStorage has `access_token`
- Try logging in again

### CORS error?

- Ensure backend is running on port 5000
- Ensure frontend is on port 5173 or 3000
- Check browser console for details

## Documentation

- **FASTAPI_MIGRATION.md** - Complete migration details
- **backend/README.md** - API documentation
- **README.md** - Project overview
- **/docs** - Interactive API docs (when server running)

## Quick Commands

```bash
# Start backend
source venv/bin/activate && python backend/server.py

# Start frontend
npm run dev

# Install backend deps
pip install -r backend/requirements.txt

# View API docs
open http://localhost:5000/docs

# Test health
curl http://localhost:5000/api/health
```

## Status

✅ **FastAPI Migration Complete!**

Backend running on FastAPI with JWT authentication. Frontend updated to use tokens. All features working!

---

**Need Help?**
- Check backend logs
- Check browser console
- Visit http://localhost:5000/docs
- See FASTAPI_MIGRATION.md for details


