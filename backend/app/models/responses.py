"""
Response models for the API.

Contains Pydantic models for all API responses.
"""

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Response model for feedback analysis results."""
    
    response: str = Field(
        ...,
        description="The agent's analysis of the feedback query",
        example="The main dashboard complaints include navigation issues, complexity, and layout confusion."
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(
        ...,
        description="Health status of the service",
        example="ok"
    )