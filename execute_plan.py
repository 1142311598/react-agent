#!/usr/bin/env python3
"""
Script to execute a research plan from the command line.
"""
import sys
import asyncio
from src.agents.orchestrator_agent import OrchestratorAgent
from src.config import llm_config, TAVILY_API_KEY

async def main_async():
    """Async main entry point."""
    if len(sys.argv) != 2:
        print("Usage: ./execute_plan.py plan_name.json")
        sys.exit(1)
    
    # Get the plan name from command line arguments
    plan_name = sys.argv[1]
    
    print(f"Executing research plan: {plan_name}")
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent(
        api_key=llm_config.api_key,
        tavily_api_key=TAVILY_API_KEY
    )
    
    # Execute the research plan
    result = await orchestrator.execute_research_plan(plan_name)
    print(result)

def main():
    """Main entry point."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
