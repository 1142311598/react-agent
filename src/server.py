"""
Server script to run the FastAPI application with static file serving.
"""
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.api import app as api_app

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mount the static files
api_app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

# Add templates
templates = Jinja2Templates(directory=os.path.join(current_dir, "static"))

@api_app.get("/", tags=["UI"])
async def root(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

def run_server(host="0.0.0.0", port=58011):
    """Run the server."""
    uvicorn.run("src.server:api_app", host=host, port=port, reload=True)

if __name__ == "__main__":
    run_server()