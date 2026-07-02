"""
Step 3: Run the Recipe Agent
===============================
The full agent: LLM + MCP tools working together.

    python steps/step3_run_agent.py

Try: pasta carbonara, sushi rolls, chocolate cake, french omelette
"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from recipe_agent import analyse_dish

dish = input("Enter a dish name (or press Enter for default): ").strip()
if not dish:
    dish = "pasta carbonara"

result = asyncio.run(analyse_dish(dish))
print("\n" + "=" * 60)
print("  FINAL ANALYSIS")
print("=" * 60 + "\n")
print(result)
