"""
Base agent class that all specialized agents will inherit from.
"""
from typing import Dict, List, Any, Optional, Callable
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.utils.react_utils import ReactReasoning

class BaseAgent:
    """
    Base agent class with common functionality.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        model_name: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: The name of the agent
            description: A description of the agent's purpose
            model_name: The name of the LLM model to use
            tools: Optional list of tools available to the agent
            api_key: Optional OpenAI API key
        """
        self.name = name
        self.description = description
        self.model_name = model_name
        self.tools = tools or []
        
        # Initialize the language model
        from src.config import llm_config
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.2,
            api_key=api_key or llm_config.api_key,
            base_url=llm_config.base_url
        )
        
        # Initialize the REACT reasoning framework if tools are provided
        if self.tools:
            self.react = ReactReasoning(self.llm, self.tools)
    
    def add_tool(self, name: str, description: str, func: Callable) -> None:
        """
        Add a tool to the agent.
        
        Args:
            name: The name of the tool
            description: A description of what the tool does
            func: The function to call when the tool is used
        """
        self.tools.append({
            "name": name,
            "description": description,
            "func": func
        })
        
        # Reinitialize the REACT reasoning framework with the updated tools
        self.react = ReactReasoning(self.llm, self.tools)
    
    def run(self, task: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the agent on a task.
        
        Args:
            task: The task to perform
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            The result of the agent's work
        """
        if not hasattr(self, 'react'):
            raise ValueError("Agent has no tools. Add tools using add_tool() before running.")
        
        return self.react.run(task, max_iterations)
    
    def simple_generate(self, prompt_template: str, **kwargs) -> str:
        """
        Generate a simple response without using the REACT framework.
        
        Args:
            prompt_template: The prompt template to use
            **kwargs: Variables to fill in the prompt template
            
        Returns:
            The generated response
        """
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(kwargs)
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name}: {self.description}"