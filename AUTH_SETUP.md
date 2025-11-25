# Authentication Setup & Testing Guide

This guide will help you set up and test the authentication system for the TTS demo application.

## Quick Start

### Option 1: Automated Start (Recommended)

Run both servers with a single command:

```bash
./start-servers.sh
```

Then open your browser and navigate to: `http://localhost:5173`

### Option 2: Manual Start

**Terminal 1 - Backend Server:**
```bash
source venv/bin/activate
python backend/server.py
```

**Terminal 2 - Frontend Server:**
```bash
npm run dev
```

## Testing the Authentication

### 1. Initial Load
- Open `http://localhost:5173` in your browser
- You should see the login page with a gradient purple background
- The page displays demo credentials

### 2. Login Test

**Test with Valid Username Credentials:**
- Username: `admin`
- Password: `admin123`
- Click "Sign In"
- You should be redirected to the main TTS application
- You'll see your username in the header: "👤 admin"

**Test with Valid Email Credentials:**
- Email: `admin@namisense.ai`
- Password: `admin123`
- Click "Sign In"
- You should be redirected to the main TTS application
- You'll see your email in the header: "👤 admin@namisense.ai"

**Test with Invalid Email Domain:**
- Try email: `user@gmail.com`
- Password: `password`
- Click "Sign In"
- You should see an error message: "Only namisense.ai email addresses are allowed"

**Test with Invalid Credentials:**
- Try username: `admin`
- Password: `wrong`
- Click "Sign In"
- You should see an error message: "Invalid credentials"

### 3. Authenticated Session

Once logged in, you should be able to:
- Use all TTS features normally
- See your username displayed in the header
- See a "Logout" button in the header

### 4. Logout Test
- Click the "Logout" button in the header
- A confirmation dialog will appear: "Are you sure you want to logout?"
- Click "OK"
- You should be redirected back to the login page

### 5. Session Persistence Test

**Session Only (Expected Behavior):**
- Log in successfully
- Refresh the page (F5 or Cmd+R)
- You should be logged out and see the login page again
- This is the expected behavior as sessions are not persistent

## Demo Accounts

The following accounts are available for testing:

### Username/Password
| Username | Password   | Description              |
|----------|------------|--------------------------|
| admin    | admin123   | Administrator account    |
| demo     | demo123    | Demo account             |
| user     | password   | Basic user account       |

### Email/Password (@namisense.ai only)
| Email                    | Password      | Description           |
|--------------------------|---------------|-----------------------|
| admin@namisense.ai       | admin123      | Admin via email       |
| user@namisense.ai        | password123   | User via email        |
| demo@namisense.ai        | demo123       | Demo via email        |

## API Endpoints

### Check Backend Status

You can verify the backend is running by visiting:

```
http://localhost:5000/api/health
```

You should see:
```json
{
  "status": "ok"
}
```

### Test Authentication API

**Login Request (Username):**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin", "password": "admin123"}' \
  -c cookies.txt
```

**Login Request (Email):**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "admin@namisense.ai", "password": "admin123"}' \
  -c cookies.txt
```

**Check Session:**
```bash
curl http://localhost:5000/api/session \
  -b cookies.txt
```

**Logout:**
```bash
curl -X POST http://localhost:5000/api/logout \
  -b cookies.txt
```

## Troubleshooting

### Backend Issues

**Backend won't start:**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Check if dependencies are installed: `pip list | grep Flask`
- Verify port 5000 is not in use: `lsof -i :5000`

**CORS Errors:**
- Ensure frontend is running on `http://localhost:5173` or `http://localhost:3000`
- Check backend console for CORS-related logs
- Verify `credentials: 'include'` is set in all fetch calls

### Frontend Issues

**Login page not showing:**
- Check browser console for errors
- Verify backend is running at `http://localhost:5000`
- Check if `AuthProvider` is wrapping the app in `main.jsx`

**Login button does nothing:**
- Open browser console and check for errors
- Verify network requests are being sent to `http://localhost:5000/api/login`
- Check if backend server is running

**Session check fails:**
- Verify cookies are being sent with requests (`credentials: 'include'`)
- Check browser's cookie storage (DevTools > Application > Cookies)
- Ensure backend CORS is configured correctly

### Network Issues

**Cannot connect to backend:**
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check if firewall is blocking port 5000
- Try accessing from a different browser

**401 Unauthorized errors:**
- Clear browser cookies
- Restart both servers
- Try logging in again

## Architecture Overview

### Authentication Flow

```
1. App loads → ProtectedApp.jsx
2. AuthContext checks session → GET /api/session
3. If not authenticated → Show Login.jsx
4. User submits username OR email + password → POST /api/login
5. Backend validates:
   - If email → Check domain is @namisense.ai
   - Validate credentials
6. Backend creates session
7. Frontend updates AuthContext
8. ProtectedApp shows App.jsx
9. User clicks logout → POST /api/logout
10. Backend clears session
11. Frontend redirects to Login.jsx
```

### File Structure

```
Frontend:
├── src/context/AuthContext.jsx    - Authentication state
├── src/api/authService.js         - API calls
├── src/components/Login.jsx       - Login UI
├── src/ProtectedApp.jsx          - Route protection
└── src/App.jsx                   - Main app (protected)

Backend:
└── backend/server.py             - Flask auth server
```

## Production Considerations

When deploying to production, you should:

1. **Use a real database** instead of the hardcoded user dictionary
2. **Hash passwords** using bcrypt or similar
3. **Enable HTTPS** and set `SESSION_COOKIE_SECURE = True`
4. **Update CORS origins** to your production domain
5. **Use persistent sessions** if needed (configure Flask-Session)
6. **Add session expiration** with timeout settings
7. **Implement rate limiting** to prevent brute force attacks
8. **Add CSRF protection** for additional security
9. **Use environment variables** for secrets
10. **Add logging** for authentication events

## Additional Features to Consider

- Password reset functionality
- User registration
- Remember me checkbox (for persistent sessions)
- Email verification
- Two-factor authentication
- OAuth integration (Google, GitHub, etc.)
- Role-based access control
- Session timeout warnings

## Need Help?

If you encounter issues:
1. Check the browser console for errors
2. Check the backend server logs
3. Verify both servers are running
4. Test the API endpoints directly with curl
5. Clear browser cache and cookies

For more details, see:
- `backend/README.md` - Backend documentation
- `README.md` - Main project documentation


