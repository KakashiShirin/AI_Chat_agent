#!/usr/bin/env python3
"""
Startup script for AI Data Agent Backend
"""

import uvicorn
import os
from pathlib import Path

def main():
    """Start the FastAPI application"""
    # Change to the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("🚀 Starting AI Data Agent Backend...")
    print("📍 Backend directory:", backend_dir)
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("-" * 50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
