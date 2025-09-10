"""
Utility functions for implementing the REACT (Reasoning and Acting) framework.
"""
from typing import List, Dict, Any, Callable, Optional
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

class ReactReasoning:
    """
    Implementation of the REACT (Reasoning and Acting) framework.
    """
    
    def __init__(self, llm, tools: List[Dict[str, Any]]):
        """
        Initialize the REACT reasoning framework.
        
        Args:
            llm: The language model to use
            tools: List of tools available to the agent
        """
        self.llm = llm
        self.tools = tools
        self.thought_history = []
        self.action_history = []
        self.observation_history = []
        
    def format_tools(self) -> str:
        """Format the tools for inclusion in the prompt."""
        tools_str = ""
        for i, tool in enumerate(self.tools):
            tools_str += f"{i+1}. {tool['name']}: {tool['description']}\n"
        return tools_str
    
    def format_history(self) -> str:
        """Format the reasoning history for inclusion in the prompt."""
        history = ""
        for i in range(len(self.thought_history)):
            history += f"Thought: {self.thought_history[i]}\n"
            if i < len(self.action_history):
                history += f"Action: {self.action_history[i]}\n"
            if i < len(self.observation_history):
                history += f"Observation: {self.observation_history[i]}\n"
        return history
    
    def create_prompt(self) -> PromptTemplate:
        """Create the prompt for the REACT framework."""
        template = """
You are an AI assistant using the REACT (Reasoning and Acting) framework to solve tasks.
You will be given a task, and you need to reason step by step to solve it.

Available tools:
{tools}

Task: {task}

{history}

Think about what to do next. First, explain your reasoning (Thought), then decide on an action to take (Action).
If you believe you have completed the task, you can use the "Final Answer" action to provide your final response.

Thought: 
"""
        return PromptTemplate(
            template=template,
            input_variables=["task", "tools", "history"]
        )
    
    def parse_output(self, output: str) -> Dict[str, str]:
        """
        Parse the output from the LLM into thought and action components.
        
        Args:
            output: The raw output from the LLM
            
        Returns:
            A dictionary containing the parsed thought and action
        """
        lines = output.strip().split('\n')
        thought = ""
        action = ""
        
        # Extract thought
        for i, line in enumerate(lines):
            if line.startswith("Action:"):
                thought = "\n".join(lines[:i]).strip()
                action = "\n".join(lines[i:]).strip()
                break
        
        if not action and thought:
            # If no action was found but there is a thought
            action = "Final Answer: " + thought
            
        return {
            "thought": thought,
            "action": action
        }
    
    def execute_action(self, action: str) -> str:
        """
        Execute the specified action using the available tools.
        
        Args:
            action: The action to execute
            
        Returns:
            The observation from executing the action
        """
        # Parse the action
        if action.startswith("Action:"):
            action = action[len("Action:"):].strip()
            
        if action.startswith("Final Answer:"):
            return "Task completed. Final answer provided."
            
        for tool in self.tools:
            if action.startswith(tool["name"]):
                # Extract arguments
                args_str = action[len(tool["name"]):].strip()
                try:
                    # Call the tool function
                    result = tool["func"](args_str)
                    return str(result)
                except Exception as e:
                    return f"Error executing action: {str(e)}"
                
        return "Unknown action. Please use one of the available tools."
    
    def run(self, task: str, max_iterations: int = 10) -> Dict[str, Any]:
        """
        Run the REACT reasoning process for the given task.
        
        Args:
            task: The task to solve
            max_iterations: Maximum number of reasoning iterations
            
        Returns:
            The final result including the reasoning process
        """
        prompt = self.create_prompt()
        
        for i in range(max_iterations):
            # Prepare the input
            input_dict = {
                "task": task,
                "tools": self.format_tools(),
                "history": self.format_history()
            }
            
            # Get the next thought and action
            chain = prompt | self.llm | StrOutputParser()
            output = chain.invoke(input_dict)
            
            # Parse the output
            parsed = self.parse_output(output)
            thought = parsed["thought"]
            action = parsed["action"]
            
            # Record the thought and action
            self.thought_history.append(thought)
            self.action_history.append(action)
            
            # Check if we're done
            if action.startswith("Final Answer:"):
                final_answer = action[len("Final Answer:"):].strip()
                return {
                    "status": "completed",
                    "answer": final_answer,
                    "thought_history": self.thought_history,
                    "action_history": self.action_history,
                    "observation_history": self.observation_history
                }
            
            # Execute the action
            observation = self.execute_action(action)
            self.observation_history.append(observation)
            
        # If we reach the maximum number of iterations
        return {
            "status": "max_iterations_reached",
            "thought_history": self.thought_history,
            "action_history": self.action_history,
            "observation_history": self.observation_history
        }