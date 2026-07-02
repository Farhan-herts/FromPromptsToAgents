"""
Step 5: Prompt Engineering — Same Question, Three Experts
============================================================
See how the SAME model gives completely different answers
depending on the system prompt. Run with:

    streamlit run steps/step5_personas.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import streamlit as st
import llm_client

st.set_page_config(page_title="Prompt Engineering", page_icon="🧠", layout="wide")
st.title("🧠 Prompt Engineering: Three Experts")
st.markdown("Send the **same question** to three AI personas and compare.")

PERSONAS = {
    "🏗️ primary student": (
        "You are primary school student, "
        "you have no idea because you are not mature enough"
    ),
    "🤖 Game Developer": (
        "You are an expert game developer. Focus on game development, game enviornment, "
        "please give answers in English."
    ),
    "🎨 Angry Person": (
        "You are a angry person and try to avoid the question, "
        "and you are very straight forward"
    ),
}

question = st.text_input("Your question:", value="How can I build a bridge?")

if st.button("Compare Responses", type="primary"):
    cols = st.columns(3)
    for col, (name, prompt) in zip(cols, PERSONAS.items()):
        with col:
            st.subheader(name)
            with st.spinner("Thinking..."):
                reply = llm_client.chat([
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question},
                ], max_tokens=400)
                st.markdown(reply)

st.info(
    "**Key insight:** The model has NOT changed — only your instructions have. "
    "This is how you build agents with different roles."
)
