# Railway Deployment Guide for PawMatcher

## Prerequisites
- GitHub account connected to Railway
- Azure OpenAI API credentials

## Deployment Steps

### 1. Connect to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `pawmatch` repository

### 2. Configure Environment Variables

In your Railway project dashboard, add these environment variables:

```
AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### 3. Railway Configuration

Railway will automatically:
- Detect Python and install dependencies from `requirements.txt`
- Use the `Procfile` to start the app with `gunicorn`
- Assign a public URL to your app

### 4. Deploy

Railway will automatically deploy when you push to your `main` branch.

## Manual Deployment via CLI

If you prefer using the CLI:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up

# Add environment variables
railway variables set AZURE_OPENAI_ENDPOINT="your_endpoint"
railway variables set AZURE_OPENAI_API_KEY="your_key"
railway variables set AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini"
railway variables set AZURE_OPENAI_API_VERSION="2024-08-01-preview"
```

## Post-Deployment

After deployment, Railway will provide a URL like:
`https://your-app.railway.app`

Visit this URL to access your PawMatcher application!

## Troubleshooting

### Check Logs
```bash
railway logs
```

### Redeploy
```bash
railway up --detach
```

### Check Service Status
View your deployment status in the Railway dashboard.

## Cost
Railway offers:
- $5 free credit per month
- Pay-as-you-go after free tier
- ~$5-10/month for small apps

## Notes
- Make sure all dependencies are in `requirements.txt`
- The app uses `gunicorn` as specified in `Procfile`
- Static files are served from the `static/` directory
- Templates are in the `templates/` directory
