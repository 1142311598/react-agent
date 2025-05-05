#!/usr/bin/env python3
"""
Script to start a new research project from the command line.
"""
import sys
from src.agents.orchestrator_agent import OrchestratorAgent
from src.config import OPENAI_API_KEY, TAVILY_API_KEY

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: ./start_research.py 'Your research topic'")
        sys.exit(1)
    
    # Get the research topic from command line arguments
    topic = " ".join(sys.argv[1:])
    
    print(f"Starting research on topic: {topic}")
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent(
        api_key=OPENAI_API_KEY,
        tavily_api_key=TAVILY_API_KEY
    )
    
    # Start the research project
    result = orchestrator.start_research_project(topic)
    print(result)

if __name__ == "__main__":
    main()