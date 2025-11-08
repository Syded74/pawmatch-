# Render Deployment Guide for PawMatcher

## Quick Deploy to Render (FREE)

Render offers a free tier that's perfect for your PawMatcher app!

### 1. Sign Up / Login
Go to [render.com](https://render.com) and sign in with GitHub

### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already done
3. Select **`Syded74/pawmatch`** repository
4. Click **"Connect"**

### 3. Configure Service

**Basic Settings:**
- **Name**: `pawmatch`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: (leave blank)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Instance Type:**
- Select **"Free"** (0$/month)

### 4. Add Environment Variables

Click **"Advanced"** and add these environment variables:

```
AZURE_OPENAI_ENDPOINT=https://tette-mhm601bb-eastus2.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 5. Deploy!

Click **"Create Web Service"**

Render will:
- Clone your repo
- Install dependencies
- Start your app
- Give you a URL like: `https://pawmatch.onrender.com`

## Free Tier Details

- ✅ Free forever
- ✅ 750 hours/month compute time
- ✅ Automatic deployments from GitHub
- ✅ Free SSL certificate
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold starts take ~30 seconds

## Auto-Deploy from GitHub

Once set up, any push to your `main` branch automatically deploys!

## View Logs

In Render dashboard:
- Go to your service
- Click **"Logs"** tab
- See real-time deployment and runtime logs

## Manual Deploy

To manually trigger a deploy:
- Go to your service dashboard
- Click **"Manual Deploy"** → **"Deploy latest commit"**

## Cost

**100% FREE** for this use case!

No credit card required for free tier.
