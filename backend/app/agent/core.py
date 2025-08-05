"""
Core agent implementation for the Client Feedback Analyzer.

Provides a clean, simple interface for analyzing user feedback queries
using an agentic RAG system powered by LangGraph.
"""

from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .storage import FeedbackVectorStore
from .tools.feedback_search import create_feedback_search_tool, create_feedback_search_tool_with_retriever
from .tools.web_search import create_web_search_tool
from ..models.agent import AgentConfig


class AgentState(TypedDict):
    """State definition for the LangGraph agent."""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]


class FeedbackAnalyzer:
    """
    Main agent class for analyzing user feedback.
    
    Provides a clean interface that hides LangGraph implementation details
    and returns simple string responses.
    """
    
    def __init__(self, config: AgentConfig = None, custom_retriever=None):
        if config is None:
            config = AgentConfig()
        
        self.config = config
        self.custom_retriever = custom_retriever
        self.vector_store = FeedbackVectorStore(
            csv_path=config.csv_path,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap
        )
        self._agent_executor = None
    
    def get_agent_executor(self):
        """Get the compiled LangGraph agent, initializing if necessary."""
        if self._agent_executor is None:
            self._agent_executor = self._build_agent()
        return self._agent_executor
    
    def _build_agent(self):
        """Build and compile the LangGraph agent."""
        # Create tools - use custom retriever if provided
        if self.custom_retriever:
            feedback_tool = create_feedback_search_tool_with_retriever(self.custom_retriever)
        else:
            feedback_tool = create_feedback_search_tool(self.vector_store)
        
        web_tool = create_web_search_tool(max_results=self.config.max_web_results)
        tools = [feedback_tool, web_tool]
        
        # Create model with tools
        model = ChatOpenAI(
            model=self.config.model_name, 
            temperature=self.config.temperature
        ).bind_tools(tools)
        
        # Define nodes
        def call_model(state: AgentState):
            """The primary agent node that decides on the next action."""
            response = model.invoke(state["messages"])
            return {"messages": [response]}
        
        tool_node = ToolNode(tools)
        
        # Define conditional edge logic
        def should_continue(state: AgentState) -> str:
            """Determines whether to continue with a tool call or end the process."""
            if state["messages"][-1].tool_calls:
                return "continue"
            return "end"
        
        # Build the graph
        graph_builder = StateGraph(AgentState)
        graph_builder.add_node("agent", call_model)
        graph_builder.add_node("action", tool_node)
        graph_builder.set_entry_point("agent")
        graph_builder.add_conditional_edges(
            "agent",
            should_continue,
            {"continue": "action", "end": END},
        )
        graph_builder.add_edge("action", "agent")
        
        return graph_builder.compile()
    
    async def analyze(self, query: str) -> str:
        """
        Analyze a user query and return a response.
        
        This is the main public interface - it takes a query string
        and returns a simple string response, hiding all LangGraph complexity.
        
        Args:
            query: The user's question about feedback
            
        Returns:
            A string response with the analysis
        """
        try:
            agent_executor = self.get_agent_executor()
            inputs = {"messages": [HumanMessage(content=query)]}
            
            # Execute the agent and extract the final response
            final_response = ""
            async for event in agent_executor.astream(inputs):
                for node, values in event.items():
                    # Check for __end__ node (ideal case)
                    if node == "__end__":
                        if "messages" in values and values["messages"]:
                            final_response = values["messages"][-1].content
                    
                    # Also capture from agent node when it has no tool calls (final response)
                    elif node == "agent" and "messages" in values and values["messages"]:
                        last_message = values["messages"][-1]
                        # If the last message has no tool calls, it's the final response
                        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
                            final_response = last_message.content
            
            return final_response or "I apologize, but I couldn't generate a response. Please try again."
            
        except Exception as e:
            return f"An error occurred while analyzing your query: {str(e)}"
    
    def reset(self):
        """Reset the agent (useful for testing)."""
        self._agent_executor = None
        self.vector_store.reset()