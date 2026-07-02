"""
Robotics MCP Server
====================
An MCP (Model Context Protocol) server that exposes tools for querying
a database of robotics components, sensors, and actuators.

This server is used by the Robotics Agent to look up parts when designing
a robotics platform for a given task.

Run directly:
    python robotics_mcp_server.py

Or connect to it from the agent via stdio transport.
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Create the MCP server instance
# ---------------------------------------------------------------------------
mcp = FastMCP("Robotics Platform Builder")

# ---------------------------------------------------------------------------
# Load data files at startup
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).parent / "robotics_data"


def load_json(filename: str) -> list[dict]:
    """Load a JSON data file from the robotics_data directory."""
    with open(DATA_DIR / filename) as f:
        return json.load(f)


COMPONENTS = load_json("components.json")
SENSORS = load_json("sensors.json")
ACTUATORS = load_json("actuators.json")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _format_item(item: dict) -> str:
    """Format a single database item into a readable string."""
    lines = [
        f"  ID: {item['id']}",
        f"  Name: {item['name']}",
    ]
    # Include category or type depending on what's present
    if "category" in item:
        lines.append(f"  Category: {item['category']}")
    if "type" in item:
        lines.append(f"  Type: {item['type']}")
    lines.append(f"  Description: {item['description']}")
    lines.append(f"  Specs: {json.dumps(item['specifications'], indent=4)}")
    lines.append(f"  Suitable for: {', '.join(item['suitable_for'])}")
    return "\n".join(lines)


def _matches_task(item: dict, task: str) -> bool:
    """Check if any keyword in the task matches the item's suitable_for list."""
    task_lower = task.lower()
    task_words = task_lower.split()
    for use_case in item.get("suitable_for", []):
        use_case_lower = use_case.lower()
        # Match if the entire task string contains the use case,
        # or if any word in the task appears in the use case
        if use_case_lower in task_lower:
            return True
        for word in task_words:
            if len(word) > 3 and word in use_case_lower:
                return True
    return False


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def search_components(category: str = None, task: str = None) -> str:
    """Search the robotics components database.

    Args:
        category: Filter by component category. Options: manipulator,
                  mobile_base, controller, frame, power.
        task: Filter by task suitability (e.g. 'pick and place',
              'welding', 'navigation'). Uses keyword matching.

    Returns:
        A formatted list of matching components.
    """
    results = COMPONENTS

    # Filter by category if provided
    if category:
        category_lower = category.lower()
        results = [c for c in results if c["category"].lower() == category_lower]

    # Filter by task if provided
    if task:
        results = [c for c in results if _matches_task(c, task)]

    if not results:
        return "No components found matching the given criteria."

    header = f"Found {len(results)} component(s):\n"
    items = "\n\n".join(_format_item(c) for c in results)
    return header + items


@mcp.tool()
def search_sensors(sensor_type: str = None, task: str = None) -> str:
    """Search the robotics sensors database.

    Args:
        sensor_type: Filter by sensor type. Options: vision, temperature,
                     force, proximity, lidar, imu.
        task: Filter by task suitability (e.g. 'navigation', 'inspection',
              'object detection'). Uses keyword matching.

    Returns:
        A formatted list of matching sensors.
    """
    results = SENSORS

    # Filter by sensor type if provided
    if sensor_type:
        type_lower = sensor_type.lower()
        results = [s for s in results if s["type"].lower() == type_lower]

    # Filter by task if provided
    if task:
        results = [s for s in results if _matches_task(s, task)]

    if not results:
        return "No sensors found matching the given criteria."

    header = f"Found {len(results)} sensor(s):\n"
    items = "\n\n".join(_format_item(s) for s in results)
    return header + items


@mcp.tool()
def search_actuators(actuator_type: str = None, task: str = None) -> str:
    """Search the robotics actuators/end-effectors database.

    Args:
        actuator_type: Filter by actuator type. Options: gripper, pump,
                       nozzle, cutter, welder, stirrer.
        task: Filter by task suitability (e.g. 'pick and place', 'welding',
              'food handling'). Uses keyword matching.

    Returns:
        A formatted list of matching actuators.
    """
    results = ACTUATORS

    # Filter by actuator type if provided
    if actuator_type:
        type_lower = actuator_type.lower()
        results = [a for a in results if a["type"].lower() == type_lower]

    # Filter by task if provided
    if task:
        results = [a for a in results if _matches_task(a, task)]

    if not results:
        return "No actuators found matching the given criteria."

    header = f"Found {len(results)} actuator(s):\n"
    items = "\n\n".join(_format_item(a) for a in results)
    return header + items


@mcp.tool()
def get_component_details(component_id: str) -> str:
    """Get detailed information about a specific component by its ID.

    Searches across all three databases (components, sensors, actuators).

    Args:
        component_id: The unique ID of the component (e.g. 'comp-001',
                      'sens-003', 'act-002').

    Returns:
        Detailed information about the component, or an error message
        if the ID is not found.
    """
    # Search all three databases
    all_items = COMPONENTS + SENSORS + ACTUATORS

    for item in all_items:
        if item["id"].lower() == component_id.lower():
            return f"Component Details:\n{_format_item(item)}"

    return f"No component found with ID '{component_id}'. Use search tools to find valid IDs."


@mcp.tool()
def recommend_platform(task_description: str) -> str:
    """Get a list of potentially suitable parts for a given robotics task.

    Searches all databases (components, sensors, actuators) and returns
    items whose 'suitable_for' tags match keywords in the task description.

    Args:
        task_description: A description of the robotics task, e.g.
            'autonomous warehouse delivery robot' or
            'pick and place objects on a conveyor belt'.

    Returns:
        A combined list of matching components, sensors, and actuators.
    """
    matching_components = [c for c in COMPONENTS if _matches_task(c, task_description)]
    matching_sensors = [s for s in SENSORS if _matches_task(s, task_description)]
    matching_actuators = [a for a in ACTUATORS if _matches_task(a, task_description)]

    sections = []

    if matching_components:
        section = f"=== Matching Components ({len(matching_components)}) ===\n"
        section += "\n\n".join(_format_item(c) for c in matching_components)
        sections.append(section)

    if matching_sensors:
        section = f"=== Matching Sensors ({len(matching_sensors)}) ===\n"
        section += "\n\n".join(_format_item(s) for s in matching_sensors)
        sections.append(section)

    if matching_actuators:
        section = f"=== Matching Actuators ({len(matching_actuators)}) ===\n"
        section += "\n\n".join(_format_item(a) for a in matching_actuators)
        sections.append(section)

    if not sections:
        return (
            f"No directly matching parts found for: '{task_description}'.\n"
            "Try using the individual search tools with broader terms, "
            "or browse all components/sensors/actuators without filters."
        )

    header = f"Recommended parts for: '{task_description}'\n\n"
    return header + "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Run the server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
