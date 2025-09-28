from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from pydantic import BaseModel
from app.models.database import get_db
from app.services.data_processor import data_processor
from app.services.ai_agent import ai_agent
from app.services.chat_session_manager import chat_session_manager
from app.core.config import settings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: str

class ApiKeyRequest(BaseModel):
    api_key: str

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
        # Get AI analysis with task breakdown for complex queries
        result = ai_agent.get_answer_with_task_breakdown(request.query, request.session_id)
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

@router.post("/api-keys/add")
async def add_api_key(request: ApiKeyRequest):
    """Add a new Gemini API key to the pool"""
    try:
        success = ai_agent.add_gemini_api_key(request.api_key)
        if success:
            return {"message": "API key added successfully", "total_keys": len(ai_agent.gemini_api_keys)}
        else:
            raise HTTPException(status_code=400, detail="Failed to add API key")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding API key: {str(e)}")

@router.get("/api-keys/status")
async def get_api_keys_status():
    """Get status of all API keys"""
    try:
        usage = ai_agent.get_credit_usage()
        return {
            "total_api_keys": len(ai_agent.gemini_api_keys),
            "api_key_usage": usage["api_key_usage"],
            "total_calls": usage["total_api_calls"],
            "total_tokens": usage["total_tokens_used"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting API key status: {str(e)}")

@router.post("/api-keys/validate")
async def validate_api_key(request: ApiKeyRequest):
    """Validate a Gemini API key without adding it"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=request.api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        test_response = model.generate_content("test")
        
        return {
            "valid": True,
            "message": "API key is valid and working"
        }
    except Exception as e:
        return {
            "valid": False,
            "message": f"API key validation failed: {str(e)}"
        }

@router.get("/health")
async def api_health_check():
    """API health check endpoint"""
    return {"status": "ok", "service": "ai-data-agent-api"}

# Chat Session Management Endpoints

class ChatRequest(BaseModel):
    query: str
    chat_id: str

class CreateChatRequest(BaseModel):
    database_session_id: str

@router.post("/chat/create")
async def create_chat_session(request: CreateChatRequest):
    """Create a new chat session for a specific database session"""
    try:
        chat_id = chat_session_manager.create_chat_session(request.database_session_id)
        return {
            "chat_id": chat_id,
            "database_session_id": request.database_session_id,
            "message": "Chat session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating chat session: {str(e)}")

@router.post("/chat/query")
async def chat_query(request: ChatRequest):
    """Process a query within a specific chat session context"""
    try:
        if not request.chat_id:
            raise HTTPException(status_code=400, detail="Chat ID is required")
        
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process query with chat context
        result = ai_agent.get_answer_with_chat_context(request.query, request.chat_id)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat query: {str(e)}")

@router.get("/chat/{chat_id}/context")
async def get_chat_context(chat_id: str):
    """Get the context of a specific chat session"""
    try:
        context = chat_session_manager.get_chat_context(chat_id)
        if context is None:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return {
            "chat_id": chat_id,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat context: {str(e)}")

@router.get("/chat/sessions")
async def get_chat_sessions():
    """Get all active chat sessions"""
    try:
        stats = chat_session_manager.get_session_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat sessions: {str(e)}")

@router.delete("/chat/{chat_id}")
async def delete_chat_session(chat_id: str):
    """Delete a specific chat session"""
    try:
        success = chat_session_manager.delete_chat_session(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        return {
            "chat_id": chat_id,
            "message": "Chat session deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chat session: {str(e)}")

@router.post("/chat/cleanup")
async def cleanup_expired_sessions():
    """Clean up expired chat sessions"""
    try:
        cleaned_count = chat_session_manager.cleanup_expired_sessions()
        return {
            "cleaned_sessions": cleaned_count,
            "message": f"Cleaned up {cleaned_count} expired sessions"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up sessions: {str(e)}")

@router.post("/cleanup/all")
async def clear_all_data(db: Session = Depends(get_db)):
    """Clear all data including sessions, uploaded data, and analysis history"""
    try:
        # Clear all chat sessions
        chat_sessions_cleared = chat_session_manager.clear_all_sessions()
        
        # Clear all uploaded data and database sessions
        data_sessions_cleared = data_processor.clear_all_data()
        
        # Reset AI agent state
        ai_agent.reset_credit_tracking()
        
        return {
            "message": "All data cleared successfully",
            "cleared_sessions": chat_sessions_cleared + data_sessions_cleared,
            "cleared_data": data_sessions_cleared
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing all data: {str(e)}")

@router.get("/model/status")
async def get_model_status():
    """Get current AI model status and configuration"""
    try:
        return {
            "current_model": ai_agent.current_model_name,
            "primary_model": ai_agent.primary_model_name,
            "fallback_model": ai_agent.fallback_model_name,
            "tertiary_model": ai_agent.tertiary_model_name,
            "is_using_fallback": ai_agent.current_model_name != ai_agent.primary_model_name,
            "model_tier": "pro" if ai_agent.current_model_name == ai_agent.primary_model_name else 
                         "flash" if ai_agent.current_model_name == ai_agent.fallback_model_name else "flash-lite",
            "api_keys_count": len(ai_agent.gemini_api_keys),
            "total_calls": ai_agent.api_call_count,
            "total_tokens": ai_agent.total_tokens_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model status: {str(e)}")

@router.post("/model/reset")
async def reset_to_primary_model():
    """Reset AI model to primary model (Gemini 2.5 Pro)"""
    try:
        ai_agent.reset_to_primary_model()
        return {
            "message": "Model reset to primary model",
            "current_model": ai_agent.current_model_name,
            "primary_model": ai_agent.primary_model_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting model: {str(e)}")
