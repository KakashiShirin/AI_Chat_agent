# Manual Testing Checklist

## 🧪 **Complete Testing Guide**

### **Prerequisites**
- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:3000
- [ ] Valid Gemini API key
- [ ] Test data file (test_data.csv)

### **Step 1: Backend Health Check**
```bash
curl http://localhost:8000/api/v1/health
```
**Expected:** `{"status": "healthy"}`

### **Step 2: Frontend Access**
- Open http://localhost:3000
- **Expected:** AI Data Agent interface loads

### **Step 3: API Key Management**
1. Go to "API Keys" tab
2. Add your Gemini API key
3. **Expected:** "API key added successfully"

### **Step 4: File Upload**
1. Go to "Upload" tab
2. Upload test_data.csv
3. **Expected:** File uploads successfully, session ID generated

### **Step 5: Data Schema**
1. Go to "Data" tab
2. **Expected:** Table schema displayed with columns

### **Step 6: AI Chat**
1. Go to "Chat" tab
2. Ask: "What is the average salary?"
3. **Expected:** AI provides analysis with answer

### **Step 7: Data Visualization**
1. Go to "Data" tab
2. **Expected:** Charts and sample data displayed

### **Step 8: Credit Tracking**
1. Go to "API Keys" tab
2. **Expected:** Usage statistics displayed

## 🚀 **Deployment Testing**

### **Backend Deployment (Railway)**
1. Push to GitHub
2. Connect to Railway
3. Set environment variables:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
4. Deploy
5. Test: `https://your-app.railway.app/api/v1/health`

### **Frontend Deployment (Vercel)**
1. Push to GitHub
2. Connect to Vercel
3. Set environment variable:
   - `VITE_API_URL=https://your-backend-url.com`
4. Deploy
5. Test: Visit your Vercel URL

## 🔧 **Troubleshooting**

### **Common Issues:**
- **API Key Invalid:** Get new key from Google AI Studio
- **Database Connection:** Check Supabase connection string
- **CORS Errors:** Ensure backend allows frontend origin
- **File Upload Fails:** Check file size limits
- **AI Queries Fail:** Verify API key has sufficient credits

### **Debug Commands:**
```bash
# Test API key
python backend/test_gemini_key.py YOUR_API_KEY

# Test complete system
python test_complete_system.py

# Check backend logs
python backend/start.py

# Check frontend build
cd frontend && npm run build
```

## 📊 **Performance Testing**

### **Load Testing:**
```bash
# Install artillery
npm install -g artillery

# Run load test
artillery quick --count 10 --num 5 http://localhost:8000/api/v1/health
```

### **File Upload Testing:**
- Test with files up to 10MB
- Test different formats (CSV, XLS, XLSX)
- Test with malformed data

### **AI Query Testing:**
- Test complex queries
- Test with large datasets
- Test error handling

## ✅ **Success Criteria**

- [ ] All endpoints respond correctly
- [ ] File upload works with test data
- [ ] AI queries return meaningful results
- [ ] Frontend displays data correctly
- [ ] API key management works
- [ ] Credit tracking is accurate
- [ ] Error handling is graceful
- [ ] Performance is acceptable (< 30s for queries)
