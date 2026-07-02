"""
Step 2: Test the MCP Tools
============================
This runs the MCP server and tests each tool directly.
No LLM involved — just verifying the tools work.

    python steps/step2_test_tools.py
"""
import asyncio
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "robotics_mcp_server.py")


async def main():
    server_params = StdioServerParameters(
        command="python", args=[SERVER],
        cwd=os.path.dirname(SERVER),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print("Available tools:")
            for t in tools.tools:
                print(f"  - {t.name}")

            # Test: search for vision sensors
            print("\n--- search_sensors(sensor_type='vision') ---")
            result = await session.call_tool("search_sensors", {"sensor_type": "vision"})
            print(result.content[0].text[:500])

            # Test: search components for sorting tasks
            print("\n--- search_components(task='sorting') ---")
            result = await session.call_tool("search_components", {"task": "sorting"})
            print(result.content[0].text[:500])

            # Test: recommend platform
            print("\n--- recommend_platform('autonomous delivery') ---")
            result = await session.call_tool("recommend_platform", {"task_description": "autonomous delivery"})
            print(result.content[0].text[:500])

    print("\n✅ All tools working!")


asyncio.run(main())
