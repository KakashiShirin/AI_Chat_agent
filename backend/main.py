"""
FastAPI application entry point for Cordly AI - Conversational Business Intelligence
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from api.main import router as api_router
from services.ai_service import AIService
from services.db_service import DatabaseService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
ai_service = None
db_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ai_service, db_service
    
    # Startup
    logger.info("Starting Cordly AI application...")
    
    try:
        # Initialize services
        db_service = DatabaseService()
        await db_service.initialize()
        
        ai_service = AIService(db_service)
        await ai_service.initialize()
        
        # Store services in app state
        app.state.ai_service = ai_service
        app.state.db_service = db_service
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cordly AI application...")
    
    if db_service:
        await db_service.close()
    
    logger.info("Application shutdown completed")

# Create FastAPI app
app = FastAPI(
    title="Cordly AI - Conversational Business Intelligence",
    description="An intelligent conversational interface for business intelligence that allows users to ask complex analytical questions of a SQL database in plain English.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Cordly AI - Conversational Business Intelligence API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "ai_service": ai_service is not None,
            "db_service": db_service is not None
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
