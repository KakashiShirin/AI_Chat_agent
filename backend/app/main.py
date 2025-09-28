from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router

app = FastAPI(
    title="AI Data Agent API",
    description="Backend API for AI Data Agent MVP",
    version="1.0.0"
)

# Configure CORS
import os
import logging

# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
if os.getenv("ENVIRONMENT") == "production":
    # Add common production domains - use specific patterns
    allowed_origins.extend([
        "https://ai-data-agent-frontend.vercel.app",
        "https://ai-data-agent-frontend-git-main.vercel.app",
        "https://csv-chat-agent.vercel.app",
        "https://csv-chat-agent-git-main.vercel.app",
        "https://csvchatagent-p1jpqslns-primetrades-projects-4edfb7c9.vercel.app",  # Your specific domain
        "https://*.vercel.app",
        "https://*.netlify.app",
        "https://*.railway.app"
    ])

# Log CORS configuration for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"[CORS] Environment: {os.getenv('ENVIRONMENT', 'development')}")
logger.info(f"[CORS] Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
