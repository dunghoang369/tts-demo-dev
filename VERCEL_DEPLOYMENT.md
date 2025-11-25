# Vercel Deployment Guide

## Overview
This guide will help you deploy the TTS application (React frontend + FastAPI backend) to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```
3. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, or Bitbucket)

## Project Structure

```
/Users/dung.hoang2/dunghc/tts/
├── api/
│   └── server.py          # FastAPI backend for Vercel serverless
├── backend/
│   └── server.py          # Original backend (for local development)
├── src/                   # React frontend
├── dist/                  # Build output (generated)
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
├── .vercelignore        # Files to ignore
└── package.json         # Node dependencies

```

## Deployment Methods

### Method 1: Deploy via Vercel Dashboard (Recommended for first deployment)

1. **Push code to Git**:
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push
   ```

2. **Import to Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your Git repository
   - Vercel will auto-detect the configuration

3. **Configure Build Settings**:
   - Framework Preset: **Vite**
   - Build Command: `npm run build` (should be auto-detected)
   - Output Directory: `dist` (should be auto-detected)
   - Install Command: `npm install` (should be auto-detected)

4. **Add Environment Variables**:
   Click "Environment Variables" and add:
   
   | Name | Value | Description |
   |------|-------|-------------|
   | `JWT_SECRET_KEY` | `<generate-secure-random-string>` | JWT secret for token signing |
   | `ALLOWED_DOMAIN` | `namisense.ai` | Email domain restriction |

   **Generate a secure JWT secret**:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete (~2-3 minutes)
   - You'll get a URL like: `https://your-app-name.vercel.app`

### Method 2: Deploy via Vercel CLI

1. **Login to Vercel**:
   ```bash
   vercel login
   ```

2. **Deploy** (from project root):
   ```bash
   # Preview deployment
   vercel

   # Production deployment
   vercel --prod
   ```

3. **Set Environment Variables**:
   ```bash
   # Add JWT secret
   vercel env add JWT_SECRET_KEY

   # Add allowed domain
   vercel env add ALLOWED_DOMAIN
   ```

4. **Redeploy** after adding env vars:
   ```bash
   vercel --prod
   ```

## Post-Deployment Configuration

### 1. Update CORS (Important!)

After first deployment, update `/api/server.py` line 23 with your actual Vercel URL:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app-name.vercel.app"],  # Replace with your URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy:
```bash
git commit -am "Update CORS with production URL"
git push
# Vercel will auto-deploy
```

### 2. Test Your Deployment

Visit your Vercel URL and test:

- ✅ Frontend loads
- ✅ Login page appears
- ✅ Can login with username (admin / admin123)
- ✅ Can login with email (admin@namisense.ai / admin123)
- ✅ Invalid domain rejected (@gmail.com)
- ✅ JWT token works
- ✅ TTS synthesis works
- ✅ Logout works

### 3. Check API Health

Visit: `https://your-app-name.vercel.app/api/health`

Should return:
```json
{
  "status": "ok"
}
```

### 4. View API Documentation

FastAPI docs available at:
- Swagger UI: `https://your-app-name.vercel.app/api/docs`
- ReDoc: `https://your-app-name.vercel.app/api/redoc`

## Custom Domain (Optional)

1. Go to your project in Vercel Dashboard
2. Navigate to **Settings** → **Domains**
3. Click **Add**
4. Enter your domain name
5. Follow DNS configuration instructions
6. Update CORS in `api/server.py` with your custom domain

## Troubleshooting

### Frontend loads but API doesn't work

**Check:**
1. Environment variables are set in Vercel dashboard
2. `requirements.txt` is in the root directory
3. Check Vercel function logs in dashboard

**View logs:**
```bash
vercel logs <deployment-url>
```

### CORS Errors

**Solution:**
Update `allow_origins` in `api/server.py` with your exact Vercel URL.

### 500 Internal Server Error

**Check:**
1. Python dependencies are correct
2. Environment variables are set
3. Check Vercel function logs

### Cold Starts

Vercel serverless functions may have cold starts (~1-2 seconds on first request).
This is normal for hobby plan.

### Build Failures

**Common issues:**
1. Missing dependencies in `package.json` or `requirements.txt`
2. Build command incorrect
3. Check build logs in Vercel dashboard

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `JWT_SECRET_KEY` | Yes | Secret for JWT token signing | Random 32+ char string |
| `ALLOWED_DOMAIN` | No | Email domain restriction | `namisense.ai` |

## Continuous Deployment

Vercel automatically deploys when you:
- Push to main/master branch (production)
- Push to other branches (preview deployments)
- Open pull requests (preview deployments)

## Manual Deployment Commands

```bash
# Preview deployment
vercel

# Production deployment
vercel --prod

# Check deployment status
vercel list

# View logs
vercel logs <deployment-url>

# Rollback to previous deployment
vercel rollback

# Remove deployment
vercel remove <deployment-url>
```

## Performance Tips

1. **Optimize Images**: Use next-gen formats (WebP)
2. **Code Splitting**: Vite handles this automatically
3. **Caching**: Vercel handles static asset caching
4. **CDN**: Your app is served from Vercel's global CDN

## Security Best Practices

1. ✅ Use environment variables for secrets
2. ✅ Enable HTTPS only (Vercel does this automatically)
3. ✅ Rotate JWT secret regularly
4. ✅ Implement rate limiting (consider for production)
5. ✅ Monitor logs for suspicious activity

## Monitoring

View analytics in Vercel dashboard:
- Request count
- Response times
- Error rates
- Bandwidth usage

## Cost

- **Hobby Plan** (Free):
  - 100 GB bandwidth/month
  - Serverless function execution: 100 GB-hours
  - Perfect for this project

- **Pro Plan** ($20/month):
  - More bandwidth
  - Faster builds
  - Priority support

## Demo Credentials

Share these credentials with users:

**Username/Password:**
- admin / admin123
- demo / demo123
- user / password

**Email/Password (@namisense.ai):**
- admin@namisense.ai / admin123
- user@namisense.ai / password123
- demo@namisense.ai / demo123

## Support

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI on Vercel**: https://vercel.com/guides/python-with-vercel
- **Discord**: Vercel Community Discord

## Success!

Once deployed, your TTS app will be live at:
`https://your-app-name.vercel.app`

Share this URL with your users! 🎉


