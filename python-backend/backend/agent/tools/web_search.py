"""
Web search tool for the agent.

Provides web search capabilities using Tavily for external information
when internal feedback data is insufficient.
"""

from langchain_community.tools.tavily_search import TavilySearchResults
from ...models.agent import ToolResult


class WebSearchTool:
    """Tool for searching the web for additional information."""
    
    def __init__(self, max_results: int = 3):
        self.max_results = max_results
        self._search_tool = None
    
    def get_search_tool(self):
        """Get the Tavily search tool instance."""
        if self._search_tool is None:
            self._search_tool = TavilySearchResults(max_results=self.max_results)
        return self._search_tool
    
    def search(self, query: str) -> str:
        """Search the web and return relevant information."""
        try:
            search_tool = self.get_search_tool()
            result = search_tool.invoke(query)
            return result
        except Exception as e:
            return f"Error searching the web: {str(e)}"
    
    def search_with_metadata(self, query: str) -> ToolResult:
        """Search the web and return a structured result."""
        try:
            search_tool = self.get_search_tool()
            result = search_tool.invoke(query)
            return ToolResult(
                tool_name="web_search",
                success=True,
                result=str(result),
                metadata={"query": query, "max_results": self.max_results}
            )
        except Exception as e:
            return ToolResult(
                tool_name="web_search",
                success=False,
                result=f"Error searching the web: {str(e)}",
                metadata={"query": query, "error": str(e)}
            )


def create_web_search_tool(max_results: int = 3):
    """Create a LangChain tool wrapper for web search functionality."""
    tool_instance = WebSearchTool(max_results)
    return tool_instance.get_search_tool()