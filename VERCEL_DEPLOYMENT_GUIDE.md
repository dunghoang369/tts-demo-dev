# Vercel Deployment Guide

This guide will walk you through deploying your TTS application to Vercel.

## Prerequisites

1. A Vercel account (sign up at https://vercel.com)
2. Your repository pushed to GitHub, GitLab, or Bitbucket
3. (Optional) Vercel CLI: `npm i -g vercel`

## Step 1: Generate JWT Secret Key

Before deploying, generate a secure JWT secret key. Run this command in your terminal:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Save this output** - you'll need it in Step 3.

Example output: `xK7j9mP2nQ5rT8wY1zA3bC4dE6fG0hH9iJ2kL5mN8oP1qR4sT7uV0wX3yZ6aB9cD`

## Step 2: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard

2. **Click "Add New Project"**

3. **Import Your Git Repository**:
   - Select your Git provider (GitHub/GitLab/Bitbucket)
   - Find and select your `tts` repository
   - Click "Import"

4. **Configure Project Settings**:
   - **Project Name**: Choose a name (e.g., `tts-demo`)
   - **Framework Preset**: Vite (should be auto-detected)
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

5. **DO NOT CLICK DEPLOY YET** - Continue to Step 3 first

## Step 3: Set Environment Variables

**CRITICAL**: You must set environment variables before deploying.

1. In the project configuration page, scroll down to **Environment Variables**

2. Add the following variable:
   - **Key**: `JWT_SECRET_KEY`
   - **Value**: Paste the secret key you generated in Step 1
   - **Environments**: Check all three (Production, Preview, Development)

3. (Optional) Add additional variable if you want to change the allowed email domain:
   - **Key**: `ALLOWED_DOMAIN`
   - **Value**: `namisense.ai` (or your custom domain)
   - **Environments**: Check all three

4. Click "Add" to save each variable

## Step 4: Deploy

1. Click **"Deploy"** button

2. Wait for the build to complete (usually 1-2 minutes)

3. Once deployed, you'll see a success message with your deployment URL

4. Click "Visit" to open your live application

## Step 5: Test Your Deployment

1. **Visit your Vercel URL**: `https://your-project-name.vercel.app`

2. **Test Login** with demo credentials:
   - Username: `admin` / Password: `admin123`
   - Or Email: `admin@namisense.ai` / Password: `admin123`

3. **Test TTS Functionality**:
   - Enter Vietnamese text (e.g., "Xin chào, tôi là trợ lý ảo")
   - Select a voice and model
   - Click "Speak" and verify audio plays

## Alternative: Deploy via Vercel CLI

If you prefer using the command line:

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /path/to/tts
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Scope: Your account
# - Link to existing project? No
# - Project name: (accept default or choose)
# - Directory: ./ (current directory)
# - Override settings? No

# Set environment variable
vercel env add JWT_SECRET_KEY production
# Paste your JWT secret when prompted

# Deploy to production
vercel --prod
```

## Troubleshooting

### Issue: "Login fails" or "Invalid credentials"

- **Check**: Environment variable `JWT_SECRET_KEY` is set correctly
- **Fix**: Go to Vercel Dashboard → Your Project → Settings → Environment Variables
- Verify the variable exists and redeploy if needed

### Issue: "Network error" when logging in

- **Check**: Backend API is running
- **Fix**: Check Vercel Functions logs in Dashboard → Your Project → Logs

### Issue: "CORS error" in browser console

- **Check**: The CORS configuration has been updated (should show `allow_origins=["*"]`)
- **Fix**: Verify `api/server.py` has the correct CORS settings and redeploy

### Issue: TTS audio doesn't play

- **Check**: External TTS API (`https://aft.namisense.ai/tts/offline`) is accessible
- **Fix**: Try the TTS API directly in a separate browser tab to verify it's working

## Post-Deployment Notes

### Domain Configuration

Your app is now live at: `https://your-project-name.vercel.app`

Vercel automatically provides:
- HTTPS/SSL certificates
- Global CDN
- Auto-deployment on git push
- Preview deployments for branches

### Automatic Redeployments

Every time you push to your main branch, Vercel will automatically:
1. Build your project
2. Run tests (if configured)
3. Deploy the new version
4. Keep the previous version as a rollback point

### Custom Domain (Optional)

To add a custom domain:
1. Go to Vercel Dashboard → Your Project → Settings → Domains
2. Add your domain (e.g., `tts.yourdomain.com`)
3. Follow DNS configuration instructions

## Security Recommendations

1. **JWT Secret**: Never commit your JWT secret to git
2. **CORS**: For production, consider restricting CORS to your specific domain
3. **Rate Limiting**: Consider adding rate limiting for the API endpoints
4. **User Database**: Replace mock users with a real database for production

## Demo Credentials

The following demo accounts are available:

**Username Authentication:**
- admin / admin123
- demo / demo123
- user / password

**Email Authentication (@namisense.ai):**
- admin@namisense.ai / admin123
- user@namisense.ai / password123
- demo@namisense.ai / demo123

## Need Help?

- Vercel Documentation: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Project Repository: Check your repo's issues/discussions

---

**Congratulations!** Your TTS application is now live on Vercel! 🎉

