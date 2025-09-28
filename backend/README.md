# AI Data Agent Backend

This is the backend API for the AI Data Agent MVP, built with FastAPI.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration:
- `DATABASE_URL`: Your PostgreSQL connection string
- `HUGGINGFACE_API_KEY`: Your Hugging Face API key

### 3. Database Setup

Make sure you have a PostgreSQL database running. You can use:
- Local PostgreSQL installation
- Neon (free tier) - https://neon.tech
- Supabase (free tier) - https://supabase.com

### 4. Run the Application

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python app/main.py
```

### 5. Test the API

Visit `http://localhost:8000/docs` to see the interactive API documentation.

Test the health endpoint:
```bash
curl http://localhost:8000/health
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/upload` - Upload data files (Excel/CSV)
- `GET /api/v1/schema/{session_id}` - Get schema for uploaded data

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── endpoints.py      # API routes
│   ├── core/
│   │   └── config.py         # Configuration
│   ├── models/
│   │   └── database.py       # Database setup
│   ├── services/
│   │   └── data_processor.py # Data processing logic
│   └── main.py               # FastAPI app
├── requirements.txt
├── Dockerfile
└── .env.example
```
