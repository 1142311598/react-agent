"""
Main entry point for the multi-agent deep research system.
"""
import os
import argparse
import json
from typing import Dict, Any, Optional

from src.config import OPENAI_API_KEY, TAVILY_API_KEY
from src.agents.orchestrator_agent import OrchestratorAgent
from src.utils.file_utils import list_plans, list_reports, load_plan

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Multi-agent deep research system")
    
    # Main command
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Start a new research project
    start_parser = subparsers.add_parser("start", help="Start a new research project")
    start_parser.add_argument("topic", help="Research topic")
    
    # Execute a research plan
    execute_parser = subparsers.add_parser("execute", help="Execute a research plan")
    execute_parser.add_argument("plan", help="Name of the plan file")
    
    # List active projects
    subparsers.add_parser("list", help="List active research projects")
    
    # List reports
    subparsers.add_parser("list-reports", help="List generated reports")
    
    # Update research progress
    update_parser = subparsers.add_parser("update", help="Update research progress")
    update_parser.add_argument("plan", help="Name of the plan file")
    update_parser.add_argument("--task", type=int, nargs=2, help="Task to update (subtopic_idx task_idx)")
    update_parser.add_argument("--status", choices=["pending", "in_progress", "completed"], help="New task status")
    
    # Show plan details
    show_parser = subparsers.add_parser("show", help="Show plan details")
    show_parser.add_argument("plan", help="Name of the plan file")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent(
        api_key=OPENAI_API_KEY,
        tavily_api_key=TAVILY_API_KEY
    )
    
    if args.command == "start":
        # Start a new research project
        result = orchestrator.start_research_project(args.topic)
        print(result)
    
    elif args.command == "execute":
        # Execute a research plan
        result = orchestrator.execute_research_plan(args.plan)
        print(result)
    
    elif args.command == "list":
        # List active research projects
        result = orchestrator.list_active_projects()
        print(result)
    
    elif args.command == "list-reports":
        # List generated reports
        from src.utils.file_utils import list_reports
        reports = list_reports()
        
        if not reports:
            print("No reports found.")
        else:
            print("Generated Reports:")
            for report in reports:
                print(f"- {report}")
    
    elif args.command == "update":
        # Update research progress
        if args.task and args.status:
            # Update a specific task
            subtopic_idx, task_idx = args.task
            
            progress_data = {
                "plan_name": args.plan,
                "task_updates": [
                    {
                        "subtopic_idx": subtopic_idx,
                        "task_idx": task_idx,
                        "status": args.status
                    }
                ]
            }
            
            result = orchestrator.update_research_progress(json.dumps(progress_data))
            print(result)
        else:
            print("Error: Both --task and --status are required for update command.")
    
    elif args.command == "show":
        # Show plan details
        try:
            plan_data = load_plan(args.plan)
            print(json.dumps(plan_data, indent=2))
        except FileNotFoundError:
            print(f"Error: Plan '{args.plan}' not found")
    
    else:
        print("Error: No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main()