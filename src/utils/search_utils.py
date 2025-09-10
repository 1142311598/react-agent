"""
Utility functions for search operations using Tavily.
"""
from typing import List, Dict, Any, Optional
import json

class TavilySearchTool:
    """
    A tool for searching the web using the Tavily API.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Tavily search tool.
        
        Args:
            api_key: The Tavily API key
        """
        try:
            from tavily import TavilyClient
            if api_key:
                self.client = TavilyClient(api_key=api_key)
            else:
                # Will use TAVILY_API_KEY environment variable
                self.client = TavilyClient()
        except ImportError:
            raise ImportError(
                "Could not import tavily python package. "
                "Please install it with `pip install tavily-python`."
            )
    
    def search(self, query: str, max_results: int = 10, search_depth: str = "basic") -> List[Dict[str, Any]]:
        """
        Search the web using Tavily.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
            search_depth: The search depth ('basic' or 'comprehensive')
            
        Returns:
            A list of search results
        """
        response = self.client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth
        )
        return response.get("results", [])
    
    def search_with_context(self, query: str, context: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web using Tavily with additional context.
        
        Args:
            query: The search query
            context: Additional context to guide the search
            max_results: Maximum number of results to return
            
        Returns:
            A list of search results
        """
        full_query = f"{query}\nContext: {context}"
        return self.search(full_query, max_results)
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: The search results to format
            
        Returns:
            A formatted string of search results
        """
        if not results:
            return "No results found."
        
        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result.get('title', 'No title')}\n"
            formatted += f"   URL: {result.get('url', 'No URL')}\n"
            formatted += f"   Content: {result.get('content', 'No content')[:200]}...\n\n"
        
        return formatted
    
    def __call__(self, query: str) -> str:
        """
        Make the class callable to use as a tool.
        
        Args:
            query: The search query
            
        Returns:
            Formatted search results
        """
        try:
            results = self.search(query)
            return self.format_results(results)
        except Exception as e:
            return f"Error performing search: {str(e)}"