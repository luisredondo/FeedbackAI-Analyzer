"""
Vector store management for feedback data.

Handles loading, chunking, and indexing of user feedback data
for semantic search capabilities.
"""

import os
from typing import Optional, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

from ...models.feedback import FeedbackEntry


class FeedbackVectorStore:
    """Manages the vector store for user feedback data."""
    
    def __init__(self, csv_path: str = "backend/data/feedback_corpus.csv", 
                 chunk_size: int = 1000, chunk_overlap: int = 100):
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._vector_store: Optional[Qdrant] = None
        self._retriever = None
    
    def get_retriever(self):
        """Get the retriever for the vector store, initializing if necessary."""
        if self._retriever is None:
            self._retriever = self.get_vector_store().as_retriever()
        return self._retriever
    
    def get_vector_store(self) -> Qdrant:
        """Get the vector store, initializing if necessary."""
        if self._vector_store is None:
            self._vector_store = self._setup_vector_store()
        return self._vector_store
    
    def _setup_vector_store(self) -> Qdrant:
        """Load data, create chunks, and set up a Qdrant vector store."""
        try:
            # Load documents from CSV
            loader = CSVLoader(
                file_path=self.csv_path,
                metadata_columns=["source", "date", "user_id", "sentiment", "feedback_text"],
                csv_args={"delimiter": ","}
            )
            docs = loader.load()
            
            if not docs:
                raise ValueError("No documents loaded from CSV file")
            
            # Use page_content from the 'feedback_text' column
            for doc in docs:
                doc.page_content = doc.metadata.get("feedback_text", "")
            
            # Filter out empty documents
            docs = [doc for doc in docs if doc.page_content and doc.page_content.strip()]
            
            if not docs:
                raise ValueError("No valid documents with content found")
            
            # Create text chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size, 
                chunk_overlap=self.chunk_overlap
            )
            chunks = text_splitter.split_documents(docs)
            
            if not chunks:
                raise ValueError("No chunks created from documents")
            
            # Create embeddings and vector store
            embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            
            vector_store = Qdrant.from_documents(
                chunks,
                embeddings,
                location=":memory:",
                collection_name="client_feedback",
            )
            
            print(f"Vector store initialized with {len(chunks)} chunks")
            return vector_store
            
        except Exception as e:
            print(f"Error setting up vector store: {e}")
            raise
    
    def reset(self):
        """Reset the vector store and retriever (useful for testing)."""
        self._vector_store = None
        self._retriever = None