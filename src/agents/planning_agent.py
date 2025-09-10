import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ResearchTask:
    id: str
    description: str
    status: str = "pending"  # pending/in_progress/completed/failed
    result: str = ""
    required_tools: List[str] = None

class PlanningAgent:
    """Agent responsible for creating and adjusting research plans."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.plan_dir = "plans"
        os.makedirs(self.plan_dir, exist_ok=True)

    async def create_plan(self, topic: str) -> str:
        """Create a detailed research plan"""
        prompt = f"""Create a research plan for: {topic}
        Output JSON format:
        {{
            "topic": "research topic",
            "subtopics": [
                {{
                    "name": "subtopic name",
                    "tasks": [
                        {{
                            "id": "task-1",
                            "description": "task description",
                            "tools": ["tool1"],
                            "status": "pending"
                        }}
                    ]
                }}
            ],
            "status": "planned",
            "created_at": "timestamp"
        }}"""
        
        try:
            # Simulate LLM call
            await asyncio.sleep(1)
            plan_data = {
                "topic": topic,
                "subtopics": [{
                    "name": f"{topic} Overview",
                    "tasks": [{
                        "id": "task-1",
                        "description": f"Research {topic} basics",
                        "tools": ["tavily"],
                        "status": "pending"
                    }]
                }],
                "status": "planned",
                "created_at": datetime.now().isoformat()
            }
            
            # Save plan
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_path = os.path.join(self.plan_dir, f"plan_{timestamp}.json")
            
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(plan_data, f, indent=2)
                
            return f"Plan saved to {plan_path}"
            
        except Exception as e:
            return f"Plan creation failed: {str(e)}"

    async def adjust_plan(self, plan_path: str, task_results: Dict[str, Dict]) -> str:
        """Adjust plan based on task execution results"""
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
                
            # Update task statuses
            for subtopic in plan_data["subtopics"]:
                for task in subtopic["tasks"]:
                    if task["id"] in task_results:
                        result = task_results[task["id"]]
                        task["status"] = "completed" if result["success"] else "failed"
                        task["result"] = result["output"]
            
            # Update overall plan status
            all_tasks = [t for s in plan_data["subtopics"] for t in s["tasks"]]
            if all(t["status"] == "completed" for t in all_tasks):
                plan_data["status"] = "completed"
            else:
                plan_data["status"] = "in_progress"
                
            # Save updated plan
            with open(plan_path, "w", encoding="utf-8") as f:
                json.dump(plan_data, f, indent=2)
                
            return f"Plan updated at {plan_path}"
            
        except Exception as e:
            return f"Plan adjustment failed: {str(e)}"