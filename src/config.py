"""
Configuration settings for the multi-agent system.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration
class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo-0125")
        self.research_model = os.getenv("RESEARCH_MODEL", "gpt-3.5-turbo-0125")
        self.planning_model = os.getenv("PLANNING_MODEL", "gpt-3.5-turbo-0125")
        self.execution_model = os.getenv("EXECUTION_MODEL", "gpt-3.5-turbo-0125")

    def get_client(self):
        from openai import OpenAI
        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

llm_config = LLMConfig()

# API Keys
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# File paths
PLANS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plans")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")

# Ensure directories exist
os.makedirs(PLANS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)