# Quick Start Guide - Email Authentication

## What's New? 🎉

The TTS demo now supports **dual authentication**:
- ✅ Login with **username** + password (existing)
- ✅ Login with **email** + password (new - @namisense.ai only)

## How to Use

### 1. Start the Servers

```bash
./start-servers.sh
```

Or manually:
```bash
# Terminal 1 - Backend
source venv/bin/activate
python backend/server.py

# Terminal 2 - Frontend
npm run dev
```

### 2. Open the App

Visit: **http://localhost:5173**

### 3. Login with Username

In the "Username or Email" field, enter:
- **Username:** `admin`
- **Password:** `admin123`
- Click "Sign In"

You'll see: **👤 admin** in the header

### 4. Login with Email

In the "Username or Email" field, enter:
- **Email:** `admin@namisense.ai`
- **Password:** `admin123`
- Click "Sign In"

You'll see: **👤 admin@namisense.ai** in the header

## Demo Accounts

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

## Features

- ✅ Single input field accepts both username and email
- ✅ Email domain restricted to @namisense.ai only
- ✅ Helper text guides users
- ✅ Clear error messages
- ✅ Email displayed in header when used
- ✅ Both methods work independently

## Error Messages

### Invalid Email Domain
If you try to login with `user@gmail.com`:
> ⚠️ Only namisense.ai email addresses are allowed

### Invalid Credentials
If password is wrong:
> ⚠️ Invalid credentials

### Missing Fields
If you leave fields empty:
> ⚠️ Please enter both username/email and password

## What Changed?

### Backend
- Added email user database
- Added domain validation (@namisense.ai)
- Updated login endpoint to accept "identifier"
- Returns both username and email in response

### Frontend
- Label changed to "Username or Email"
- Added helper text below input
- Updated demo credentials display
- Email displayed in header if used

## Testing

Try these scenarios:

1. ✅ Login with username `admin` / `admin123`
2. ✅ Login with email `admin@namisense.ai` / `admin123`
3. ❌ Try `user@gmail.com` → Should show domain error
4. ❌ Try wrong password → Should show invalid credentials
5. ✅ Verify email shows in header after email login
6. ✅ Verify username shows in header after username login

## API Examples

### Login with Username
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin", "password": "admin123"}' \
  -c cookies.txt
```

**Response:**
```json
{
  "success": true,
  "user": {
    "username": "admin",
    "email": null
  }
}
```

### Login with Email
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@namisense.ai", "password": "admin123"}' \
  -c cookies.txt
```

**Response:**
```json
{
  "success": true,
  "user": {
    "username": "admin",
    "email": "admin@namisense.ai"
  }
}
```

### Invalid Domain
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "user@gmail.com", "password": "password"}' \
  -i
```

**Response:**
```json
{
  "success": false,
  "error": "Only namisense.ai email addresses are allowed"
}
```
**Status:** 403 Forbidden

## Documentation

For more details, see:
- `EMAIL_AUTH_UPDATE.md` - Complete implementation details
- `README.md` - Updated project documentation
- `AUTH_SETUP.md` - Detailed setup and testing guide
- `backend/README.md` - API documentation

## Need Help?

1. Make sure backend dependencies are installed:
   ```bash
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

2. Check both servers are running:
   - Backend: http://localhost:5000/api/health
   - Frontend: http://localhost:5173

3. Check browser console for errors

4. Verify you're using @namisense.ai domain for email

## Status

✅ **Email authentication is ready to use!**

Both authentication methods work seamlessly. Choose whichever method you prefer!


