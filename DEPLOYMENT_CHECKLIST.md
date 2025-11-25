# Quick Deployment Checklist

## Before Deployment

- [ ] All code committed to Git
- [ ] Pushed to GitHub/GitLab/Bitbucket
- [ ] Have Vercel account

## Files Created/Modified

✅ Created:
- [x] `/api/server.py` - Vercel serverless backend
- [x] `/vercel.json` - Vercel configuration
- [x] `/requirements.txt` - Python dependencies (root level)
- [x] `/.vercelignore` - Ignore files
- [x] `/VERCEL_DEPLOYMENT.md` - Full deployment guide

✅ Modified:
- [x] `/package.json` - Added `vercel-build` script
- [x] `/src/api/authService.js` - Added environment-based API URL

## Deployment Steps

### 1. Generate JWT Secret

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output - you'll need it for Vercel environment variables.

### 2. Deploy to Vercel

**Option A: Via Dashboard**
1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Add environment variables:
   - `JWT_SECRET_KEY`: (paste the secret from step 1)
   - `ALLOWED_DOMAIN`: `namisense.ai`
4. Click "Deploy"

**Option B: Via CLI**
```bash
# Install CLI (if not installed)
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod

# Add environment variables
vercel env add JWT_SECRET_KEY
vercel env add ALLOWED_DOMAIN

# Redeploy
vercel --prod
```

### 3. After Deployment

1. **Get your URL**: e.g., `https://tts-abc123.vercel.app`

2. **Update CORS in `/api/server.py`** (line 23):
   ```python
   allow_origins=["https://tts-abc123.vercel.app"]
   ```

3. **Commit and push**:
   ```bash
   git add api/server.py
   git commit -m "Update CORS with production URL"
   git push
   ```
   Vercel will auto-deploy.

### 4. Test Your Deployment

Visit: `https://your-app-name.vercel.app`

Test:
- [ ] Frontend loads
- [ ] Login page appears  
- [ ] Login with username works
- [ ] Login with email works
- [ ] TTS synthesis works
- [ ] API health check: `/api/health`

## Demo Credentials

**Username:**
- admin / admin123
- demo / demo123

**Email (@namisense.ai):**
- admin@namisense.ai / admin123
- user@namisense.ai / password123

## Troubleshooting

**API not working?**
- Check environment variables in Vercel dashboard
- Check function logs: `vercel logs`

**CORS errors?**
- Update `allow_origins` in `/api/server.py`

**Build fails?**
- Check `requirements.txt` is in root
- Check `vercel.json` configuration

## View Logs

```bash
vercel logs <your-url>
```

## For Complete Guide

See: `VERCEL_DEPLOYMENT.md`

## Success!

Your app is now live! 🎉

Share your URL:
`https://your-app-name.vercel.app`


