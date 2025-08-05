"""
Feedback search tool for the agent.

Provides semantic search capabilities over the internal feedback database
using RAG (Retrieval-Augmented Generation).
"""

from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from ..storage import FeedbackVectorStore
from ...models.agent import ToolResult


class FeedbackSearchTool:
    """Tool for searching and analyzing internal feedback data."""
    
    def __init__(self, vector_store: FeedbackVectorStore):
        self.vector_store = vector_store
        self._rag_chain = None
    
    def get_rag_chain(self):
        """Lazily create and return the RAG chain."""
        if self._rag_chain is None:
            prompt = ChatPromptTemplate.from_template(
                "Answer the user's question based ONLY on the following context:\n\n{context}\n\nQuestion: {question}"
            )
            
            self._rag_chain = (
                {"context": self.vector_store.get_retriever(), "question": RunnablePassthrough()}
                | prompt
                | ChatOpenAI(model="gpt-4o-mini")
                | StrOutputParser()
            )
        return self._rag_chain
    
    def search(self, query: str) -> str:
        """Search the feedback database and return relevant information."""
        try:
            rag_chain = self.get_rag_chain()
            result = rag_chain.invoke(query)
            return result
        except Exception as e:
            error_msg = f"Error searching feedback database: {str(e)}"
            return error_msg
    
    def search_with_metadata(self, query: str) -> ToolResult:
        """Search the feedback database and return a structured result."""
        try:
            rag_chain = self.get_rag_chain()
            result = rag_chain.invoke(query)
            return ToolResult(
                tool_name="feedback_search",
                success=True,
                result=result,
                metadata={"query": query}
            )
        except Exception as e:
            return ToolResult(
                tool_name="feedback_search",
                success=False,
                result=f"Error searching feedback database: {str(e)}",
                metadata={"query": query, "error": str(e)}
            )


def create_feedback_search_tool(vector_store: FeedbackVectorStore):
    """Create a LangChain tool wrapper for the feedback search functionality."""
    tool_instance = FeedbackSearchTool(vector_store)
    
    @tool
    def feedback_search_tool(query: str) -> str:
        """Searches and analyzes the internal user feedback knowledge base to answer questions about user complaints, feature requests, or sentiment."""
        return tool_instance.search(query)
    
    return feedback_search_tool


def create_feedback_search_tool_with_retriever(custom_retriever):
    """Create a LangChain tool wrapper using a custom retriever."""
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.output_parsers import StrOutputParser
    from langchain_openai import ChatOpenAI
    
    # Create a simple RAG chain with the custom retriever
    rag_prompt = ChatPromptTemplate.from_template(
        "Answer the user's question based ONLY on the following context:\\n\\n{context}\\n\\nQuestion: {question}"
    )
    
    rag_chain = (
        {"context": custom_retriever, "question": RunnablePassthrough()}
        | rag_prompt
        | ChatOpenAI(model="gpt-4o-mini")
        | StrOutputParser()
    )
    
    @tool
    def feedback_search_tool(query: str) -> str:
        """Searches and analyzes the internal user feedback knowledge base to answer questions about user complaints, feature requests, or sentiment."""
        try:
            return rag_chain.invoke(query)
        except Exception as e:
            return f"Error searching feedback database: {str(e)}"
    
    return feedback_search_tool