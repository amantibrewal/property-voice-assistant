#!/usr/bin/env python
"""
Startup script for Ivy Homes Voice Agent
"""
import sys
from pathlib import Path

# Add the src directory to the path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run the agent
from ivy_homes_agent.agent import entrypoint
from livekit.agents import WorkerOptions, cli

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
