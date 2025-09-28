# 🤖 AI Data Agent

A modern, intelligent data analysis platform that transforms your CSV/Excel files into actionable insights through conversational AI.

## ✨ Features

- **📊 Smart Data Analysis** - Upload CSV/Excel files and get instant AI-powered insights
- **💬 Conversational Interface** - Ask questions about your data in natural language
- **📈 Interactive Charts** - Generate beautiful visualizations (bar, pie, line, scatter, area charts)
- **🔑 Flexible API Keys** - Use your own Gemini API key or try with our demo key
- **🎨 Modern UI** - Responsive, professional interface with smooth animations
- **⚡ Real-time Processing** - Fast data processing with multi-model AI fallback

## 🚀 Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- Vite for development

**Backend:**
- FastAPI (Python)
- Google Gemini AI (2.5 Pro, Flash, Flash-Lite)
- SQLite/PostgreSQL database
- Multi-API key support with automatic fallback

## 🛠️ Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/KakashiShirin/cordly-ai.git
   cd cordly-ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   python -m uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Add your Gemini API key** (optional - demo key available)

## 📱 Usage

1. Upload your CSV/Excel file
2. Ask questions like:
   - "Show me a pie chart of department distribution"
   - "What's the average salary by location?"
   - "Which department has the highest performance scores?"

## 🎯 Perfect For

- **Data Analysts** - Quick insights from datasets
- **Business Users** - No-code data exploration
- **Students** - Learning data analysis concepts
- **Developers** - AI-powered data processing

## 🔧 Configuration

- **API Keys**: Add your Gemini API key in the API Keys section
- **File Formats**: Supports CSV, XLS, XLSX (up to 10MB)
- **Models**: Gemini 2.5 Pro → Flash → Flash-Lite (automatic fallback)

## 📄 License

MIT License - feel free to use and modify!

---

**Made with ❤️ by [Naga Sai Kanishka](https://github.com/KakashiShirin)**

*Data Scientist and AI Enthusiast*
