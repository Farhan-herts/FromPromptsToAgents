"""
Step 3: Run the Robotics Agent
=================================
This is the full agent — it connects the LLM to the MCP tools.
The LLM decides which tools to call and designs a robot.

    python steps/step3_run_agent.py

Try different tasks:
  - "Build a robot for sorting fruit on a conveyor belt"
  - "Design a warehouse delivery robot"
  - "Create a search and rescue robot"
"""
import asyncio
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from robotics_agent import run_agent

task = input("Enter a robotics task (or press Enter for default): ").strip()
if not task:
    task = "Build a robot for sorting objects on a conveyor belt"

print(f"\nTask: {task}")
print("The agent will now call tools and design a robot...\n")

asyncio.run(run_agent(task))
