import re
import uuid
import streamlit as st
from agent import graph, as_text

st.set_page_config(page_title="AI SQL Analyst", page_icon="📊")
st.title("📊 AI SQL Analyst")
st.caption("Ask questions about the Olist Brazilian e-commerce database.")

# One conversation = one thread_id. Keep it in session state.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.history = []   # list of (role, text, chart_paths)

with st.sidebar:
    if st.button("New chat"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.history = []
        st.rerun()
    st.markdown("**Try asking:**")
    st.markdown("- Which 5 states have the most orders?\n"
                "- Show a line chart of monthly orders in 2017\n"
                "- Do late deliveries get worse review scores?")

# Replay earlier messages
for role, text, charts in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)
        for p in charts:
            st.image(p)

question = st.chat_input("Ask a question about the data...")

if question:
    st.session_state.history.append(("user", question, []))
    with st.chat_message("user"):
        st.markdown(question)

    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    chart_paths = []

    with st.chat_message("assistant"):
        placeholder = st.empty()
        text = ""
        status = st.status("Thinking...", expanded=False)

        for chunk, meta in graph.stream(
            {"messages": [("user", question)]}, config, stream_mode="messages"
        ):
            node = meta.get("langgraph_node")
            if node == "agent" and chunk.type == "AIMessageChunk":
                text += as_text(chunk.content)
                placeholder.markdown(text + "▌")
                if getattr(chunk, "tool_call_chunks", None):
                    status.update(label="Running a query...")
            elif node == "tools" and chunk.type == "tool":
                found = re.findall(r"charts/\S+\.png", str(chunk.content))
                chart_paths.extend(found)

        status.update(label="Done", state="complete")
        placeholder.markdown(text)
        for p in chart_paths:
            st.image(p)

    st.session_state.history.append(("assistant", text, chart_paths))