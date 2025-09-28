from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from pydantic import BaseModel
from app.models.database import get_db
from app.services.data_processor import data_processor
from app.services.ai_agent import ai_agent
from app.core.config import settings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: str

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Upload and process a data file (Excel or CSV)
    
    Args:
        file: The uploaded file
        db: Database session
        
    Returns:
        Session ID and metadata about processed tables
    """
    # Validate file type
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
        )
    
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    try:
        # Process and store the file
        result = await data_processor.process_and_store_file(file, session_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.get("/schema/{session_id}")
async def get_schema(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get schema information for a session's data
    
    Args:
        session_id: The session identifier
        db: Database session
        
    Returns:
        Schema information for all tables in the session
    """
    try:
        schema_info = data_processor.get_table_schema(session_id)
        return {
            "session_id": session_id,
            "schema": schema_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving schema: {str(e)}")

@router.post("/query")
async def query_data(
    request: QueryRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process natural language query and return AI analysis
    
    Args:
        request: Query request containing query and session_id
        db: Database session
        
    Returns:
        AI analysis with answer, explanation, and visualization suggestions
    """
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )
    
    if not request.session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty"
        )
    
    try:
        # Get AI analysis
        result = ai_agent.get_answer(request.query, request.session_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/credits")
async def get_credit_usage():
    """Get current credit usage statistics"""
    try:
        usage = ai_agent.get_credit_usage()
        return usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving credit usage: {str(e)}")

@router.post("/credits/reset")
async def reset_credit_tracking():
    """Reset credit tracking counters"""
    try:
        ai_agent.reset_credit_tracking()
        return {"message": "Credit tracking reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting credit tracking: {str(e)}")

@router.get("/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "ok", "service": "ai-data-agent-api"}
