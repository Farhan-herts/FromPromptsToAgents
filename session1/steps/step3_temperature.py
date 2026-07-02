"""
Step 3: Temperature — Creativity vs Consistency
==================================================
Temperature controls how "creative" or "random" the model is.
Low temperature = focused, predictable. High = creative, varied.

    python steps/step3_temperature.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import llm_client

llm_client.check_health()

question = "Write a one-sentence description of a futuristic city."

for temp in [0.2, 1.0]:
    label = "LOW (0.2) — focused" if temp == 0.2 else "HIGH (1.0) — creative"
    print(f"\nTemperature {label}:")
    reply = llm_client.chat(
        [{"role": "system", "content": "You are a creative writer."},
         {"role": "user", "content": question}],
        temperature=temp,
    )
    print(f"  {reply}")

print("\n" + "="*50)
print("KEY: Same model, same question, different temperature")
print("     → different style of answer.")
print("="*50)
