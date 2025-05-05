#!/usr/bin/env python3
"""
Script to execute a research plan from the command line.
"""
import sys
from src.agents.orchestrator_agent import OrchestratorAgent
from src.config import OPENAI_API_KEY, TAVILY_API_KEY

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: ./execute_plan.py plan_name.json")
        sys.exit(1)
    
    # Get the plan name from command line arguments
    plan_name = sys.argv[1]
    
    print(f"Executing research plan: {plan_name}")
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent(
        api_key=OPENAI_API_KEY,
        tavily_api_key=TAVILY_API_KEY
    )
    
    # Execute the research plan
    result = orchestrator.execute_research_plan(plan_name)
    print(result)

if __name__ == "__main__":
    main()