"""
Step 2: Test the Recipe MCP Tools
====================================
Test each tool before running the full agent.

    python steps/step2_test_tools.py
"""
import asyncio, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe_mcp_server.py")


async def main():
    params = StdioServerParameters(command="python", args=[SERVER])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available tools:")
            for t in tools.tools:
                print(f"  - {t.name}")

            # Test analyse_dish
            print("\n--- analyse_dish('pasta carbonara') ---")
            r = await session.call_tool("analyse_dish", {"dish_name": "pasta carbonara"})
            data = json.loads(r.content[0].text)
            print(f"  Dish: {data['dish_name']}")
            print(f"  Cuisine: {data['cuisine_type']}, Difficulty: {data['difficulty']}")
            print(f"  Steps: {len(data['steps'])}, Time: {data['estimated_time_minutes']} min")
            print(f"  Techniques: {', '.join(data['cooking_techniques'])}")

            # Test safety
            print("\n--- get_safety_requirements('fish and chips') ---")
            r = await session.call_tool("get_safety_requirements", {"dish_name": "fish and chips"})
            safety = json.loads(r.content[0].text)
            print(f"  Fire risks: {len(safety['kitchen_safety']['fire_and_burn_risks'])}")
            print(f"  Allergens: {len(safety['allergen_information'])}")

    print("\n✅ All tools working!")

asyncio.run(main())
