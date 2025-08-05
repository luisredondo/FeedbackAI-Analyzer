"""
Evaluation framework for the Client Feedback Analyzer.

Provides tools for generating golden datasets, comparing retrieval strategies,
and measuring performance using Ragas and LangSmith.
"""

from .golden_dataset import GoldenDatasetGenerator
from .evaluator import RAGEvaluator
from .retrievers import RetrieverFactory

__all__ = ["GoldenDatasetGenerator", "RAGEvaluator", "RetrieverFactory"]