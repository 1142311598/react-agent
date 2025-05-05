# Multi-Agent Deep Research System

A multi-agent system based on LLM with REACT reasoning architecture for deep research. This system uses multiple specialized agents to perform comprehensive research on any topic, generate detailed reports, and adapt its research plan based on findings.

## Features

- **Task Decomposition**: Breaks down complex research topics into manageable subtasks
- **Adaptive Planning**: Adjusts research plans based on findings and progress
- **Internet Search**: Uses Tavily API to search for relevant information
- **Comprehensive Reports**: Generates well-structured research reports
- **Web Interface**: User-friendly interface to manage research projects

## Architecture

The system consists of the following components:

1. **Orchestrator Agent**: Coordinates the overall research process
2. **Planning Agent**: Creates and updates research plans
3. **Research Agent**: Gathers information from the internet
4. **Report Agent**: Generates comprehensive research reports
5. **REACT Framework**: Provides reasoning and acting capabilities to agents

## Getting Started

### Prerequisites

- Python 3.8+
- OpenAI API key
- Tavily API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/react-agent.git
   cd react-agent
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export TAVILY_API_KEY=your_tavily_api_key
   ```

### Running the System

#### Command Line Interface

```
# Start a new research project
python -m src.main start "Your research topic"

# Execute a research plan
python -m src.main execute plan_20250505_123456.json

# List active research projects
python -m src.main list

# List generated reports
python -m src.main list-reports

# Show plan details
python -m src.main show plan_20250505_123456.json
```

#### Web Interface

```
# Start the web server
python -m src.server
```

Then open your browser and navigate to http://localhost:58011

## Project Structure

```
react-agent/
├── plans/                  # Research plans storage
├── reports/                # Generated reports storage
├── src/
│   ├── agents/             # Specialized agents
│   │   ├── base_agent.py   # Base agent class
│   │   ├── orchestrator_agent.py
│   │   ├── planning_agent.py
│   │   ├── research_agent.py
│   │   └── report_agent.py
│   ├── utils/              # Utility functions
│   │   ├── file_utils.py   # File operations
│   │   ├── react_utils.py  # REACT framework
│   │   └── search_utils.py # Search operations
│   ├── static/             # Web interface files
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── api.py              # FastAPI endpoints
│   ├── config.py           # Configuration settings
│   ├── main.py             # CLI entry point
│   └── server.py           # Web server
└── requirements.txt        # Dependencies
```

## How It Works

1. **Task Decomposition**: When a research topic is submitted, the Planning Agent breaks it down into subtopics and specific tasks.

2. **Execution**: The Orchestrator Agent coordinates the execution of tasks, using the Research Agent to gather information from the internet.

3. **Adaptation**: As tasks are completed, the system updates the research plan based on findings and progress.

4. **Report Generation**: Once all tasks are completed, the Report Agent generates a comprehensive research report.

## License

This project is licensed under the MIT License - see the LICENSE file for details.