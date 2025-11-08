# 🚀 PawMatcher Deployment Guide

## ✅ What's Ready

Your app is **100% ready to deploy** with:
- ✅ **11,845 dog breed images** uploaded to Azure Blob Storage
- ✅ **Azure Storage URL**: https://pawmatchstorage2024.blob.core.windows.net/dog-breeds/
- ✅ **177 dog breeds** mapped and working
- ✅ **Smart dual-mode chatbot** (batch + interactive)
- ✅ **WhatsApp sharing** (mobile/desktop optimized)
- ✅ **All dependencies** in requirements.txt

---

## 🎯 Choose Your Platform

### **Option 1: Railway.app** ⭐ RECOMMENDED (with GitHub Student Pack)
**Cost**: FREE with Student Pack ($5/month credit)  
**Always-On**: ✅ Yes  
**Setup Time**: 5 minutes

### **Option 2: Render.com** 💚 EASIEST (No card, free forever)
**Cost**: FREE forever  
**Always-On**: ❌ Sleeps after 15 min  
**Setup Time**: 5 minutes

### **Option 3: Heroku** 🟣 RELIABLE (Paid option)
**Cost**: $7/month (Basic tier)  
**Always-On**: ✅ Yes  
**Setup Time**: 10 minutes

---

## 📦 Step 1: Initialize Git (Required for all platforms)

```bash
# Navigate to project directory
cd /Users/m2/Downloads/pawmatcher

# Initialize Git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - PawMatcher ready for deployment"
```

---

## 🚂 OPTION 1: Deploy to Railway.app

### Prerequisites:
- GitHub Student Pack: https://education.github.com/pack
- GitHub account

### Steps:

1. **Push to GitHub**:
```bash
# Create new repo on GitHub: https://github.com/new
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/pawmatcher.git
git branch -M main
git push -u origin main
```

2. **Deploy on Railway**:
   - Go to https://railway.app
   - Sign up with GitHub (apply Student Pack discount)
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select `pawmatcher` repo
   - Railway auto-detects Python and uses `requirements.txt`

3. **Add Environment Variables** in Railway dashboard:
   - `AZURE_OPENAI_API_KEY` = [Your key]
   - `AZURE_OPENAI_ENDPOINT` = [Your endpoint]
   - `AZURE_OPENAI_DEPLOYMENT_NAME` = [e.g., gpt-4o-mini]
   - `AZURE_STORAGE_ACCOUNT` = `pawmatchstorage2024`
   - `AZURE_STORAGE_CONTAINER` = `dog-breeds`

4. **Deploy**:
   - Railway automatically builds and deploys
   - Get your URL: `https://pawmatcher.up.railway.app`

**Done!** ✅ Your app is live and always-on.

---

## 💚 OPTION 2: Deploy to Render.com

### Prerequisites:
- GitHub account (or deploy without GitHub)

### Steps:

1. **Push to GitHub** (recommended):
```bash
# Create new repo on GitHub: https://github.com/new
git remote add origin https://github.com/YOUR_USERNAME/pawmatcher.git
git branch -M main
git push -u origin main
```

2. **Deploy on Render**:
   - Go to https://render.com and sign up (no card needed)
   - Click **"New +"** → **"Web Service"**
   - Connect GitHub repo OR use "Public Git repository"
   - Render detects `render.yaml` automatically

3. **Configure** (if not using render.yaml):
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment**: Python 3

4. **Add Environment Variables** in Render dashboard:
   - `AZURE_OPENAI_API_KEY` = [Your key]
   - `AZURE_OPENAI_ENDPOINT` = [Your endpoint]
   - `AZURE_OPENAI_DEPLOYMENT_NAME` = [e.g., gpt-4o-mini]
   - `AZURE_STORAGE_ACCOUNT` = `pawmatchstorage2024`
   - `AZURE_STORAGE_CONTAINER` = `dog-breeds`

5. **Deploy**:
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Get your URL: `https://pawmatcher.onrender.com`

