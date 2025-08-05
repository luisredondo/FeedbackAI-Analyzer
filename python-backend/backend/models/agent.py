"""
Agent-related models.

Contains Pydantic models for agent configuration and results.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Configuration model for the feedback analyzer agent."""
    
    csv_path: str = Field(
        default="backend/data/feedback_corpus.csv",
        description="Path to the feedback CSV file"
    )
    
    model_name: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model to use for the agent"
    )
    
    temperature: float = Field(
        default=0.0,
        description="Temperature setting for the model",
        ge=0.0,
        le=2.0
    )
    
    max_web_results: int = Field(
        default=3,
        description="Maximum number of web search results",
        ge=1,
        le=10
    )
    
    chunk_size: int = Field(
        default=1000,
        description="Size of text chunks for vector store",
        ge=100,
        le=5000
    )
    
    chunk_overlap: int = Field(
        default=100,
        description="Overlap between text chunks",
        ge=0,
        le=500
    )


class ToolResult(BaseModel):
    """Model representing the result of a tool execution."""
    
    tool_name: str = Field(
        ...,
        description="Name of the tool that was executed"
    )
    
    success: bool = Field(
        ...,
        description="Whether the tool execution was successful"
    )
    
    result: str = Field(
        ...,
        description="The result or error message from the tool"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the tool execution"
    )