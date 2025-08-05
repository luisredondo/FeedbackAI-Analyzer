"""
Agent module for the Client Feedback Analyzer.

This module provides a clean interface for the agentic RAG system,
hiding LangGraph implementation details behind a simple API.
"""

from .core import FeedbackAnalyzer

__all__ = ["FeedbackAnalyzer"]