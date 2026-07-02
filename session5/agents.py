"""
Multi-Agent System: Constraint-Aware Recipe Agent + Robotics Agent
=================================================================
Session 5: The Challenge - Robotic Chef Platform

This module extends the original A2A pipeline with budget, servings,
and nutrition constraints:
1. Agent 1 receives a meal request plus constraints
2. Agent 1 uses the Recipe MCP Server to shortlist dishes that fit
3. Agent 1 selects the best dish, explains the trade-off, and builds
   a structured robotics task specification
4. Agent 2 uses the Robotics MCP Server to design a robotic platform
5. The final result returns both the culinary analysis and robot design

All LLM calls go through llm_client (local LLM service via requests).
"""

import asyncio
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

import llm_client

SERVER_DIR = Path(__file__).parent


@dataclass
class MealConstraints:
    meal_request: str
    budget_usd: float = 20.0
    servings: int = 2
    min_protein_g: float = 0.0
    max_calories_kcal: float = 0.0
    preferred_dish: str = ""

    def to_prompt_block(self) -> str:
        preferred = self.preferred_dish.strip() or "None"
        calorie_text = (
            f"{self.max_calories_kcal:.0f} kcal per serving"
            if self.max_calories_kcal > 0
            else "No calorie cap"
        )
        return (
            f"Meal request: {self.meal_request}\n"
            f"Preferred dish: {preferred}\n"
            f"Budget: ${self.budget_usd:.2f}\n"
            f"Servings: {self.servings}\n"
            f"Minimum protein: {self.min_protein_g:.0f} g per serving\n"
            f"Maximum calories: {calorie_text}"
        )


async def run_agent_with_mcp(
    server_script: str,
    system_prompt: str,
    user_message: str,
    status_callback=None,
) -> str:
    """Run a generic MCP-backed tool-using agent loop."""

    def _status(message: str) -> None:
        if status_callback:
            status_callback(message)

    _status(f"Starting MCP server: {Path(server_script).name}")
    server_path = str(Path(server_script).resolve())

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[server_path],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            _status("MCP session initialised")

            tools_result = await session.list_tools()
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                    if tool.inputSchema
                    else {"type": "object", "properties": {}},
                }
                for tool in tools_result.tools
            ]
            _status(
                f"Discovered {len(tools)} tools: "
                f"{', '.join(tool['name'] for tool in tools)}"
            )

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]

            last_content = ""
            for iteration in range(10):
                _status(f"LLM call (iteration {iteration + 1})")
                response = llm_client.chat(messages, tools=tools)

                if response["tool_calls"]:
                    messages.append(
                        {"role": "assistant", "content": response["raw"]}
                    )

                    for tool_call in response["tool_calls"]:
                        fn_name = tool_call["name"]
                        fn_args = tool_call["arguments"]
                        _status(f"Calling tool: {fn_name}")

                        try:
                            result = await session.call_tool(fn_name, fn_args)
                            tool_output = ""
                            if result.content:
                                for content_block in result.content:
                                    if hasattr(content_block, "text"):
                                        tool_output += content_block.text
                            _status(
                                f"Tool {fn_name} returned {len(tool_output)} chars"
                            )
                        except Exception as exc:
                            tool_output = json.dumps({"error": str(exc)})
                            _status(f"Tool {fn_name} error: {exc}")

                        messages.append(
                            {
                                "role": "tool",
                                "name": fn_name,
                                "content": tool_output,
                            }
                        )
                else:
                    _status("Agent produced final response")
                    return response["content"] or ""

                last_content = response.get("content") or ""

            _status("Max iterations reached")
            return (
                last_content
                or "Agent did not produce a final response within the iteration limit."
            )


FOOD_ANALYSIS_SYSTEM_PROMPT = """\
You are the Food Analysis Agent. You now have two jobs:
1. Meal planner: pick the best dish that fits the user's budget, servings,
   and nutrition constraints.
2. Culinary analyst: turn the chosen dish into a detailed robotics-ready task
   specification for Agent 2.

Workflow rules you MUST follow:
- First call find_matching_dishes using the exact user constraints.
- If the user gave a preferred dish, test it fairly against the constraints.
- Choose the best fitting dish. If no dish fits everything, choose the closest
  option and clearly explain the trade-off.
- After selecting a dish, call analyse_dish with the requested servings.
- Also call get_cooking_techniques, get_equipment_specs for key equipment,
  and get_safety_requirements.
- Your final answer must be plain text with headings and no tool_call tags.

Your final answer must contain these sections:

## User Constraints
- Meal request
- Preferred dish (if any)
- Budget
- Servings
- Protein target
- Calorie cap

## Shortlisted Dishes
- 2-4 strongest candidates with cost and nutrition snapshots

## Selected Dish and Trade-off
- Selected dish name
- Why it was chosen
- Whether it fully fits all constraints
- If not, what trade-off was made

## Budget and Nutrition Summary
- Total recipe cost
- Cost per serving
- Protein per serving
- Calories per serving
- Total protein for the full recipe
- Total calories for the full recipe

## Dish Overview
- Name, cuisine, difficulty, servings, total time

## Physical Tasks Required
For each important cooking step, describe the robotic physical action needed.
Include cutting, stirring, pouring, heating, timing, and plating actions.

## Cooking Techniques with Precision Requirements
List each technique with exact temperatures, durations, precision level,
and failure modes.

## Equipment to Operate
For each important piece of equipment, explain how it is used and what physical
interaction is required.

## Safety Requirements
- Temperature hazards
- Splash and spill risks
- Timing-critical steps
- Food-safety considerations

## Robotics Task Specification
Summarise all manipulation tasks, sensing requirements, workspace needs,
speed/timing constraints, and robot safety constraints.
"""


