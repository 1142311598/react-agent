#!/usr/bin/env python3
"""
Script to run the web server for the multi-agent deep research system.
"""
from src.server import run_server

if __name__ == "__main__":
    print("Starting Deep Research Multi-Agent System server...")
    print("Access the web interface at http://localhost:58011")
    run_server(host="0.0.0.0", port=58011)