"""
Pydantic models for request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class VisualizationType(str, Enum):
    """Supported visualization types"""
    BAR_CHART = "bar_chart"
    LINE_CHART = "line_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    SCATTER_PLOT = "scatter_plot"

class AskRequest(BaseModel):
    """Request model for /api/ask endpoint"""
    question: str = Field(
        ...,
        description="Natural language question about the data",
        example="What are the top 5 product categories by revenue?"
    )

class VisualizationData(BaseModel):
    """Visualization data structure"""
    type: VisualizationType = Field(
        ...,
        description="Type of visualization to render"
    )
    data: List[Dict[str, Any]] = Field(
        ...,
        description="Data points for the visualization"
    )
    dataKey: str = Field(
        ...,
        description="Key for the x-axis/labels"
    )
    barKey: Optional[str] = Field(
        None,
        description="Key for the y-axis/values (for bar charts)"
    )
    title: Optional[str] = Field(
        None,
        description="Title for the visualization"
    )

class TableData(BaseModel):
    """Table data structure"""
    columns: List[str] = Field(
        ...,
        description="Column names"
    )
    rows: List[List[Any]] = Field(
        ...,
        description="Table rows data"
    )

class AskResponse(BaseModel):
    """Response model for /api/ask endpoint"""
    summary: str = Field(
        ...,
        description="Natural language summary of the results"
    )
    visualization: Optional[VisualizationData] = Field(
        None,
        description="Visualization data for charts"
    )
    tableData: Optional[TableData] = Field(
        None,
        description="Table data for detailed results"
    )
    sqlQuery: Optional[str] = Field(
        None,
        description="Generated SQL query (for debugging)"
    )
    executionTime: Optional[float] = Field(
        None,
        description="Query execution time in seconds"
    )

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(
        ...,
        description="Error type"
    )
    message: str = Field(
        ...,
        description="Error message"
    )
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(
        ...,
        description="Service status"
    )
    services: Dict[str, bool] = Field(
        ...,
        description="Status of individual services"
    )