ROBOTICS_DESIGN_SYSTEM_PROMPT = """\
You are the Robotics Design Agent, an expert in robotic cooking platforms.
You will receive a constraint-aware task specification from Agent 1.
The selected dish, requested servings, and operational requirements in that
specification are the source of truth.

Use the available tools to:
1. Search for suitable robot arms/platforms
2. Find suitable sensors
3. Find actuators and end-effectors
4. Get full specifications for chosen items
5. Use the recommendation tool for a strong starting point

Your final answer must contain these sections:

## Robot Design Overview
- Robot type and overall rationale
- Single-arm vs dual-arm justification
- Stationary vs mobile justification

## Selected Components
For each component include ID, name, key specs, and why it was chosen.

## Sensor Suite
For each sensor include ID, name, purpose, and mounting recommendation.

## Actuators and End-Effectors
For each actuator include ID, name, task role, and relevant specs.

## Motion and Control Requirements
- Degrees of freedom needed
- Speed requirements
- Force-control needs
- Coordination between parallel operations

## Safety and Compliance
- Hot-surface safety
- Human-robot interaction safety
- Food-safety compliance
- Emergency-stop scenarios

## Platform Summary Table
Provide a compact summary table with IDs, names, and roles.

## Estimated Capabilities
- Fully autonomous steps
- Steps needing human oversight
- Overall autonomy estimate

Be specific and reference actual component IDs from the database.
"""


async def run_food_analysis_agent(
    constraints: MealConstraints,
    status_callback=None,
) -> str:
    server_script = str(SERVER_DIR / "recipe_mcp_server.py")
    user_message = (
        "Please plan a dish and analyse it for a robotic chef pipeline.\n\n"
        f"{constraints.to_prompt_block()}\n\n"
        "Important: shortlist dishes first, then choose the best fit, explain the "
        "trade-off, and build the robotics-ready task specification."
    )

    return await run_agent_with_mcp(
        server_script=server_script,
        system_prompt=FOOD_ANALYSIS_SYSTEM_PROMPT,
        user_message=user_message,
        status_callback=status_callback,
    )


async def run_robotics_agent(
    task_specification: str,
    status_callback=None,
) -> str:
    server_script = str(SERVER_DIR / "robotics_mcp_server.py")
    user_message = (
        "Design a complete robotic cooking platform based on the following "
        "constraint-aware task specification from the Food Analysis Agent.\n\n"
        f"--- TASK SPECIFICATION ---\n{task_specification}\n--- END SPECIFICATION ---"
    )

    return await run_agent_with_mcp(
        server_script=server_script,
        system_prompt=ROBOTICS_DESIGN_SYSTEM_PROMPT,
        user_message=user_message,
        status_callback=status_callback,
    )


async def run_robotic_chef_pipeline(
    meal_request: str,
    budget_usd: float = 20.0,
    servings: int = 2,
    min_protein_g: float = 0.0,
    max_calories_kcal: float = 0.0,
    preferred_dish: str = "",
    status_callback=None,
) -> dict:
    """Run the full A2A robotic chef pipeline with constraints."""

    constraints = MealConstraints(
        meal_request=meal_request.strip(),
        budget_usd=float(budget_usd),
        servings=int(servings),
        min_protein_g=float(min_protein_g),
        max_calories_kcal=float(max_calories_kcal),
        preferred_dish=preferred_dish.strip(),
    )

    def _status(message: str) -> None:
        if status_callback:
            status_callback(message)

    _status("=== Stage 1: Constraint-Aware Food Analysis Agent ===")
    food_analysis = await run_food_analysis_agent(
        constraints=constraints,
        status_callback=status_callback,
    )
    _status("Food Analysis Agent complete")

    _status("=== Stage 2: Robotics Designer Agent ===")
    robot_design = await run_robotics_agent(
        task_specification=food_analysis,
        status_callback=status_callback,
    )
    _status("Robotics Designer Agent complete")

    return {
        "request_summary": asdict(constraints),
        "food_analysis": food_analysis,
        "robot_design": robot_design,
    }


async def _main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Constraint-aware Robotic Chef Pipeline"
    )
    parser.add_argument(
        "meal_request",
        nargs="?",
        default="high protein pasta",
        help="Meal request, for example: 'high protein pasta'",
    )
    parser.add_argument("--budget", type=float, default=20.0)
    parser.add_argument("--servings", type=int, default=2)
    parser.add_argument("--protein", type=float, default=25.0)
    parser.add_argument("--calories", type=float, default=850.0)
    parser.add_argument("--preferred-dish", default="")
    args = parser.parse_args()

    def print_status(message: str) -> None:
        print(f"  [{message}]")

    print("\nRobotic Chef Pipeline - Constraint Aware")
    print("=" * 60)
    print(f"Request: {args.meal_request}")
    print(f"Budget: ${args.budget:.2f} | Servings: {args.servings}")
    print(
        f"Protein target: {args.protein:.0f} g/serving | "
        f"Calorie cap: {args.calories:.0f} kcal/serving"
    )
    if args.preferred_dish:
        print(f"Preferred dish: {args.preferred_dish}")

    result = await run_robotic_chef_pipeline(
        meal_request=args.meal_request,
        budget_usd=args.budget,
        servings=args.servings,
        min_protein_g=args.protein,
        max_calories_kcal=args.calories,
        preferred_dish=args.preferred_dish,
        status_callback=print_status,
    )

    print("\n" + "=" * 60)
    print("FOOD ANALYSIS (Agent 1)")
    print("=" * 60)
    print(result["food_analysis"])

    print("\n" + "=" * 60)
    print("ROBOT DESIGN (Agent 2)")
    print("=" * 60)
    print(result["robot_design"])


if __name__ == "__main__":
    asyncio.run(_main())
