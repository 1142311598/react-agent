"""
Utility functions for file operations.
"""
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

def save_plan(plan_data: Dict[str, Any], plan_name: Optional[str] = None) -> str:
    """
    Save a plan to the plans directory.
    
    Args:
        plan_data: The plan data to save
        plan_name: Optional name for the plan file
        
    Returns:
        The path to the saved plan file
    """
    from src.config import PLANS_DIR
    
    if plan_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_name = f"plan_{timestamp}.json"
    
    plan_path = os.path.join(PLANS_DIR, plan_name)
    
    with open(plan_path, 'w') as f:
        json.dump(plan_data, f, indent=2)
    
    return plan_path

def load_plan(plan_name: str) -> Dict[str, Any]:
    """
    Load a plan from the plans directory.
    
    Args:
        plan_name: The name of the plan file
        
    Returns:
        The plan data
    """
    from src.config import PLANS_DIR
    
    plan_path = os.path.join(PLANS_DIR, plan_name)
    
    with open(plan_path, 'r') as f:
        plan_data = json.load(f)
    
    return plan_data

def save_report(report_content: str, report_name: Optional[str] = None) -> str:
    """
    Save a report to the reports directory.
    
    Args:
        report_content: The content of the report
        report_name: Optional name for the report file
        
    Returns:
        The path to the saved report file
    """
    from src.config import REPORTS_DIR
    
    if report_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"report_{timestamp}.md"
    
    report_path = os.path.join(REPORTS_DIR, report_name)
    
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    return report_path

def list_plans() -> List[str]:
    """
    List all plans in the plans directory.
    
    Returns:
        A list of plan file names
    """
    from src.config import PLANS_DIR
    
    return [f for f in os.listdir(PLANS_DIR) if f.endswith('.json')]

def list_reports() -> List[str]:
    """
    List all reports in the reports directory.
    
    Returns:
        A list of report file names
    """
    from src.config import REPORTS_DIR
    
    return [f for f in os.listdir(REPORTS_DIR) if f.endswith('.md')]