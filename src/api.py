"""
FastAPI server for the multi-agent deep research system.
"""
import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.config import llm_config, TAVILY_API_KEY, PLANS_DIR, REPORTS_DIR
from src.agents.orchestrator_agent import OrchestratorAgent
from src.utils.file_utils import list_plans, list_reports, load_plan, save_plan

# Initialize the FastAPI app
app = FastAPI(
    title="Deep Research Multi-Agent System",
    description="API for multi-agent deep research system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator agent
orchestrator = OrchestratorAgent(
    api_key=llm_config.api_key,
    tavily_api_key=TAVILY_API_KEY
)

# Define request and response models
class ResearchRequest(BaseModel):
    topic: str

class PlanRequest(BaseModel):
    plan_name: str

class TaskUpdateRequest(BaseModel):
    plan_name: str
    subtopic_idx: int
    task_idx: int
    status: str

class ResearchResponse(BaseModel):
    message: str
    plan_name: Optional[str] = None

class PlanListResponse(BaseModel):
    plans: List[Dict[str, Any]]

class ReportListResponse(BaseModel):
    reports: List[str]

# Background task for executing research plans
def execute_research_plan_task(plan_name: str):
    """
    Execute a research plan in the background.
    
    Args:
        plan_name: The name of the plan file
    """
    orchestrator.execute_research_plan(plan_name)

# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Deep Research Multi-Agent System API"}

@app.post("/research/start", response_model=ResearchResponse)
async def start_research(request: ResearchRequest):
    """
    Start a new research project.
    
    Args:
        request: The research request containing the topic
        
    Returns:
        A response with a message and the plan name
    """
    try:
        # Run with timeout
        result = await asyncio.wait_for(
            orchestrator.start_research_project(request.topic),
            timeout=30.0
        )
        
        # Extract the plan name from the result
        plan_name = None
        if "Plan saved to" in result:
            plan_path = result.split("Plan saved to: ")[-1].split("\n")[0]
            plan_name = os.path.basename(plan_path)
        
        return ResearchResponse(message=result, plan_name=plan_name)
        
    except asyncio.TimeoutError:
        return ResearchResponse(message="Research request timed out after 30 seconds")
    except Exception as e:
        return ResearchResponse(message=f"Research failed: {str(e)}")

@app.post("/research/execute", response_model=ResearchResponse)
async def execute_research(request: PlanRequest, background_tasks: BackgroundTasks):
    """
    Execute a research plan.
    
    Args:
        request: The plan request containing the plan name
        background_tasks: FastAPI background tasks
        
    Returns:
        A response with a message
    """
    # Check if the plan exists
    try:
        load_plan(request.plan_name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Plan '{request.plan_name}' not found")
    
    # Execute the plan in the background
    background_tasks.add_task(execute_research_plan_task, request.plan_name)
    
    return ResearchResponse(
        message=f"Research plan execution started in the background. Check the plan status for updates.",
        plan_name=request.plan_name
    )

@app.get("/plans", response_model=PlanListResponse)
async def list_research_plans():
    """
    List all research plans.
    
    Returns:
        A response with a list of plans
    """
    plan_files = list_plans()
    plans = []
    
    for plan_file in plan_files:
        try:
            plan_data = load_plan(plan_file)
            plans.append({
                "plan_name": plan_file,
                "topic": plan_data.get("topic", "Unknown"),
                "status": plan_data.get("status", "Unknown"),
                "progress": plan_data.get("progress", 0),
                "current_step": plan_data.get("current_step", "Unknown"),
                "created_at": plan_data.get("created_at", "Unknown")
            })
        except:
            # Skip plans that can't be loaded
            continue
    
    return PlanListResponse(plans=plans)

@app.get("/plans/{plan_name}")
async def get_plan(plan_name: str):
    """
    Get a specific research plan.
    
    Args:
        plan_name: The name of the plan file
        
    Returns:
        The plan data
    """
    try:
        plan_data = load_plan(plan_name)
        return plan_data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_name}' not found")

@app.post("/plans/{plan_name}/update_task", response_model=ResearchResponse)
async def update_task(plan_name: str, request: TaskUpdateRequest):
    """
    Update a task in a research plan.
    
    Args:
        plan_name: The name of the plan file
        request: The task update request
        
    Returns:
        A response with a message
    """
    progress_data = {
        "plan_name": plan_name,
        "task_updates": [
            {
                "subtopic_idx": request.subtopic_idx,
                "task_idx": request.task_idx,
                "status": request.status
            }
        ]
    }
    
    result = orchestrator.update_research_progress(json.dumps(progress_data))
    
    return ResearchResponse(message=result, plan_name=plan_name)

@app.get("/reports", response_model=ReportListResponse)
async def list_research_reports():
    """
    List all research reports.
    
    Returns:
        A response with a list of reports
    """
    reports = list_reports()
    return ReportListResponse(reports=reports)

@app.get("/reports/{report_name}")
async def get_report(report_name: str):
    """
    Get a specific research report.
    
    Args:
        report_name: The name of the report file
        
    Returns:
        The report content as a file
    """
    report_path = os.path.join(REPORTS_DIR, report_name)
    
    if not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail=f"Report '{report_name}' not found")
    
    return FileResponse(report_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api:app", host="0.0.0.0", port=58011, reload=True)