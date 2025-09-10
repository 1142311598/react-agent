"""
Report agent responsible for generating comprehensive research reports.
"""
import os
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.utils.file_utils import save_report, load_plan

class ReportAgent(BaseAgent):
    """
    Agent responsible for generating comprehensive research reports.
    """
    
    def __init__(
        self,
        model_name: str = os.getenv("DEFAULT_MODEL", "deepseek-v3-250324"),
        api_key: Optional[str] = None
    ):
        """
        Initialize the report agent.
        
        Args:
            model_name: The name of the LLM model to use
            api_key: Optional OpenAI API key
        """
        super().__init__(
            name="ReportAgent",
            description="Generates comprehensive research reports",
            model_name=model_name,
            api_key=api_key
        )
        
        self.report_dir = "reports"
        os.makedirs(self.report_dir, exist_ok=True)
        
        # Add report-specific tools
        self.add_tool(
            name="generate_report",
            description="Generate a comprehensive report based on research findings",
            func=self.generate_report
        )
        
        self.add_tool(
            name="generate_executive_summary",
            description="Generate an executive summary of a research report",
            func=self.generate_executive_summary
        )
        
        self.add_tool(
            name="generate_section",
            description="Generate a specific section of a research report",
            func=self.generate_section
        )
    
    def generate_report(self, input_data: str) -> str:
        """
        Generate a comprehensive report based on research findings.
        
        Args:
            input_data: JSON string containing plan_name and research_findings
            
        Returns:
            A confirmation message with the report file path
        """
        try:
            # Parse the input data
            data = json.loads(input_data)
            plan_name = data.get("plan_name")
            research_findings = data.get("research_findings", [])
            
            if not plan_name:
                return "Error: No plan name provided"
            
            # Initialize plan_data
            plan_data = json.loads(input_data).get('plan_data', None)
            
            # Load plan if not provided
            if not plan_data:
                try:
                    plan_data = load_plan(plan_name)
                except FileNotFoundError:
                    return f"Error: Plan '{plan_name}' not found"
            
            # Prepare structured report input
            report_data = {
                "topic": plan_data.get("topic", "Unknown Topic"),
                "subtopics": [
                    {
                        "name": f["subtopic"],
                        "summary": f["findings"]["summary"],
                        "sources": f["findings"].get("sources", [])
                    }
                    for f in research_findings
                ]
            }

            report_prompt = f"""
Generate a professional research report with the following structure:

# {report_data['topic']} Research Report
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
Summarize key findings from all subtopics.

## Detailed Findings
{'\n'.join(
    f'### {st["name"]}\n{st["summary"]}\nSources: {len(st["sources"])}'
    for st in report_data['subtopics']
)}

## Conclusions and Recommendations
Provide overall conclusions and actionable recommendations.
"""
            
            # Debug: Print prompt before generation
            print(f"\n=== Report Prompt ===\n{report_prompt}\n=== End Prompt ===")

            # Bypass LLM for testing
            report_content = f"""# {report_data['topic']} Research Report
**Date**: {datetime.now().strftime('%Y-%m-%d')}

## Executive Summary
This is a mock report generated for testing purposes.

## Detailed Findings
{"".join(
    f"### {st['name']}\n{st['summary']}\nSources: {len(st['sources'])}\n\n"
    for st in report_data['subtopics']
)}

## Conclusions
Mock conclusions for testing.
"""

            print(f"\n=== Generated Report ===\n{report_content}\n=== End Report ===")
            
            # Debug output
            print(f"Report content length: {len(report_content)} characters")
            print(f"Report content sample: {report_content[:200]}...")
            
            # Save the report
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                topic_slug = plan_data.get("topic", "research").lower().replace(" ", "_")[:30]
                report_name = f"{topic_slug}_report_{timestamp}.md"
                report_path = os.path.join(self.report_dir, report_name)
                
                with open(report_path, "w") as f:
                    f.write(report_content)
                
                print(f"Report successfully saved to {report_path}")
                return f"Research report generated and saved to {report_path}"
            except Exception as e:
                return f"Failed to save report: {str(e)}"
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON in input_data"
    
    def generate_executive_summary(self, report_content: str) -> str:
        """
        Generate an executive summary of a research report.
        
        Args:
            report_content: The content of the research report
            
        Returns:
            An executive summary
        """
        summary_prompt = f"""
You are a research report writer. Your task is to create an executive summary of the following research report:

{report_content[:10000]}  # Limit to first 10000 chars to avoid token limits

Create a concise executive summary (300-500 words) that:
1. States the purpose of the research
2. Summarizes the key findings
3. Highlights the main conclusions
4. Presents the most important recommendations

The executive summary should be self-contained and provide a complete overview of the report for busy executives.
"""
        
        executive_summary = self.simple_generate(summary_prompt)
        
        return executive_summary
    
    def generate_section(self, section_data: str) -> str:
        """
        Generate a specific section of a research report.
        
        Args:
            section_data: JSON string containing section_name, context, and findings
            
        Returns:
            The generated section content
        """
        try:
            # Parse the section data
            data = json.loads(section_data)
            section_name = data.get("section_name")
            context = data.get("context", "")
            findings = data.get("findings", [])
            
            if not section_name:
                return "Error: No section name provided"
            
            # Generate the section
            section_prompt = f"""
You are a research report writer. Your task is to create the "{section_name}" section of a research report based on the following context and findings:

CONTEXT:
{context}

FINDINGS:
{json.dumps(findings, indent=2)}

Create a well-written, professional section that:
1. Is appropriate for a section titled "{section_name}"
2. Incorporates the relevant findings
3. Maintains a logical flow
4. Uses appropriate headings and subheadings
5. Cites sources appropriately

Format the section in Markdown.
"""
            
            section_content = self.simple_generate(section_prompt)
            
            return section_content
            
        except json.JSONDecodeError:
            return "Error: Invalid JSON in section_data"