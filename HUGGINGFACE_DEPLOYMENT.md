# Hugging Face Spaces Deployment Guide

## Why Hugging Face Spaces?
- ✅ 100% FREE
- ✅ Great for AI/ML apps
- ✅ Supports Docker
- ✅ Reliable uptime
- ✅ No credit card needed
- ✅ Good for demos/portfolio

## Deploy Steps:

1. **Go to Hugging Face:**
   https://huggingface.co/spaces

2. **Create New Space:**
   - Click "Create new Space"
   - Name: `pawmatch`
   - License: MIT
   - Select: **Docker**

3. **Connect GitHub Repo:**
   - Settings → Repository
   - Link to: `https://github.com/Syded74/pawmatch-`

4. **Add Secrets (Environment Variables):**
   - Settings → Variables and secrets
   - Add each variable:
     ```
     AZURE_OPENAI_ENDPOINT
     AZURE_OPENAI_API_KEY
     AZURE_OPENAI_DEPLOYMENT
     AZURE_OPENAI_API_VERSION
     PORT=7860
     ```

5. **Spaces will auto-deploy!**
   - Your app URL: `https://huggingface.co/spaces/YOUR_USERNAME/pawmatch`

## Note:
Hugging Face Spaces uses port 7860 by default, so we need to update the Dockerfile.

---

**Want to try this? It's more reliable than Render!**
