"""
Step 1: Explore the Robotics Knowledge Base
==============================================
Before building the agent, let's look at the data it will use.
Our "knowledge base" is three JSON files with robotics parts.

    python steps/step1_explore_data.py
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "robotics_data"

print("=" * 60)
print("  ROBOTICS KNOWLEDGE BASE")
print("=" * 60)

for filename in ["components.json", "sensors.json", "actuators.json"]:
    data = json.loads((DATA_DIR / filename).read_text())
    print(f"\n📦 {filename} — {len(data)} items:")
    for item in data:
        tags = ", ".join(item["suitable_for"][:3])
        print(f"   {item['id']:10s}  {item['name'][:40]:40s}  [{tags}]")

print("\n" + "=" * 60)
print("Each item has: id, name, type, description, specifications,")
print("and a 'suitable_for' list that the agent uses to find matches.")
print("=" * 60)
