"""
API routes for Cordly AI
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any

from models.schemas import AskRequest, AskResponse, ErrorResponse
from services.ai_service import AIService
from services.db_service import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter()

def get_ai_service() -> AIService:
    """Dependency to get AI service from app state"""
    from main import app
    return app.state.ai_service

def get_db_service() -> DatabaseService:
    """Dependency to get database service from app state"""
    from main import app
    return app.state.db_service

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Process a natural language question and return insights with visualizations
    
    This endpoint:
    1. Converts natural language to SQL
    2. Executes the query against the database
    3. Generates a natural language summary
    4. Creates appropriate visualizations
    5. Returns structured data for the frontend
    """
    try:
        logger.info(f"Processing question: {request.question}")
        
        start_time = time.time()
        
        # Process the question using AI service
        result = await ai_service.process_question(request.question)
        
        execution_time = time.time() - start_time
        
        # Add execution time to result
        result["executionTime"] = execution_time
        
        logger.info(f"Question processed successfully in {execution_time:.2f}s")
        
        return AskResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Processing failed",
                "message": str(e)
            }
        )

@router.get("/schema")
async def get_database_schema(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Get database schema information
    
    Returns information about tables, columns, and relationships
    for use by the AI model in generating SQL queries.
    """
    try:
        schema = await db_service.get_schema_info()
        return {"schema": schema}
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Schema retrieval failed",
                "message": str(e)
            }
        )

@router.get("/tables")
async def get_tables(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Get list of available tables
    """
    try:
        tables = await db_service.get_tables()
        return {"tables": tables}
        
    except Exception as e:
        logger.error(f"Error getting tables: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Table retrieval failed",
                "message": str(e)
            }
        )

@router.get("/sample-queries")
async def get_sample_queries():
    """
    Get sample questions that users can ask
    """
    sample_queries = [
        "What are the top 5 product categories by revenue?",
        "Which states have the highest average order value?",
        "How many orders were placed each month in 2017?",
        "What is the distribution of payment methods?",
        "Which sellers have the highest customer satisfaction?",
        "What are the most popular products in São Paulo?",
        "How does order volume vary by day of the week?",
        "What is the average delivery time by state?",
        "Which product categories have the highest profit margins?",
        "How many customers made repeat purchases?"
    ]
    
    return {"sample_queries": sample_queries}
