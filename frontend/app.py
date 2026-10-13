"""
Nexoramind Intelligent Chatbot - Streamlit Web Interface.
Interactive studio supporting multi-session memory, automatic intent routing,
and tool execution traces (Calculator, Weather, Dictionary, Wikipedia).
"""

from datetime import datetime
import json
import os
from pathlib import Path
import sys
import time

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.bot import get_chatbot_engine
from core.memory import get_memory_manager
from core.tools import get_tool_registry
from frontend.styles import CUSTOM_CSS

# Page Configuration
st.set_page_config(
    page_title="Nexoramind - Intelligent Chatbot with Memory",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

bot = get_chatbot_engine()
memory = get_memory_manager()
tools = get_tool_registry().list_tools()

# Session State
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = "default_session"

# Ensure active session exists in memory
current_session = memory.get_or_create_session(st.session_state.active_session_id)


# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown("### 🤖 Nexoramind Chatbot")
    st.caption("Task 05: Memory & Tool Use")
    st.divider()

    st.subheader("💬 Sessions Manager")

    # Start new session
    if st.button("➕ Start New Conversation", use_container_width=True, type="primary"):
        new_sess = memory.create_session()
        st.session_state.active_session_id = new_sess.session_id
        st.rerun()

    # Session Selector
    sessions = memory.list_sessions()
    session_options = {s["session_id"]: f"{s['title']} ({s['active_messages_count']} msgs)" for s in sessions}

    selected_sid = st.selectbox(
        "Select Active Session",
        options=list(session_options.keys()),
        format_func=lambda x: session_options.get(x, x),
        index=list(session_options.keys()).index(st.session_state.active_session_id) if st.session_state.active_session_id in session_options else 0,
    )

    if selected_sid != st.session_state.active_session_id:
        st.session_state.active_session_id = selected_sid
        st.rerun()

    # Session Metadata Card
    active_s = memory.get_session(st.session_state.active_session_id)
    if active_s:
        st.caption(f"**Session ID:** `{active_s.session_id}`")
        st.caption(f"**Sliding Window:** `{len(active_s.messages)} / 20 messages`")
        if active_s.summary:
            with st.expander("📝 Archived Summary", expanded=False):
                st.caption(active_s.summary)

        # Delete session button
        if st.button("🗑️ Delete Session", use_container_width=True):
            memory.delete_session(active_s.session_id)
            remaining = memory.list_sessions()
            st.session_state.active_session_id = remaining[0]["session_id"] if remaining else "default_session"
            st.rerun()

    st.divider()
    st.subheader("🛠️ Integrated Tools")
    for t in tools:
        st.markdown(f"**{t['name'].capitalize()}**")
        st.caption(t["description"])

    st.divider()
    st.caption("Backend: **FastAPI (In-Process / http://127.0.0.1:8000)**")


# ==================== MAIN BANNER ====================
st.markdown(
    """
    <div class="hero-banner">
        <span class="hero-badge">Nexoramind AI Internship</span>
        <span class="hero-badge">Conversational AI</span>
        <span class="hero-badge">Task 05</span>
        <h1 class="hero-title">Intelligent Chatbot with Memory & Tool Use</h1>
        <p class="hero-sub">
            Conversation history tracking (last 20 messages sliding window + auto-summary), 
            intent classification, and external tool orchestration (Calculator, Weather, Dictionary, Wikipedia).
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Quick Prompt Buttons
st.markdown("##### ⚡ Quick Test Queries")
q_cols = st.columns(5)
quick_queries = [
    ("🧮 15% of 230", "What is 15% of 230?"),
    ("🌤️ Weather Tokyo", "What is the current weather in Tokyo?"),
    ("📖 Define Resilient", "What is the meaning of resilient?"),
    ("🌐 Alan Turing", "Search wikipedia for Alan Turing"),
    ("💬 Intro Chat", "Hello! What are your capabilities?"),
]

triggered_query = None
for i, (label, query_text) in enumerate(quick_queries):
    with q_cols[i]:
        if st.button(label, use_container_width=True, key=f"quick_{i}"):
            triggered_query = query_text


# ==================== CHAT INTERFACE ====================
active_session = memory.get_session(st.session_state.active_session_id)
messages = active_session.messages if active_session else []

# Render message history
for msg in messages:
    with st.chat_message(msg.role):
        if msg.role == "assistant":
            meta = msg.metadata
            intent = meta.get("intent", "general")
            tool_used = meta.get("tool_used")

            # Pill for intent
            intent_class = f"intent-{intent.replace(' ', '-')}"
            st.markdown(f'<span class="intent-pill {intent_class}">{intent}</span>', unsafe_allow_html=True)

            # Tool trace card
            if tool_used:
                st.markdown(
                    f"""<div class="tool-trace-card">
                    🔧 <strong>Tool Invocation:</strong> <code>{tool_used}</code><br/>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown(msg.content)


# Chat Input
user_input = st.chat_input("Type your message, ask a math problem, weather, or definition...")
if triggered_query:
    user_input = triggered_query

if user_input:
    # 1. Display user query immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Process with Chatbot Engine
    with st.spinner("Processing intent, tool routing, and memory..."):
        t0 = time.perf_counter()
        res = bot.process_message(query=user_input, session_id=st.session_state.active_session_id)
        latency = (time.perf_counter() - t0) * 1000

    # 3. Display Assistant Response
    with st.chat_message("assistant"):
        intent = res["intent"]
        tool_used = res["tool_used"]

        intent_class = f"intent-{intent.replace(' ', '-')}"
        st.markdown(f'<span class="intent-pill {intent_class}">{intent} (Confidence: {res["confidence"]:.2f})</span>', unsafe_allow_html=True)

        if tool_used:
            st.markdown(
                f"""<div class="tool-trace-card">
                🔧 <strong>Tool Invocation:</strong> <code>{tool_used}</code> | Latency: <code>{latency:.1f}ms</code>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown(res["response"])

    st.rerun()
