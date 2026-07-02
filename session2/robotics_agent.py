"""
Robotics Agent - An AI agent that designs robotics platforms.
==============================================================

This agent connects to the Robotics MCP Server, discovers available tools,
and uses the university's local LLM service to reason about which tools to
call in order to design a robotics platform for a given task.

This is the key file for Session 2 - it demonstrates:
  1. Connecting to an MCP server as a client
  2. Discovering tools dynamically at runtime
  3. Converting MCP tool schemas to simple dicts for the local LLM
  4. The full agent loop: LLM reasons -> calls tools -> reads results -> repeats

Usage:
    python robotics_agent.py
"""

import asyncio
import json
import os

import llm_client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ---------------------------------------------------------------------------
# System prompt - tells the LLM what role it plays and how to behave
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Robotics Platform Designer. Your job is to design
custom robotics platforms for specific tasks.

You have access to tools that let you search a database of robotics components,
sensors, and actuators. Use these tools to find suitable parts, then synthesise
a complete platform recommendation.

Your final recommendation should include:
1. Robot type and form factor
2. Required components (with justification)
3. Sensor suite
4. Actuators and end-effectors
5. Key capabilities
6. Safety considerations

Always search the database before making recommendations. Use multiple tool calls
if needed to gather comprehensive information."""


# ---------------------------------------------------------------------------
# Tool format conversion
# ---------------------------------------------------------------------------

def mcp_tools_to_dicts(mcp_tools) -> list[dict]:
    """Convert MCP tool definitions to simple dicts for the local LLM.

    The MCP SDK gives us tool objects with .name, .description, and .inputSchema.
    We convert these to plain dicts that llm_client can inject into the prompt.
    """
    tool_dicts = []
    for tool in mcp_tools:
        tool_dicts.append({
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema if tool.inputSchema else {
                "type": "object",
                "properties": {},
            },
        })
    return tool_dicts


# ---------------------------------------------------------------------------
# The main agent loop
# ---------------------------------------------------------------------------

async def run_agent(task: str):
    """Run the robotics agent for a given task.

    This function:
    1. Starts the MCP server as a subprocess
    2. Connects to it and discovers available tools
    3. Runs the agent loop: LLM decides what to do, we execute tool calls,
       feed results back, and repeat until the LLM gives a final answer
    """

    # Check LLM service health first
    health = llm_client.check_health()
    if not health.get("model_loaded", False):
        print(f"WARNING: LLM service health check: {health}")
        print("The agent will attempt to continue, but generation may fail.\n")

    # Configure how to launch the MCP server
    # StdioServerParameters tells the client to start the server as a
    # subprocess and communicate over stdin/stdout
    server_params = StdioServerParameters(
        command="python",
        args=["robotics_mcp_server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    # Connect to the MCP server
    # stdio_client spawns the server process and gives us read/write streams
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP session (handshake with the server)
            await session.initialize()

            # Step 1: Discover available tools from the server
            tools_result = await session.list_tools()
            tools = mcp_tools_to_dicts(tools_result.tools)

            print("\nConnected to MCP server. Available tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Step 2: Set up the conversation with the LLM
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Design a robotics platform for the following task: {task}"
                    ),
                },
            ]

            print(f"\nTask: {task}")
            print("\nAgent is thinking...\n")

            # Step 3: Agent loop
            # The LLM will keep calling tools until it has enough info
            # to give a final answer (a response without tool_calls)
            max_iterations = 10
            for i in range(max_iterations):

                # Ask the LLM what to do next
                response = llm_client.chat(messages, tools=tools)

                # Add the assistant's raw response to the conversation
                messages.append({
                    "role": "assistant",
                    "content": response["raw"],
                })

                # If the LLM didn't request any tool calls, it's giving
                # its final answer - we're done!
                if not response["tool_calls"]:
                    print("=" * 60)
                    print("ROBOTICS PLATFORM RECOMMENDATION")
                    print("=" * 60)
                    print(response["content"])
                    return response["content"]

                # The LLM wants to call one or more tools
                # Process each tool call
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["arguments"]

                    print(f"  Calling tool: {tool_name}({tool_args})")

                    # Execute the tool via MCP
                    result = await session.call_tool(tool_name, tool_args)

                    # Extract the text result
                    tool_result_text = (
                        result.content[0].text if result.content else "No results"
                    )

                    # Add the tool result to the conversation so the LLM
                    # can see what the tool returned
                    messages.append({
                        "role": "tool",
                        "name": tool_name,
                        "content": tool_result_text,
                    })

            print("Max iterations reached.")
            last = messages[-1]
            if last.get("role") == "assistant":
                return last.get("content", "Agent could not complete the task.")
            return "Agent could not complete the task."


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    task = input("Enter a robotics task (or press Enter for default): ").strip()
    if not task:
        task = "Build a platform for autonomous object sorting on a conveyor belt"

    result = asyncio.run(run_agent(task))
