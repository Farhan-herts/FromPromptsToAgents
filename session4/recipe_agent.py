"""
=============================================================================
  Session 4: Recipe Agent
  University of Hertfordshire AI Workshop
  Time: 14:30 - 16:00
=============================================================================

  This agent connects to the Recipe MCP Server, discovers its tools, and
  uses the local LLM service to provide comprehensive dish analysis.

  Architecture:
      User --> Recipe Agent --> Local LLM Service (Qwen2.5)
                            --> MCP Server --> Recipe Tools --> Dish Database

  The agent loop follows the same pattern as the Robotics Agent from
  Session 2:
    1. Connect to the MCP server via stdio
    2. Discover available tools and convert them to tool description format
    3. Send the user's request to the LLM along with the tool definitions
    4. If the LLM wants to call a tool, call it via MCP and feed the result back
    5. Repeat until the LLM produces a final text response
    6. Return the analysis

  Usage:
      python recipe_agent.py

  Or import the analyse_dish function for use in other scripts:
      from recipe_agent import analyse_dish
=============================================================================
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import llm_client

load_dotenv()

# ---------------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------------
# This prompt shapes the LLM's behaviour as a culinary analysis expert.
# It instructs the model to use ALL available tools for a thorough analysis.

SYSTEM_PROMPT = """You are a culinary analysis expert. Your job is to analyse dishes
in comprehensive detail, focusing on what would be needed if a robot were to prepare them.

You have access to tools for dish analysis, cooking technique breakdown, equipment specs,
and safety requirements. Use ALL relevant tools to build a complete picture.

Your analysis should cover:
1. Dish overview (cuisine, difficulty, time)
2. Ingredients list
3. Step-by-step preparation with techniques
4. Equipment needed with specifications
5. Safety considerations
6. A summary of the key physical tasks involved (chopping, stirring, pouring, etc.)
   with notes on precision and difficulty

Format your output clearly with headers and bullet points."""


# ---------------------------------------------------------------------------
# Helper: Call an MCP tool by name
# ---------------------------------------------------------------------------

async def call_mcp_tool(session: ClientSession, tool_name: str, arguments: dict) -> str:
    """
    Call a tool on the MCP server and return the result as a string.

    Parameters
    ----------
    session : ClientSession
        The active MCP client session.
    tool_name : str
        The name of the tool to call.
    arguments : dict
        The arguments to pass to the tool.

    Returns
    -------
    str
        The tool's response as a string.
    """
    result = await session.call_tool(tool_name, arguments)
    # MCP returns a list of content blocks; combine their text
    return "\n".join(block.text for block in result.content if hasattr(block, "text"))


# ---------------------------------------------------------------------------
# Agent Loop
# ---------------------------------------------------------------------------

async def run_agent_loop(
    session: ClientSession,
    tools: list,
    user_message: str,
    max_iterations: int = 15,
) -> str:
    """
    Run the agent loop: send messages to the LLM, handle tool calls,
    feed results back, and repeat until the LLM produces a final response.

    Parameters
    ----------
    session : ClientSession
        The active MCP client session (for calling tools).
    tools : list
        Tool definitions as dicts with name, description, parameters.
    user_message : str
        The user's request (e.g., "Analyse pasta carbonara").
    max_iterations : int
        Safety limit to prevent infinite loops.

    Returns
    -------
    str
        The LLM's final text response.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    for iteration in range(max_iterations):
        # --- Call the LLM via the local service ---
        response = llm_client.chat(messages, tools=tools)

        # --- Check if the LLM wants to call tools ---
        if response["tool_calls"]:
            print(f"\n  [Agent] LLM requested {len(response['tool_calls'])} tool call(s):")

            # Add the assistant's raw response to conversation history
            messages.append({"role": "assistant", "content": response["raw"]})

            for tc in response["tool_calls"]:
                tool_name = tc["name"]
                tool_args = tc["arguments"]
                print(f"    -> {tool_name}({tool_args})")

                # Call the tool via MCP
                try:
                    tool_result = await call_mcp_tool(session, tool_name, tool_args)
                    print(f"    <- Got result ({len(tool_result)} chars)")
                except Exception as e:
                    tool_result = json.dumps({"error": str(e)})
                    print(f"    <- Error: {e}")

                # Feed the tool result back to the LLM
                messages.append({
                    "role": "tool",
                    "name": tool_name,
                    "content": tool_result,
                })

        # --- No tool calls: the LLM is done ---
        else:
            print(f"\n  [Agent] LLM finished after {iteration + 1} iteration(s).")
            return response["content"] or ""

    # Safety: if we hit max iterations
    print(f"\n  [Agent] Reached max iterations ({max_iterations}).")
    last = messages[-1]
    return last.get("content", "") if isinstance(last, dict) else str(last)


