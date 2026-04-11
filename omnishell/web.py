"""
OmniShell Web UI — Enhanced Streamlit-based dashboard.
"""

import os
import sys
import streamlit as st
from dotenv import load_dotenv, find_dotenv

# --- PAGE CONFIG (must be first Streamlit call) ---
st.set_page_config(
    page_title="OmniShell AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- LOAD ENV ---
load_dotenv(find_dotenv())

# Bridge Streamlit secrets to environment
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# Now safe to import omnishell modules
from omnishell import __version__
from omnishell.core import detect_system_info
from omnishell.llm import get_llm, invoke_llm, PROVIDERS, DEFAULT_MODELS
from omnishell.prompts import (
    get_system_prompt,
    get_explain_prompt,
    EXPLAIN_SYSTEM,
)
from omnishell.safety import is_blocked, sanitize_command
from omnishell.history import save_command, get_history, clear_history, get_history_stats
from langchain_core.messages import SystemMessage, HumanMessage

# --- DETECT SYSTEM ---
distro_name, pkg_manager = detect_system_info()

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Dark glassmorphism styling */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        backdrop-filter: blur(10px) !important;
        padding: 1rem !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Input area */
    .stChatInput > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    
    /* Code blocks */
    code {
        color: #a5f3fc !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        background: rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: #818cf8;
    }
    
    /* Headers */
    h1, h2, h3 {
        background: linear-gradient(90deg, #818cf8, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Stat label fix */
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.7) !important;
    }
</style>
""", unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    # Provider selection
    provider = st.selectbox(
        "LLM Provider",
        PROVIDERS,
        index=PROVIDERS.index(os.getenv("OMNISHELL_PROVIDER", "groq")),
        help="Choose your AI backend",
    )

    # Model override
    default_model = DEFAULT_MODELS.get(provider, "")
    model = st.text_input("Model", value=default_model, help="Override the default model")

    # Mode selection
    mode = st.selectbox(
        "Mode",
        ["pro", "newbie", "god"],
        help="Safety level for generated commands",
    )

    mode_descriptions = {
        "pro": "🟢 **Pro** — Commands only, safe mode enabled",
        "newbie": "🟡 **Newbie** — Extra explanations, sudo warnings",
        "god": "🔴 **God** — No restrictions (use carefully!)",
    }
    st.markdown(mode_descriptions[mode])

    st.divider()

    # System info panel
    st.markdown("### 🖥️ System Info")
    st.markdown(f"**Distro:** {distro_name}")
    st.markdown(f"**Package Manager:** `{pkg_manager}`")
    st.markdown(f"**OmniShell:** v{__version__}")

    st.divider()

    # History stats
    st.markdown("### 📊 Statistics")
    stats = get_history_stats()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total", stats["total"])
    col2.metric("✅", stats["success"])
    col3.metric("❌", stats["failed"])

    st.divider()

    # History section
    st.markdown("### 📜 Recent History")
    history_records = get_history(limit=10)
    if history_records:
        for r in history_records:
            icon = "✅" if r["status"] == "success" else "❌"
            with st.expander(f"{icon} {r['query'][:35]}"):
                st.code(r["command"], language="bash")
                st.caption(r["timestamp"][:19].replace("T", " "))
    else:
        st.caption("No history yet. Start by asking a question!")

    if st.button("🗑️ Clear History", use_container_width=True):
        clear_history()
        st.rerun()


# --- MAIN AREA ---
st.markdown("# 🧠 OmniShell")
st.markdown("*Self-healing AI terminal assistant — describe what you need in plain English.*")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Describe a task (e.g., 'Show disk usage', 'Install docker')"):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Initialize LLM
    try:
        llm = get_llm(provider=provider, model=model if model else None)
    except ValueError as e:
        st.error(f"❌ {e}")
        st.stop()

    with st.chat_message("assistant"):
        with st.spinner("🧠 Thinking..."):
            try:
                # Generate system prompt
                system_prompt = get_system_prompt(distro_name, pkg_manager, mode)
                msgs = [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]
                
                # Generate command
                command = invoke_llm(llm, msgs)
                command = sanitize_command(command)

                # Safety check
                if "SAFE_MODE_ERROR" in command:
                    response_text = "🛡️ **Safe Mode Activated**\n\nThis request was blocked for safety reasons."
                elif is_blocked(command):
                    response_text = f"🛡️ **Security Block**\n\nBlocked dangerous command: `{command}`"
                else:
                    # Build response
                    response_text = f"**💻 Suggested Command:**\n```bash\n{command}\n```\n"

                    # Get explanation
                    explain_msgs = [
                        SystemMessage(content=EXPLAIN_SYSTEM),
                        HumanMessage(content=get_explain_prompt(command)),
                    ]
                    explanation = invoke_llm(llm, explain_msgs)
                    response_text += f"\n**ℹ️ Explanation:**\n{explanation}"

                    # Save to history
                    save_command(prompt, command, "suggested", "", mode, provider)

                    # Copy hint
                    response_text += f"\n\n---\n*📋 Copy the command above and paste it in your terminal.*"

            except Exception as e:
                response_text = f"❌ **Error:** {str(e)}"

        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
