"""
Step 1: Explore the Recipe Database
======================================
Look at the dishes and techniques available to the Recipe Agent.

    python steps/step1_explore_dishes.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the databases directly from the MCP server module
# (we can do this because the data is defined as Python dicts)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "recipe_server",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipe_mcp_server.py")
)
mod = importlib.util.find_spec("mcp") # just check mcp is installed

# Simpler approach: just read the key info
from recipe_mcp_server import DISH_DATABASE, TECHNIQUE_DATABASE, EQUIPMENT_DATABASE

print("=" * 60)
print("  RECIPE DATABASE")
print("=" * 60)

print(f"\n🍽️  {len(DISH_DATABASE)} dishes available:\n")
for key, dish in DISH_DATABASE.items():
    techniques = ", ".join(dish["cooking_techniques"][:4])
    print(f"  {dish['dish_name']:25s}  {dish['cuisine_type']:15s}  "
          f"Difficulty: {dish['difficulty']:8s}  [{techniques}]")

print(f"\n🔧 {len(TECHNIQUE_DATABASE)} cooking techniques with robotic feasibility ratings")
print(f"🍳 {len(EQUIPMENT_DATABASE)} equipment items with specs\n")

print("=" * 60)
print("The Recipe Agent will search this data using 4 MCP tools:")
print("  1. analyse_dish         — full dish breakdown")
print("  2. get_cooking_techniques — technique details + robot feasibility")
print("  3. get_equipment_specs  — equipment specifications")
print("  4. get_safety_requirements — safety considerations")
print("=" * 60)
