#!/usr/bin/env python3
"""
Script to list all plans.
"""
import os
import json

def list_plans():
    """List all plans in the plans directory."""
    plans_dir = "plans"
    if not os.path.exists(plans_dir):
        print("Plans directory not found.")
        return
    
    plans = [f for f in os.listdir(plans_dir) if f.endswith('.json')]
    
    if not plans:
        print("No plans found.")
    else:
        print("Research Plans:")
        for plan_name in plans:
            try:
                with open(os.path.join(plans_dir, plan_name), 'r') as f:
                    plan_data = json.load(f)
                
                topic = plan_data.get("topic", "Unknown")
                status = plan_data.get("status", "unknown")
                progress = plan_data.get("progress", 0)
                
                print(f"- {plan_name}")
                print(f"  Topic: {topic}")
                print(f"  Status: {status}")
                print(f"  Progress: {progress}%")
                print()
            except Exception as e:
                print(f"- {plan_name} (Error: {str(e)})")

if __name__ == "__main__":
    list_plans()
