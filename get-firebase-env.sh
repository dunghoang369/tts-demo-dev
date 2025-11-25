#!/bin/bash

# Script to generate a single-line JSON for Vercel environment variables
# Usage: ./get-firebase-env.sh

if [ ! -f "firebase-credentials.json" ]; then
    echo "Error: firebase-credentials.json not found!"
    echo "Make sure you're in the project root directory."
    exit 1
fi

echo "================================================"
echo "Firebase Credentials (Single-line for Vercel)"
echo "================================================"
echo ""
echo "Copy the line below and paste it as the value for FIREBASE_CREDENTIALS_JSON in Vercel:"
echo ""
cat firebase-credentials.json | tr -d '\n' | tr -d '\r'
echo ""
echo ""
echo "================================================"
echo "Next steps:"
echo "1. Copy the line above"
echo "2. Go to Vercel Dashboard → Your Project → Settings → Environment Variables"
echo "3. Add new variable: FIREBASE_CREDENTIALS_JSON"
echo "4. Paste the copied line as the value"
echo "5. Select all environments (Production, Preview, Development)"
echo "6. Save and redeploy"
echo "================================================"

