"""
Request models for the API.

Contains Pydantic models for all incoming API requests.
"""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for feedback analysis queries."""
    
    query: str = Field(
        ...,
        description="The user's question about feedback data",
        min_length=1,
        max_length=1000,
        example="What are the main complaints about the dashboard?"
    )