# ---------------------------------------------------------------------------
# Main Function: analyse_dish
# ---------------------------------------------------------------------------

async def analyse_dish(dish_name: str) -> str:
    """
    Analyse a dish using the Recipe MCP Server and the local LLM service.

    This is the main entry point for programmatic use. It:
      1. Starts the MCP server as a subprocess
      2. Connects to it and discovers tools
      3. Runs the agent loop with the dish name
      4. Returns the final analysis text

    Parameters
    ----------
    dish_name : str
        The name of the dish to analyse (e.g., "pasta carbonara").

    Returns
    -------
    str
        A comprehensive textual analysis of the dish, including ingredients,
        techniques, equipment, safety considerations, and robotic feasibility.

    Example
    -------
    >>> import asyncio
    >>> from recipe_agent import analyse_dish
    >>> result = asyncio.run(analyse_dish("pasta carbonara"))
    >>> print(result)
    """
    # Path to the MCP server script (same directory as this file)
    server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recipe_mcp_server.py")

    # Configure the MCP server connection via stdio
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )

    print(f"\n{'=' * 70}")
    print(f"  RECIPE AGENT: Analysing '{dish_name}'")
    print(f"{'=' * 70}")

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialise the MCP connection
            await session.initialize()
            print("\n  [Agent] Connected to Recipe MCP Server.")

            # Discover available tools
            tools_response = await session.list_tools()
            mcp_tools = tools_response.tools
            print(f"  [Agent] Discovered {len(mcp_tools)} tools:")
            for tool in mcp_tools:
                desc = (tool.description or "")[:80]
                print(f"    - {tool.name}: {desc}...")

            # Convert MCP tools to simple dict format for llm_client
            tools = [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "parameters": t.inputSchema if t.inputSchema else {"type": "object", "properties": {}},
                }
                for t in mcp_tools
            ]

            # Build the user message
            user_message = (
                f"Please provide a comprehensive analysis of '{dish_name}'. "
                f"Use all available tools to gather dish details, cooking techniques, "
                f"equipment specifications, and safety requirements. Then synthesise "
                f"everything into a clear, well-structured report that would help "
                f"someone understand exactly what is involved in preparing this dish, "
                f"especially from a robotics perspective."
            )

            # Run the agent loop
            result = await run_agent_loop(session, tools, user_message)

            print(f"\n{'=' * 70}")
            print("  ANALYSIS COMPLETE")
            print(f"{'=' * 70}\n")

            return result


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print()
    print("=" * 70)
    print("  RECIPE AGENT")
    print("  Session 4 - University of Hertfordshire AI Workshop")
    print("=" * 70)
    print()
    print("  This agent analyses dishes in detail, focusing on what a robot")
    print("  would need to know to prepare them.")
    print()

    # Get dish name from user
    dish_name = input("  Enter a dish name to analyse (e.g., 'pasta carbonara'): ").strip()

    if not dish_name:
        print("  No dish name entered. Using 'pasta carbonara' as default.")
        dish_name = "pasta carbonara"

    # Check for LLM service configuration
    if not os.getenv("LLM_SERVICE_URL"):
        print("\n  WARNING: LLM_SERVICE_URL not found in environment.")
        print("  Using default: http://localhost:8000")

    # Run the analysis
    result = asyncio.run(analyse_dish(dish_name))

    # Print the final analysis
    print("\n" + "=" * 70)
    print("  FINAL ANALYSIS")
    print("=" * 70 + "\n")
    print(result)
    print()
