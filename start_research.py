#!/usr/bin/env python3
"""
Script to start a new research project from the command line.
"""
import sys
import asyncio
from src.agents.orchestrator_agent import OrchestratorAgent
from src.config import llm_config, TAVILY_API_KEY

async def main_async():
    """Async main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ./start_research.py 'Your research topic'")
        sys.exit(1)
    
    # Get the research topic from command line arguments
    topic = " ".join(sys.argv[1:])
    
    print(f"Starting research on topic: {topic}")
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent(
        api_key=llm_config.api_key,
        tavily_api_key=TAVILY_API_KEY
    )
    
    # Start the research project
    result = await orchestrator.start_research_project(topic)
    print(result)

def main():
    """Main entry point."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
