"""
Retriever factory for creating different retrieval strategies.

Provides a centralized way to create and configure various retrieval methods.
"""

from typing import List, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank


class RetrieverFactory:
    """Factory class for creating different types of retrievers."""
    
    def __init__(self, documents: List[Any]):
        self.documents = documents
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        
        # Create base vector store and chunks
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.chunks = self.text_splitter.split_documents(documents)
        self.vector_store = Qdrant.from_documents(
            self.chunks, 
            self.embeddings, 
            location=":memory:", 
            collection_name="feedback_chunks"
        )
        print(f"Initialized vector store with {len(self.chunks)} chunks")
    
    def create_naive_retriever(self, k: int = 10):
        """Create a simple vector similarity retriever."""
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def create_bm25_retriever(self, k: int = 10):
        """Create a BM25 (keyword-based) retriever."""
        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = k
        return bm25_retriever
    
    def create_multi_query_retriever(self, base_k: int = 10):
        """Create a multi-query retriever that generates multiple search queries."""
        base_retriever = self.vector_store.as_retriever(search_kwargs={"k": base_k})
        return MultiQueryRetriever.from_llm(retriever=base_retriever, llm=self.llm)
    
    def create_parent_document_retriever(self):
        """Create a parent-document retriever with hierarchical chunking."""
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)
        store = InMemoryStore()
        
        parent_retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
        )
        parent_retriever.add_documents(self.documents)
        return parent_retriever
    
    def create_rerank_retriever(self, base_k: int = 20):
        """Create a retriever with Cohere reranking."""
        import os
        if not os.getenv("COHERE_API_KEY"):
            raise ValueError("COHERE_API_KEY environment variable is required for rerank retriever")
        
        base_retriever = self.vector_store.as_retriever(search_kwargs={"k": base_k})
        compressor = CohereRerank()
        return ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=base_retriever
        )
    
    def create_ensemble_retriever(self, k: int = 10):
        """Create an ensemble retriever combining BM25 and vector search."""
        bm25_retriever = self.create_bm25_retriever(k)
        vector_retriever = self.create_naive_retriever(k)
        
        return EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )
    
    def get_available_retrievers(self) -> dict:
        """Get a dictionary of all available retrievers."""
        return {
            "naive": self.create_naive_retriever,
            "bm25": self.create_bm25_retriever,
            "multi_query": self.create_multi_query_retriever,
            "parent_document": self.create_parent_document_retriever,
            "rerank": self.create_rerank_retriever,
            "ensemble": self.create_ensemble_retriever
        }