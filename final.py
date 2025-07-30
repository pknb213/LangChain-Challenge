import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Load environment variables
load_dotenv()

# === Session State Initialization ===
if 'assistant_id' not in st.session_state:
    st.session_state.assistant_id = None
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
if 'run_id' not in st.session_state:
    st.session_state.run_id = None

# === Sidebar: API Key Input ===
st.sidebar.title("🔑 OpenAI API Key")
api_key = st.sidebar.text_input(
    label="Enter your OpenAI API Key:",
    type="password",
    value=os.getenv("OPENAI_API_KEY", ""),
)
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

# Instantiate OpenAI client with v2 Assistants header
client = None
if api_key:
    try:
        client = OpenAI(
            api_key=api_key,
            default_headers={"OpenAI-Beta": "assistants=v1"}
        )
    except OpenAIError as e:
        st.sidebar.error(f"Failed to initialize OpenAI client: {e}")

# === Create Assistant ===
if client and st.session_state.assistant_id is None:
    try:
        assistant = client.beta.assistants.create(
            name="research-agent",
            model='gpt-3.5.turbo',

        )
        st.session_state.assistant_id = assistant.id
        st.sidebar.success(f"Assistant created: {assistant.id}")
    except OpenAIError as e:
        st.sidebar.error(f"Error creating assistant: {e}")

# === Create Thread ===
if client and st.session_state.assistant_id and st.session_state.thread_id is None:
    try:
        thread = client.beta.assistants(
            st.session_state.assistant_id
        ).threads.create(title="Research Session")
        st.session_state.thread_id = thread.id
        st.sidebar.success(f"Thread created: {thread.id}")
    except OpenAIError as e:
        st.sidebar.error(f"Error creating thread: {e}")

# === Main UI ===
st.title("🔬 Research AI Agent")
user_prompt = st.text_area("Ask your research question:")

if st.button("Run Research") and user_prompt:
    if client and st.session_state.assistant_id and st.session_state.thread_id:
        try:
            run = client.beta.assistants(
                st.session_state.assistant_id
            ).threads(
                st.session_state.thread_id
            ).runs.create(
                messages=[{"role": "user", "content": user_prompt}]
            )
            st.session_state.run_id = run.id

            # Display assistant response
            for choice in run.choices:
                st.markdown(f"**Assistant:** {choice.message.content}")
        except OpenAIError as e:
            st.error(f"Error during run: {e}")
    else:
        st.error("Assistant or Thread not initialized.")
