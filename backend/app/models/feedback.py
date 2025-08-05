"""
Feedback data models.

Contains Pydantic models for representing user feedback data.
"""

from datetime import date as date_type
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FeedbackSentiment(str, Enum):
    """Enumeration of possible feedback sentiments."""
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class FeedbackSource(str, Enum):
    """Enumeration of possible feedback sources."""
    SUPPORT_TICKET = "Support Ticket"
    APP_STORE_REVIEW = "App Store Review"
    SURVEY = "Survey"
    TWITTER_MENTION = "Twitter Mention"


class FeedbackEntry(BaseModel):
    """Model representing a single piece of user feedback."""
    
    feedback_id: str = Field(
        ...,
        description="Unique identifier for the feedback",
        example="FB-001"
    )
    
    source: FeedbackSource = Field(
        ...,
        description="Source of the feedback"
    )
    
    date: date_type = Field(
        ...,
        description="Date when the feedback was received"
    )
    
    user_id: str = Field(
        ...,
        description="Identifier of the user who provided feedback",
        example="user-123"
    )
    
    feedback_text: str = Field(
        ...,
        description="The actual feedback content",
        min_length=1,
        max_length=5000
    )
    
    sentiment: FeedbackSentiment = Field(
        ...,
        description="Sentiment classification of the feedback"
    )
    
    class Config:
        use_enum_values = True