**Note**: Free tier sleeps after 15 min of inactivity (30s wake-up time).

---

## 🟣 OPTION 3: Deploy to Heroku

### Prerequisites:
- Heroku account: https://signup.heroku.com
- Heroku CLI: `brew install heroku/brew/heroku`

### Steps:

1. **Login to Heroku**:
```bash
heroku login
```

2. **Create Heroku app**:
```bash
heroku create pawmatcher-app
```

3. **Add Procfile**:
```bash
echo "web: gunicorn app:app" > Procfile
git add Procfile
git commit -m "Add Procfile for Heroku"
```

4. **Set Environment Variables**:
```bash
heroku config:set AZURE_OPENAI_API_KEY="your-key"
heroku config:set AZURE_OPENAI_ENDPOINT="your-endpoint"
heroku config:set AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"
heroku config:set AZURE_STORAGE_ACCOUNT="pawmatchstorage2024"
heroku config:set AZURE_STORAGE_CONTAINER="dog-breeds"
```

5. **Deploy**:
```bash
git push heroku main
```

6. **Open app**:
```bash
heroku open
```

**Cost**: $7/month for Basic tier (always-on)

---

## 🔧 Environment Variables Needed

All platforms require these environment variables:

```bash
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_STORAGE_ACCOUNT=pawmatchstorage2024
AZURE_STORAGE_CONTAINER=dog-breeds
```

---

## 🧪 Test Locally Before Deploying

```bash
# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export AZURE_OPENAI_API_KEY="your-key"
export AZURE_OPENAI_ENDPOINT="your-endpoint"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o-mini"
export AZURE_STORAGE_ACCOUNT="pawmatchstorage2024"
export AZURE_STORAGE_CONTAINER="dog-breeds"

# Run app
python app.py
```

Visit http://localhost:5000 and verify:
- ✅ Images load from Azure Blob Storage
- ✅ Chatbot works (try batch mode: "I want active, friendly, medium-sized dog")
- ✅ Breed matching generates results
- ✅ WhatsApp sharing works

---

## 📊 Platform Comparison Summary

| Feature | Railway (Student) | Render (Free) | Heroku (Basic) |
|---------|-------------------|---------------|----------------|
| **Cost** | $0 | $0 | $7/mo |
| **Always-On** | ✅ Yes | ❌ No (sleeps) | ✅ Yes |
| **Setup** | Easy | Easy | Medium |
| **Performance** | ⚡ Fast | 🐢 Slower | ⚡ Fast |
| **Best For** | Students | Testing/Demo | Production |

---

## 🐛 Troubleshooting

### Images not loading?
- Check environment variables are set correctly
- Verify Azure Blob Storage container has public access
- Check browser console for CORS errors

### Build fails?
- Ensure `requirements.txt` is in root directory
- Check Python version compatibility (3.9+)
- Review build logs for missing dependencies

### App crashes on startup?
- Verify all environment variables are set
- Check that Flask port binding is correct (`0.0.0.0`)
- Review application logs

---

## 🎉 After Deployment

Once deployed, test these features:
1. **Breed matching** - Chat with bot and get recommendations
2. **Batch mode** - "I want large, friendly, low-energy dog"
3. **Interactive mode** - Answer questions one by one
4. **WhatsApp sharing** - Share results via WhatsApp
5. **Image loading** - Verify all breed images display correctly

---

## 📱 Share Your App

After deployment, you'll get a URL like:
- Railway: `https://pawmatcher.up.railway.app`
- Render: `https://pawmatcher.onrender.com`
- Heroku: `https://pawmatcher-app.herokuapp.com`

Share it with friends and test the WhatsApp sharing feature!

---

## 💡 Next Steps

1. Monitor usage and performance
2. Consider upgrading if traffic increases
3. Add custom domain (optional)
4. Set up monitoring/analytics
5. Gather user feedback

**Your app is ready to go live! Choose a platform and deploy! 🚀**
