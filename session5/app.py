"""
Robotic Chef Platform - Constraint-Aware Multi-Agent AI System
===============================================================

This Streamlit app extends the original RobotChef A2A demo with the Session 5
challenge requirements:
- budget input
- serving count
- nutrition targets (protein and calories)
- Agent 1 selects the best dish before Agent 2 designs the robot

Run with:
    streamlit run app.py
"""

import asyncio
import os

import streamlit as st
from dotenv import load_dotenv

from agents import run_robotic_chef_pipeline
import llm_client

load_dotenv()

st.set_page_config(
    page_title="Smart Budget RobotChef",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

with st.sidebar:
    st.header("Challenge Flow")
    st.markdown(
        """
        **User input**
        - meal request
        - budget
        - servings
        - protein target
        - calorie cap

        **Agent 1**
        - shortlists matching dishes
        - picks the best fit
        - explains the trade-off
        - builds the robotics task spec

        **Agent 2**
        - designs the robot platform
        - selects components, sensors, and actuators
        """
    )

    st.divider()
    st.header("Example Requests")
    st.markdown(
        """
        - high protein pasta
        - quick Japanese meal
        - low calorie dinner
        - something with beef
        - affordable stir-fry
        """
    )

    st.divider()
    st.caption(
        "Constraint-aware RobotChef\n\n"
        "Agent-to-Agent meal planning + robot design"
    )

st.title("🍽️ Smart Budget RobotChef")
st.markdown("### Budget + Nutrition + A2A Robotics")
st.markdown(
    """
    Enter a meal request and the system will:
    1. let **Agent 1** choose the best dish that fits your budget and nutrition needs
    2. pass that task specification into **Agent 2**
    3. generate a robotic cooking platform for the selected dish
    """
)

health = llm_client.check_health()
if health["status"] == "online":
    st.success(
        f"LLM backend online: {health['backend']} | model: {health['model']}"
    )
else:
    st.error(
        "No LLM backend is available. Configure the local LLM service or a "
        "Gemini API key before running the app."
    )

with st.form("robotchef_form"):
    col1, col2 = st.columns([2, 1])

    with col1:
        meal_request = st.text_input(
            "Meal request",
            placeholder="e.g. high protein pasta, affordable beef dinner, quick sushi-style meal",
        )
        preferred_dish = st.text_input(
            "Preferred dish (optional)",
            placeholder="e.g. pasta carbonara",
        )

    with col2:
        budget_usd = st.number_input(
            "Budget ($)",
            min_value=1.0,
            max_value=250.0,
            value=20.0,
            step=1.0,
        )
        servings = st.selectbox("Servings", options=[2, 3, 4], index=0)

    col3, col4 = st.columns(2)
    with col3:
        min_protein_g = st.number_input(
            "Min protein per serving (g)",
            min_value=0.0,
            max_value=200.0,
            value=25.0,
            step=1.0,
        )
    with col4:
        max_calories_kcal = st.number_input(
            "Max calories per serving (kcal)",
            min_value=0.0,
            max_value=3000.0,
            value=850.0,
            step=25.0,
        )

    run_button = st.form_submit_button(
        "Plan Meal + Design Robot",
        type="primary",
        use_container_width=True,
    )

if run_button and not meal_request.strip():
    st.warning("Please enter a meal request before running the pipeline.")

elif run_button and meal_request.strip():
    status_container = st.status(
        f"Running RobotChef for: **{meal_request}**",
        expanded=True,
    )
    status_lines = []

    def status_callback(message: str) -> None:
        status_lines.append(message)
        with status_container:
            st.text(message)

    try:
        try:
            running_loop = asyncio.get_running_loop()
        except RuntimeError:
            running_loop = None

        pipeline_kwargs = dict(
            meal_request=meal_request,
            budget_usd=budget_usd,
            servings=servings,
            min_protein_g=min_protein_g,
            max_calories_kcal=max_calories_kcal,
            preferred_dish=preferred_dish,
            status_callback=status_callback,
        )

        if running_loop and running_loop.is_running():
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = pool.submit(
                    asyncio.run,
                    run_robotic_chef_pipeline(**pipeline_kwargs),
                ).result()
        else:
            result = asyncio.run(run_robotic_chef_pipeline(**pipeline_kwargs))

        status_container.update(
            label="Pipeline complete!",
            state="complete",
            expanded=False,
        )

        st.divider()
        summary = result["request_summary"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Budget", f"${summary['budget_usd']:.2f}")
        m2.metric("Servings", summary["servings"])
        m3.metric("Min Protein", f"{summary['min_protein_g']:.0f} g")
        calorie_label = (
            f"{summary['max_calories_kcal']:.0f} kcal"
            if summary["max_calories_kcal"] > 0
            else "No cap"
        )
        m4.metric("Calorie Cap", calorie_label)

        if summary.get("preferred_dish"):
            st.info(f"Preferred dish: {summary['preferred_dish']}")

        with st.expander("Agent 1: Budget + Nutrition Meal Planning", expanded=True):
            st.markdown(result["food_analysis"])

        with st.expander("Agent 2: Robot Design", expanded=True):
            st.markdown(result["robot_design"])

    except Exception as exc:
        status_container.update(label="Pipeline failed", state="error")
        st.error(f"An error occurred: {exc}")
        st.exception(exc)
