# 🚀 Vercel Deployment Guide

## 📋 Overview

This guide will help you deploy your AI Data Agent to Vercel (frontend) and Railway (backend).

## 🎯 Deployment Architecture

```
Frontend (React + Vite) → Vercel
Backend (FastAPI + Python) → Railway
```

---

## **Step 1: Deploy Backend to Railway**

### 1.1 Create Railway Account
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your GitHub account

### 1.2 Deploy Backend
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `AI_Chat_agent` repository
4. Select the `backend` folder as the root directory

### 1.3 Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://username:password@host:port/database
DEBUG=False
MAX_FILE_SIZE=10485760
```

### 1.4 Get Backend URL
- Railway will provide a URL like: `https://your-app-name.railway.app`
- Copy this URL for frontend configuration

---

## **Step 2: Deploy Frontend to Vercel**

### 2.1 Create Vercel Account
1. Go to [Vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Connect your GitHub account

### 2.2 Deploy Frontend
1. Click "New Project"
2. Import your `AI_Chat_agent` repository
3. Set the following configuration:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 2.3 Configure Environment Variables
In Vercel dashboard, go to Settings → Environment Variables and add:

```env
VITE_API_URL=https://your-app-name.railway.app
VITE_APP_NAME=AI Data Agent
VITE_APP_VERSION=1.0.0
```

### 2.4 Deploy
1. Click "Deploy"
2. Wait for deployment to complete
3. Get your Vercel URL: `https://your-app-name.vercel.app`

---

## **Step 3: Configure CORS (Backend)**

Add CORS configuration to your backend to allow Vercel frontend:

```python
# In backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://your-app-name.vercel.app",  # Production
        "https://*.vercel.app"  # All Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## **Step 4: Test Deployment**

1. **Test Backend**: Visit `https://your-app-name.railway.app/health`
2. **Test Frontend**: Visit `https://your-app-name.vercel.app`
3. **Test Integration**: Upload a file and run a query

---

## **Step 5: Custom Domain (Optional)**

### 5.1 Vercel Custom Domain
1. Go to Vercel dashboard → Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

### 5.2 Railway Custom Domain
1. Go to Railway dashboard → Settings → Domains
2. Add your custom domain
3. Configure DNS records

---

## **🔧 Troubleshooting**

### Common Issues:

1. **CORS Errors**:
   - Ensure CORS is configured in backend
   - Check that frontend URL is in allowed origins

2. **API Connection Issues**:
   - Verify `VITE_API_URL` is set correctly
   - Check backend is running and accessible

3. **Build Failures**:
   - Check Node.js version (16+)
   - Clear cache: `npm run build -- --force`

4. **Environment Variables**:
   - Ensure all required variables are set
   - Check variable names match exactly

---

## **📊 Monitoring**

### Vercel Analytics
- Enable Vercel Analytics for performance monitoring
- Monitor build times and deployment status

### Railway Monitoring
- Check Railway logs for backend issues
- Monitor resource usage and performance

---

## **🔄 Continuous Deployment**

Both platforms support automatic deployments:
- **Vercel**: Deploys on every push to main branch
- **Railway**: Deploys on every push to main branch

---

## **💰 Cost Considerations**

### Vercel
- **Free Tier**: 100GB bandwidth, unlimited deployments
- **Pro**: $20/month for advanced features

### Railway
- **Free Tier**: $5 credit monthly
- **Pro**: Pay-as-you-use pricing

---

## **🎉 Success!**

Your AI Data Agent is now live and accessible worldwide!

- **Frontend**: `https://your-app-name.vercel.app`
- **Backend**: `https://your-app-name.railway.app`
- **API Docs**: `https://your-app-name.railway.app/docs`
