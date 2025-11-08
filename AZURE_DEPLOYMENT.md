# Azure App Service Deployment Guide for PawMatcher

## Prerequisites
- Azure CLI installed ✅
- Azure account logged in ✅
- GitHub repository ready ✅

## Quick Deploy Steps

### 1. Create Resource Group (if needed)
```bash
az group create --name pawmatch-rg --location eastus2
```

### 2. Create App Service Plan
```bash
az appservice plan create \
  --name pawmatch-plan \
  --resource-group pawmatch-rg \
  --sku B1 \
  --is-linux
```

### 3. Create Web App
```bash
az webapp create \
  --resource-group pawmatch-rg \
  --plan pawmatch-plan \
  --name pawmatch-app \
  --runtime "PYTHON:3.11" \
  --deployment-local-git
```

### 4. Configure Environment Variables
```bash
az webapp config appsettings set \
  --resource-group pawmatch-rg \
  --name pawmatch-app \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://tette-mhm601bb-eastus2.cognitiveservices.azure.com/" \
    AZURE_OPENAI_API_KEY="your_key_here" \
    AZURE_OPENAI_DEPLOYMENT="gpt-4o-mini" \
    AZURE_OPENAI_API_VERSION="2024-08-01-preview" \
    SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 5. Deploy from GitHub
```bash
az webapp deployment source config \
  --name pawmatch-app \
  --resource-group pawmatch-rg \
  --repo-url https://github.com/Syded74/pawmatch \
  --branch main \
  --manual-integration
```

## Alternative: Deploy with Azure Web App Extension

Using VS Code Azure extension (easier):
1. Install Azure App Service extension
2. Right-click on the project
3. Select "Deploy to Web App"
4. Follow the prompts

## View Your App

After deployment, your app will be available at:
```
https://pawmatch-app.azurewebsites.net
```

## Useful Commands

### View logs
```bash
az webapp log tail --name pawmatch-app --resource-group pawmatch-rg
```

### Restart app
```bash
az webapp restart --name pawmatch-app --resource-group pawmatch-rg
```

### SSH into container
```bash
az webapp ssh --name pawmatch-app --resource-group pawmatch-rg
```

## Cost
Azure for Students includes:
- $100 free credit
- Free App Service tier (F1) available
- B1 tier: ~$13/month (recommended for production)

## Notes
- The app uses gunicorn as specified in Procfile
- Azure will automatically detect Python and install requirements.txt
- Environment variables are set via App Settings
