"""
Step 2: Multi-turn Conversation
=================================
This shows how conversation history works.
The LLM can remember what you said earlier in the conversation.

    python steps/step2_conversation.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import llm_client

llm_client.check_health()
print("Multi-turn conversation demo\n")

# The conversation history — each message has a role and content
conversation = [
    {"role": "system", "content": "You are a helpful assistant for university students."},
    {"role": "user", "content": "What is machine learning?"},
]

# --- Turn 1 ---
print("You: What is machine learning?")
reply1 = llm_client.chat(conversation)
print(f"AI:  {reply1}\n")

# Add the AI's reply to history, then ask a follow-up
conversation.append({"role": "assistant", "content": reply1})
conversation.append({"role": "user", "content": "Give me one real-world example of it."})

# --- Turn 2 ---
# The model sees the FULL conversation and knows "it" = machine learning
print("You: Give me one real-world example of it.")
reply2 = llm_client.chat(conversation)
print(f"AI:  {reply2}\n")

print("="*50)
print("KEY INSIGHT: The model remembers the conversation because")
print("we send ALL previous messages with each request.")
print("="*50)
