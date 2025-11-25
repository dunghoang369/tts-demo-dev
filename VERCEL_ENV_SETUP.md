# Vercel Environment Variables Setup

This guide explains how to set up Firebase credentials securely using Vercel environment variables.

## Why Use Environment Variables?

- ✅ **Security**: Credentials are not exposed in your repository
- ✅ **Best Practice**: Industry-standard approach for managing secrets
- ✅ **Flexibility**: Easy to update without changing code
- ✅ **GitHub Protection**: No more push protection errors

## Setup Instructions

### Step 1: Get Your Firebase Credentials JSON

Your Firebase credentials are stored in `firebase-credentials.json` (which is gitignored). You'll need to convert this to a single-line string.

Run this command in your terminal:

```bash
cat firebase-credentials.json | tr -d '\n'
```

This will output your credentials as a single line. **Copy the entire output.**

### Step 2: Add to Vercel Environment Variables

1. Go to your Vercel Dashboard: https://vercel.com/dashboard
2. Select your project (`tts-demo-dev`)
3. Go to **Settings** → **Environment Variables**
4. Add a new environment variable:
   - **Name**: `FIREBASE_CREDENTIALS_JSON`
   - **Value**: Paste the single-line JSON string from Step 1
   - **Environment**: Select **Production**, **Preview**, and **Development** (all three)
5. Click **Save**

### Step 3: Redeploy Your Application

After adding the environment variable:

1. Go to the **Deployments** tab in Vercel
2. Click the three dots (**...**) on your latest deployment
3. Select **Redeploy**

Or simply push a new commit to trigger a deployment.

## How It Works

The updated code in `api/index.py` now:

1. **First** tries to load credentials from the `FIREBASE_CREDENTIALS_JSON` environment variable
2. **Falls back** to the local `firebase-credentials.json` file for local development

This means:
- **Production (Vercel)**: Uses environment variables ✅
- **Local Development**: Uses your local file ✅

## Verification

After deployment, check your Vercel logs:

- Success: `Firebase initialized successfully using environment variable`
- Fallback: `Firebase initialized successfully using [file path]`
- Error: `Error initializing Firebase: [error message]`

## Alternative: Using Vercel CLI

You can also set environment variables using the Vercel CLI:

```bash
vercel env add FIREBASE_CREDENTIALS_JSON
```

Then paste your single-line JSON when prompted.

## Security Notes

- ❌ **Never** commit `firebase-credentials.json` to git
- ✅ The file is already in `.gitignore`
- ✅ Keep your local `firebase-credentials.json` for development
- ✅ Rotate your credentials if they were ever exposed

## Troubleshooting

### Error: "Firebase credentials not found"

- Verify the environment variable is set in Vercel
- Check that you selected all three environments (Production, Preview, Development)
- Ensure the JSON is valid (no extra quotes or characters)

### Error: "Invalid JSON"

- Make sure you copied the entire JSON output
- Verify there are no line breaks in the environment variable value
- Test the JSON locally: `echo "$FIREBASE_CREDENTIALS_JSON" | python -m json.tool`

## Need Help?

If you encounter issues:
1. Check Vercel deployment logs for specific errors
2. Verify the environment variable is set correctly
3. Try redeploying after making changes

