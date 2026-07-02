"""
Step 1: Your First LLM Call
=============================
Run this file to send a message to an LLM and get a response.
This is the simplest possible interaction with an AI model.

    python steps/step1_hello_llm.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import llm_client

# --- Check which LLM is available ---
print("Checking LLM connection...")
health = llm_client.check_health()
print(f"  Backend: {health['backend']}  |  Model: {health['model']}")
print()

if not health["model_loaded"]:
    print("ERROR: No LLM available.")
    print("Fix: set GEMINI_API_KEY in your .env file (see README)")
    exit(1)

# --- Send a simple message ---
print("Sending: 'What is an AI agent? Answer in two sentences.'")
print()

response = llm_client.chat([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is an AI agent? Answer in two sentences."},
])

print(f"Response:\n{response}")
print()

# --- Try it yourself! ---
print("="*50)
print("YOUR TURN: Edit the user message above and re-run!")
print("Try asking: 'Explain machine learning to a 10-year-old'")
print("="*50)
