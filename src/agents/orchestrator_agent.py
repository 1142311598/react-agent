"""
Orchestrator agent responsible for coordinating the multi-agent system.
"""
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.research_agent import ResearchAgent
from src.agents.report_agent import ReportAgent
from src.utils.file_utils import save_plan, load_plan, list_plans, list_reports

class OrchestratorAgent(BaseAgent):
    """
    Agent responsible for coordinating the multi-agent system.
    """
    
    def __init__(
        self,
        model_name: str = os.getenv("DEFAULT_MODEL", "deepseek-v3-250324"),
        api_key: Optional[str] = None,
        tavily_api_key: Optional[str] = None
    ):
        """
        Initialize the orchestrator agent.
        
        Args:
            model_name: The name of the LLM model to use
            api_key: Optional OpenAI API key
            tavily_api_key: Optional Tavily API key
        """
        super().__init__(
            name="OrchestratorAgent",
            description="Coordinates the multi-agent system",
            model_name=model_name,
            api_key=api_key
        )
        
        # Initialize the specialized agents
        self.planning_agent = PlanningAgent(model_name=model_name, api_key=api_key)
        self.research_agent = ResearchAgent(model_name=model_name, api_key=api_key, tavily_api_key=tavily_api_key)
        self.report_agent = ReportAgent(model_name=model_name, api_key=api_key)
        
        # Add orchestration-specific tools
        self.add_tool(
            name="start_research_project",
            description="Start a new research project on a given topic",
            func=self.start_research_project
        )
        
        self.add_tool(
            name="execute_research_plan",
            description="Execute a research plan",
            func=self.execute_research_plan
        )
        
        self.add_tool(
            name="update_research_progress",
            description="Update the progress of a research project",
            func=self.update_research_progress
        )
        
        self.add_tool(
            name="list_active_projects",
            description="List all active research projects",
            func=self.list_active_projects
        )
    
    async def start_research_project(self, topic: str) -> str:
        """
        Start a new research project on a given topic.
        
        Args:
            topic: The research topic
            
        Returns:
            A confirmation message with the plan file path
        """
        # Create a research plan
        try:
            print(f"[DEBUG] Starting research project on topic: {topic}")
            result = await self.planning_agent.create_plan(topic)
            print(f"[DEBUG] Planning agent returned: {result[:200]}...")  # Log first 200 chars
            
            # Extract the plan name from the result
            plan_name = None
            if "saved to" in result:
                plan_path = result.split("saved to ")[-1].strip()
                plan_name = os.path.basename(plan_path)
                
                # Update the plan status
                try:
                    plan_data = load_plan(plan_name)
                    plan_data["status"] = "in_progress"
                    plan_data["current_step"] = "research"
                    save_plan(plan_data, plan_name)
                except Exception as e:
                    print(f"[WARNING] Failed to update plan status: {str(e)}")
                
                return f"Research project started on topic: {topic}\nPlan saved to: {plan_path}"
            return f"Research project started but no plan saved: {result}"
            
        except Exception as e:
            print(f"[ERROR] Failed to start research project: {str(e)}")
            return f"Research failed: {str(e)}"
    
    def execute_research_plan(self, plan_name: str) -> str:
        """
        Execute a research plan.
        
        Args:
            plan_name: The name of the plan file
            
        Returns:
            A summary of the execution results
        """
        try:
            # Load the research plan
            plan_data = load_plan(plan_name)
            
            # Check if the plan is already completed
            if plan_data.get("status") == "completed":
                return f"Research plan '{plan_name}' is already completed."
            
            # Update the plan status
            plan_data["status"] = "in_progress"
            plan_data["current_step"] = "research"
            save_plan(plan_data, plan_name)
            
            # Execute each subtopic research task
            research_findings = []
            
            for subtopic_idx, subtopic in enumerate(plan_data["subtopics"]):
                subtopic_name = subtopic["name"]
                
                # Research each task in the subtopic
                for task_idx, task in enumerate(subtopic["tasks"]):
                    if task["status"] == "completed":
                        continue
                    
                    task_description = task["description"]
                    
                    # Update task status to in_progress
                    plan_data["subtopics"][subtopic_idx]["tasks"][task_idx]["status"] = "in_progress"
                    save_plan(plan_data, plan_name)
                    
                    # Perform the research
                    research_query = f"{plan_data['topic']}: {subtopic_name} - {task_description}"
                    research_result = self.research_agent.deep_research(research_query)
                    
                    # Store the findings
                    research_findings.append({
                        "subtopic": subtopic_name,
                        "task": task_description,
                        "findings": research_result
                    })
                    
                    # Update task status to completed
                    plan_data["subtopics"][subtopic_idx]["tasks"][task_idx]["status"] = "completed"
                    plan_data["subtopics"][subtopic_idx]["tasks"][task_idx]["completed_at"] = datetime.now().isoformat()
                    save_plan(plan_data, plan_name)
            
            # Generate the report
            report_input = json.dumps({
                "plan_name": plan_name,
                "research_findings": research_findings
            })
            
            report_result = self.report_agent.generate_report(report_input)
            
            # Update the plan status
            plan_data["status"] = "completed"
            plan_data["current_step"] = "completed"
            plan_data["progress"] = 100
            plan_data["completed_at"] = datetime.now().isoformat()
            save_plan(plan_data, plan_name)
            
            return f"Research plan execution completed.\n{report_result}"
            
        except FileNotFoundError:
            return f"Error: Plan '{plan_name}' not found"
        except Exception as e:
            return f"Error executing research plan: {str(e)}"
    
    def update_research_progress(self, progress_data: str) -> str:
        """
        Update the progress of a research project.
        
        Args:
            progress_data: JSON string containing plan_name and progress updates
            
        Returns:
            A confirmation message
        """
        try:
            # Parse the progress data
            data = json.loads(progress_data)
            plan_name = data.get("plan_name")
            
            if not plan_name:
                return "Error: No plan name provided"
            
            # Load the research plan
            try:
                plan_data = load_plan(plan_name)
            except FileNotFoundError:
                return f"Error: Plan '{plan_name}' not found"
            
            # Update the task statuses
            if "task_updates" in data:
                for task_update in data["task_updates"]:
                    subtopic_idx = task_update.get("subtopic_idx")
                    task_idx = task_update.get("task_idx")
                    
                    if subtopic_idx is not None and task_idx is not None:
                        if 0 <= subtopic_idx < len(plan_data["subtopics"]) and \
                           0 <= task_idx < len(plan_data["subtopics"][subtopic_idx]["tasks"]):
                            # Update the task status
                            for key, value in task_update.items():
                                if key not in ["subtopic_idx", "task_idx"]:
                                    plan_data["subtopics"][subtopic_idx]["tasks"][task_idx][key] = value
            
            # Calculate overall progress
            total_tasks = 0
            completed_tasks = 0
            
            for subtopic in plan_data["subtopics"]:
                for task in subtopic["tasks"]:
                    total_tasks += 1
                    if task["status"] == "completed":
                        completed_tasks += 1
            
            progress_percentage = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            plan_data["progress"] = progress_percentage
            
            # Update the current step if provided
            if "current_step" in data:
                plan_data["current_step"] = data["current_step"]
            
            # Update the status if provided
            if "status" in data:
                plan_data["status"] = data["status"]
            
            # Save the updated plan
            save_plan(plan_data, plan_name)
            
            return f"Research progress updated. Current progress: {progress_percentage}%"
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON in progress_data"
    
    def list_active_projects(self, _: str = "") -> str:
        """
        List all active research projects.
        
        Args:
            _: Ignored parameter to match the tool function signature
            
        Returns:
            A list of active research projects
        """
        # Get all plan files
        plan_files = list_plans()
        
        if not plan_files:
            return "No research projects found."
        
        # Load each plan and check its status
        active_projects = []
        
        for plan_file in plan_files:
            try:
                plan_data = load_plan(plan_file)
                
                # Add to active projects if not completed
                if plan_data.get("status") != "completed":
                    active_projects.append({
                        "plan_name": plan_file,
                        "topic": plan_data.get("topic", "Unknown"),
                        "status": plan_data.get("status", "Unknown"),
                        "progress": plan_data.get("progress", 0),
                        "current_step": plan_data.get("current_step", "Unknown")
                    })
            except:
                # Skip plans that can't be loaded
                continue
        
        if not active_projects:
            return "No active research projects found."
        
        # Format the result
        result = "Active Research Projects:\n\n"
        
        for project in active_projects:
            result += f"Plan: {project['plan_name']}\n"
            result += f"Topic: {project['topic']}\n"
            result += f"Status: {project['status']}\n"
            result += f"Progress: {project['progress']}%\n"
            result += f"Current Step: {project['current_step']}\n\n"
        
        return result