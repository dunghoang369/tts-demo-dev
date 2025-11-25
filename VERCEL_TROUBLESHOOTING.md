# Vercel Deployment Troubleshooting

## Network Error: "Please ensure the backend server is running"

If you see this error on your deployed site, it means the backend API serverless function isn't working properly.

### Root Causes & Solutions

#### 1. Missing `api/requirements.txt`

**Problem**: Vercel needs a `requirements.txt` file in the same directory as your Python serverless function.

**Solution**: ✅ Fixed - Created `/api/requirements.txt` with required dependencies:
```
fastapi==0.115.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.12
pydantic==2.9.2
email-validator==2.2.0
mangum==0.17.0
```

#### 2. Missing Mangum ASGI Adapter

**Problem**: FastAPI needs Mangum to work as a Vercel serverless function.

**Solution**: ✅ Fixed - Updated `api/server.py`:
- Added `from mangum import Mangum`
- Changed handler from `handler = app` to `handler = Mangum(app)`

#### 3. Missing JWT_SECRET_KEY Environment Variable

**Problem**: If the environment variable isn't set, the app may fail to start.

**Solution**: Set it in Vercel Dashboard:
1. Go to your project on Vercel Dashboard
2. Click **Settings** → **Environment Variables**
3. Add:
   - **Key**: `JWT_SECRET_KEY`
   - **Value**: Run `python -c "import secrets; print(secrets.token_urlsafe(32))"` and paste the output
   - **Environments**: Check all (Production, Preview, Development)
4. Click **Save**
5. **Redeploy** the project (Settings → Deployments → Click ⋯ on latest → Redeploy)

---

## How to Redeploy with Fixes

After the code changes, you need to redeploy to Vercel:

### Option 1: Via Git Push (Recommended)

```bash
# Stage and commit the changes
git add api/requirements.txt api/server.py
git commit -m "fix: Add Mangum adapter and requirements for Vercel serverless functions"

# Push to your main branch
git push origin main
```

Vercel will automatically detect the push and redeploy.

### Option 2: Via Vercel Dashboard

1. Go to your project on Vercel Dashboard
2. Click **Deployments**
3. Click the **⋯** (three dots) on the latest deployment
4. Click **Redeploy**
5. Confirm the redeployment

### Option 3: Via Vercel CLI

```bash
# From your project root
vercel --prod
```

---

## Verification Steps

After redeployment, verify the fix:

### 1. Check API Health Endpoint

Open in your browser:
```
https://your-project-name.vercel.app/api/health
```

You should see:
```json
{"status":"ok"}
```

If you see this, your API is working! ✅

### 2. Test Login

1. Go to your deployed site
2. Try logging in with:
   - **Username**: `admin`
   - **Password**: `admin123`
3. You should successfully log in and see the main TTS interface

### 3. Check Browser Console

1. Open Developer Tools (F12)
2. Go to **Console** tab
3. Try logging in
4. Look for any error messages

If you see CORS errors or 404 errors, continue to Advanced Troubleshooting below.

---

## Advanced Troubleshooting

### Check Vercel Function Logs

1. Go to Vercel Dashboard → Your Project
2. Click **Logs** (or **Deployments** → Click a deployment → **Functions**)
3. Look for errors when you try to log in
4. Common errors:
   - **Module not found**: Missing dependency in `requirements.txt`
   - **Import error**: Syntax error in `api/server.py`
   - **No module named 'mangum'**: Mangum not installed

### Test API Endpoints Directly

Use curl or Postman to test the API:

```bash
# Test health endpoint
curl https://your-project-name.vercel.app/api/health

# Test login endpoint
curl -X POST https://your-project-name.vercel.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"identifier":"admin","password":"admin123"}'
```

Expected response:
```json
{
  "success": true,
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {"username": "admin", "email": null}
}
```

### Verify vercel.json Routes

Your `vercel.json` should look like this:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "api/server.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/server.py"
    },
    {
      "src": "/(.*)",
      "dest": "$1"
    }
  ]
}
```

### Check Build Logs

1. Go to Vercel Dashboard → Your Project → Deployments
2. Click on the latest deployment
3. Click **Building**
4. Look for:
   - ✅ "Installing Python dependencies"
   - ✅ "Building API functions"
   - ❌ Any errors during installation

---

## Still Having Issues?

### 1. Clear Cache and Redeploy

Sometimes Vercel caches old builds:

```bash
# Via CLI
vercel --prod --force

# Or in Dashboard: Deployments → ⋯ → Redeploy → Check "Use existing Build Cache" → Uncheck it
```

### 2. Check Python Version

Vercel uses Python 3.9 by default. If you need a specific version, create `runtime.txt`:

```txt
python-3.9
```

### 3. Environment Variables Not Loading

Make sure:
- Variables are set for the correct environment (Production/Preview/Development)
- Variables don't have trailing spaces
- After adding variables, you **must redeploy**

### 4. CORS Issues

If you see CORS errors in the browser console, check that `api/server.py` has:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Quick Checklist

Before asking for help, verify:

- [ ] `api/requirements.txt` exists with all dependencies
- [ ] `api/server.py` imports and uses `Mangum`
- [ ] `JWT_SECRET_KEY` environment variable is set in Vercel
- [ ] Code is pushed to git (if using git-based deployment)
- [ ] Latest deployment shows "Ready" status
- [ ] `/api/health` endpoint returns `{"status":"ok"}`
- [ ] Browser console shows no CORS errors
- [ ] Vercel function logs show no errors

---

## Summary of Files Changed

### New Files:
- `/api/requirements.txt` - Python dependencies for serverless function

### Modified Files:
- `/api/server.py` - Added Mangum import and updated handler

### Next Steps:
1. Commit and push these changes
2. Wait for Vercel to automatically redeploy
3. Set `JWT_SECRET_KEY` environment variable if not already set
4. Test the `/api/health` endpoint
5. Try logging in again

---

Good luck! If you follow these steps, your deployment should work perfectly. 🚀

