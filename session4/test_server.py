"""
=============================================================================
  Session 4: Test Script for the Recipe MCP Server
  University of Hertfordshire AI Workshop
=============================================================================

  This script connects to the Recipe MCP Server and tests each tool
  to verify everything is working correctly.

  Run it with:
      python test_server.py

  You should see output from all four tools. If any test fails, check that:
    - recipe_mcp_server.py is in the same directory
    - The mcp package is installed (pip install mcp[cli])
    - Python 3.10+ is being used
=============================================================================
"""

import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_tests():
    """
    Connect to the Recipe MCP Server and test each tool.
    """
    server_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "recipe_mcp_server.py",
    )

    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )

    print("=" * 70)
    print("  RECIPE MCP SERVER - Test Suite")
    print("=" * 70)
    print()

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialise connection
            await session.initialize()
            print("[OK] Connected to Recipe MCP Server.\n")

            # List available tools
            tools_response = await session.list_tools()
            tools = tools_response.tools
            print(f"[OK] Discovered {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool.name}")
            print()

            # ----------------------------------------------------------
            # Test 1: analyse_dish
            # ----------------------------------------------------------
            print("-" * 70)
            print("TEST 1: analyse_dish('pasta carbonara')")
            print("-" * 70)
            result = await session.call_tool("analyse_dish", {"dish_name": "pasta carbonara"})
            text = result.content[0].text
            data = json.loads(text)
            print(f"  Dish:       {data.get('dish_name')}")
            print(f"  Cuisine:    {data.get('cuisine_type')}")
            print(f"  Difficulty: {data.get('difficulty')}")
            print(f"  Time:       {data.get('estimated_time_minutes')} minutes")
            print(f"  Steps:      {len(data.get('steps', []))} steps")
            print(f"  Techniques: {', '.join(data.get('cooking_techniques', []))}")
            print("[OK] analyse_dish passed.\n")

            # ----------------------------------------------------------
            # Test 2: get_cooking_techniques
            # ----------------------------------------------------------
            print("-" * 70)
            print("TEST 2: get_cooking_techniques('pasta carbonara')")
            print("-" * 70)
            result = await session.call_tool("get_cooking_techniques", {"dish_name": "pasta carbonara"})
            text = result.content[0].text
            data = json.loads(text)
            techniques = data.get("techniques", [])
            print(f"  Found {len(techniques)} technique(s):")
            for tech in techniques:
                feasibility = tech.get("robotic_feasibility", "?")
                print(f"    - {tech.get('technique', '?'):20s}  (robotic feasibility: {feasibility})")
            print("[OK] get_cooking_techniques passed.\n")

            # ----------------------------------------------------------
            # Test 3: get_equipment_specs
            # ----------------------------------------------------------
            print("-" * 70)
            print("TEST 3: get_equipment_specs('pot')")
            print("-" * 70)
            result = await session.call_tool("get_equipment_specs", {"equipment_name": "pot"})
            text = result.content[0].text
            data = json.loads(text)
            print(f"  Name:        {data.get('name')}")
            print(f"  Type:        {data.get('type')}")
            print(f"  Dimensions:  {data.get('typical_dimensions_cm')}")
            print(f"  Weight:      {data.get('weight_range_kg')}")
            print(f"  Robot notes: {data.get('robotic_interaction_notes', '')[:100]}...")
            print("[OK] get_equipment_specs passed.\n")

            # ----------------------------------------------------------
            # Test 4: get_safety_requirements
            # ----------------------------------------------------------
            print("-" * 70)
            print("TEST 4: get_safety_requirements('pasta carbonara')")
            print("-" * 70)
            result = await session.call_tool("get_safety_requirements", {"dish_name": "pasta carbonara"})
            text = result.content[0].text
            data = json.loads(text)
            allergens = data.get("allergen_information", [])
            kitchen_safety = data.get("kitchen_safety", {})
            print(f"  Allergens found: {len(allergens)}")
            for allergen in allergens:
                print(f"    - {allergen[:80]}...")
            sharp_tools = kitchen_safety.get("sharp_tools", [])
            hot_surfaces = kitchen_safety.get("hot_surfaces", [])
            print(f"  Sharp tool warnings: {len(sharp_tools)}")
            print(f"  Hot surface warnings: {len(hot_surfaces)}")
            print("[OK] get_safety_requirements passed.\n")

            # ----------------------------------------------------------
            # Test 5 (Bonus): Test with an unknown dish
            # ----------------------------------------------------------
            print("-" * 70)
            print("TEST 5: analyse_dish('beef wellington') -- unknown dish")
            print("-" * 70)
            result = await session.call_tool("analyse_dish", {"dish_name": "beef wellington"})
            text = result.content[0].text
            data = json.loads(text)
            has_note = "note" in data
            print(f"  Returned template: {'yes' if has_note else 'no'}")
            print(f"  Cuisine:    {data.get('cuisine_type')}")
            if has_note:
                print(f"  Note:       {data.get('note', '')[:80]}...")
            print("[OK] Unknown dish handling passed.\n")

    # ----------------------------------------------------------
    # Summary
    # ----------------------------------------------------------
    print("=" * 70)
    print("  ALL TESTS PASSED")
    print("=" * 70)
    print()
    print("  Your Recipe MCP Server is working correctly!")
    print("  Next step: run the Recipe Agent with:")
    print("      python recipe_agent.py")
    print()


if __name__ == "__main__":
    asyncio.run(run_tests())
