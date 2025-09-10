#!/usr/bin/env python3
"""
Script to list all reports.
"""
import os

def list_reports():
    """List all reports in the reports directory."""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print("Reports directory not found.")
        return
    
    reports = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
    
    if not reports:
        print("No reports found.")
    else:
        print("Generated Reports:")
        for report in reports:
            print(f"- {report}")

if __name__ == "__main__":
    list_reports()
