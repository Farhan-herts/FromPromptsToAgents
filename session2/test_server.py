"""
Quick test script to verify the MCP server works correctly.
=============================================================

Run this BEFORE running the full agent to make sure your MCP server
is set up properly and all tools respond as expected.

Usage:
    python test_server.py
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test():
    """Connect to the MCP server and test each tool."""

    server_params = StdioServerParameters(
        command="python",
        args=["robotics_mcp_server.py"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List all available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Test 1: Search components by category
            print("\n--- Testing search_components (category=manipulator) ---")
            result = await session.call_tool("search_components", {"category": "manipulator"})
            print(result.content[0].text)

            # Test 2: Search sensors by type
            print("\n--- Testing search_sensors (sensor_type=vision) ---")
            result = await session.call_tool("search_sensors", {"sensor_type": "vision"})
            print(result.content[0].text)

            # Test 3: Search all actuators (no filter)
            print("\n--- Testing search_actuators (no filter) ---")
            result = await session.call_tool("search_actuators", {})
            print(result.content[0].text)

            # Test 4: Get details for a specific component
            print("\n--- Testing get_component_details (comp-001) ---")
            result = await session.call_tool("get_component_details", {"component_id": "comp-001"})
            print(result.content[0].text)

            # Test 5: Recommend a platform for a task
            print("\n--- Testing recommend_platform ---")
            result = await session.call_tool(
                "recommend_platform",
                {"task_description": "pick and place objects on a conveyor belt"}
            )
            print(result.content[0].text)

            print("\n" + "=" * 40)
            print("All tests passed! Server is working.")
            print("=" * 40)


if __name__ == "__main__":
    asyncio.run(test())
