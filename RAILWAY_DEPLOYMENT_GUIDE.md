# 🚂 Railway Backend Deployment Guide

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ GitHub repository with your code
- ✅ Gemini API key
- ✅ Railway account (free tier available)

---

## **Step 1: Create Railway Account**

1. **Go to Railway**: Visit [railway.app](https://railway.app)
2. **Sign Up**: Click "Sign Up" or "Login"
3. **Choose GitHub**: Select "Continue with GitHub"
4. **Authorize**: Allow Railway to access your GitHub repositories
5. **Complete Setup**: Fill in your profile information

---

## **Step 2: Create New Project**

1. **Dashboard**: Once logged in, you'll see the Railway dashboard
2. **New Project**: Click the big "+" button or "New Project"
3. **Deploy from GitHub**: Select "Deploy from GitHub repo"
4. **Select Repository**: Choose your `AI_Chat_agent` repository
5. **Configure**: Railway will detect it's a Python project

---

## **Step 3: Configure Project Settings**

### 3.1 Set Root Directory
1. **Project Settings**: Click on your project name
2. **Settings Tab**: Go to "Settings"
3. **Root Directory**: Set to `backend`
   - This tells Railway to look in the `backend` folder for your Python code

### 3.2 Configure Build Settings
Railway should auto-detect:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## **Step 4: Add Environment Variables**

1. **Variables Tab**: Click on "Variables" in your project
2. **Add Variables**: Click "New Variable" for each:

### Required Variables:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
ENVIRONMENT=production
PORT=8000
```

### Optional Variables:
```env
DEBUG=False
MAX_FILE_SIZE=10485760
DATABASE_URL=postgresql://username:password@host:port/database
```

### How to Add Each Variable:
1. Click "New Variable"
2. **Name**: `GEMINI_API_KEY`
3. **Value**: Paste your actual Gemini API key
4. Click "Add"
5. Repeat for other variables

---

## **Step 5: Deploy**

1. **Deploy Button**: Click "Deploy" or Railway will auto-deploy
2. **Build Process**: Watch the build logs
3. **Wait**: This can take 2-5 minutes
4. **Success**: You'll see "Deployed successfully"

---

## **Step 6: Get Your Backend URL**

1. **Deployments Tab**: Click on "Deployments"
2. **Copy URL**: Click the copy button next to your domain
3. **URL Format**: `https://your-app-name.railway.app`
4. **Test**: Visit `https://your-app-name.railway.app/health`

---

## **Step 7: Configure Custom Domain (Optional)**

1. **Settings**: Go to project settings
2. **Domains**: Click "Domains" tab
3. **Add Domain**: Enter your custom domain
4. **DNS**: Configure DNS records as instructed

---

## **🔧 Troubleshooting Common Issues**

### Issue 1: Build Fails
**Error**: `ModuleNotFoundError` or `pip install` fails
**Solution**:
1. Check `requirements.txt` exists in `backend/` folder
2. Ensure all dependencies are listed
3. Check Railway build logs for specific errors

### Issue 2: App Won't Start
**Error**: `uvicorn` not found or port issues
**Solution**:
1. Verify start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
2. Check `app/main.py` exists
3. Ensure FastAPI app is properly configured

### Issue 3: Environment Variables Not Working
**Error**: API key not found or CORS issues
**Solution**:
1. Double-check variable names (case-sensitive)
2. Ensure `ENVIRONMENT=production` is set
3. Redeploy after adding variables

### Issue 4: CORS Errors
**Error**: Frontend can't connect to backend
**Solution**:
1. Add your frontend domain to `ALLOWED_ORIGINS`
2. Set `ENVIRONMENT=production`
3. Redeploy backend

### Issue 5: Database Issues
**Error**: Database connection fails
**Solution**:
1. Railway provides PostgreSQL by default
2. Add `DATABASE_URL` variable
3. Or use SQLite (default) for simple deployments

---

## **📊 Monitoring Your Deployment**

### View Logs:
1. **Deployments Tab**: Click on your deployment
2. **Logs**: View real-time logs
3. **Debug**: Check for errors or warnings

### Health Check:
- Visit: `https://your-app-name.railway.app/health`
- Should return: `{"status": "ok"}`

### API Documentation:
- Visit: `https://your-app-name.railway.app/docs`
- Interactive API documentation

---

## **💰 Railway Pricing**

### Free Tier:
- $5 credit monthly
- Enough for small projects
- Automatic scaling

### Pro Tier:
- Pay-as-you-use
- More resources
- Custom domains
- Better support

---

## **🔄 Continuous Deployment**

Railway automatically deploys when you:
1. Push to your main branch
2. Make changes to your code
3. Update environment variables

---

## **📝 Quick Checklist**

- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Root directory set to `backend`
- [ ] Environment variables added:
  - [ ] `GEMINI_API_KEY`
  - [ ] `ENVIRONMENT=production`
  - [ ] `PORT=8000`
- [ ] Project deployed successfully
- [ ] Health check passes: `/health`
- [ ] API docs accessible: `/docs`
- [ ] Backend URL copied for frontend

---

## **🎯 Next Steps**

Once your backend is deployed:
1. **Copy the Railway URL** (e.g., `https://your-app.railway.app`)
2. **Deploy frontend to Vercel** using this URL
3. **Test the full application**
4. **Configure custom domains** if needed

---

## **🆘 Need Help?**

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Community**: Railway Discord
- **Support**: Railway support team
- **Logs**: Check deployment logs for specific errors
