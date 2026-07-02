import time
import requests
import streamlit as st

BASE_URL = "https://uhhpc.herts.ac.uk/qwen"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsIm5hbWUiOiJLaGFzaGF5YXIiLCJyb2xlIjoicHJpbmNpcGFsX2FpX2VuZ2luZWVyIiwiaWF0IjoxNzc0MjE0NzY0LCJleHAiOjE3NzQyMTgzNjR9.6cyxd0svDfs1Hzh29CkMFidpgaBDinFa9nHXywq3F-Y"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

st.set_page_config(page_title="Qwen LLM Chat", page_icon="🤖", layout="wide")
st.title("Qwen LLM Chat")

# Sidebar – settings & health
with st.sidebar:
    st.header("Settings")
    max_tokens = st.slider("Max tokens", 64, 8192, 2048)
    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, step=0.1)
    top_p = st.slider("Top-p", 0.0, 1.0, 0.9, step=0.05)

    st.divider()
    if st.button("Check Service Health"):
        try:
            r = requests.get(f"{BASE_URL}/health", headers=HEADERS, timeout=10)
            data = r.json()
            if data.get("model_loaded"):
                st.success(f"Model: {data['model']} — Ready")
            else:
                st.warning(f"Model: {data['model']} — Loading...")
        except requests.exceptions.RequestException as e:
            st.error(f"Cannot reach service: {e}")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask Qwen anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generating..."):
            try:
                # Submit prompt
                resp = requests.post(
                    f"{BASE_URL}/generate",
                    headers=HEADERS,
                    json={
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                task_id = resp.json()["task_id"]

                # Poll for result
                while True:
                    result = requests.get(
                        f"{BASE_URL}/result/{task_id}",
                        headers=HEADERS,
                        timeout=10,
                    ).json()
                    status = result["status"]
                    if status == "completed":
                        answer = result["response"]
                        st.markdown(answer)
                        st.session_state.messages.append(
                            {"role": "assistant", "content": answer}
                        )
                        break
                    elif status == "failed":
                        err = result.get("error", "Unknown error")
                        st.error(f"Generation failed: {err}")
                        break
                    time.sleep(1)

            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
