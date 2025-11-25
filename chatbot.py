import streamlit as st
import requests
from datetime import datetime

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Health Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------
# REMOVE STREAMLIT TOP FROST HEADER COMPLETELY
# ---------------------------------------------------
st.markdown("""
<style>
/* Remove Streamlit top header / frost / padding */
header, [data-testid="stHeader"] {display: none !important;}
.css-18e3th9 {padding-top: 0 !important;}
.block-container {padding-top: 0 !important; margin-top: 0 !important;}
</style>
""", unsafe_allow_html=True)

# Remove sidebar default nav
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none !important;}
[data-testid="stSidebar"] ul {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# GLOBAL STYLES (CLEAN + FIXED)
# ---------------------------------------------------
STYLES = """
    <style>

    .stApp {
        background: linear-gradient(-45deg, #3b82f6, #1e3a8a, #0f1a3a, #000814);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: rgba(15, 26, 58, 0.9);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(16, 185, 129, 0.3);
    }

    .sidebar-title {
        color: white;
        font-size: 1.4rem;
        font-weight: 700;
        text-align: center;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #10b981;
        margin-bottom: 1rem;
    }

    .no-history {
        color: rgba(255, 255, 255, 0.6);
        text-align: center;
        padding: 2rem 1rem;
        font-style: italic;
    }

    /* HOME BUTTON */
    .home-btn-container {
        position: absolute;
        top: 20px;
        right: 25px;
        z-index: 1000;
    }

    .home-btn {
        background: black;
        color: white;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        cursor: pointer;
    }

    /* HEADER */
    .chat-header {
        background: linear-gradient(135deg, rgba(16,185,129,0.3), rgba(5,150,105,0.3));
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(16,185,129,0.4);
        margin-bottom: 1.5rem;
        margin-top: 0;
    }

    .chat-title {
        font-size: 2.4rem;
        font-weight: 900;
        color: white;
        margin: 0;
    }

    .chat-subtitle {
        color: rgba(255,255,255,0.9);
        margin-top: .5rem;
        font-size: 1.05rem;
    }

    /* CHAT AREA */
    .chat-container {
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        padding: 1rem;
        overflow-y: auto;
        max-height: 480px;
        min-height: 40px;
        margin-bottom: 1rem;
    }

    /* CHAT BUBBLES */
    .user-bubble {
        background: white;
        color: #000;
        padding: 1rem;
        border-radius: 18px 18px 4px 18px;
        float: right;
        clear: both;
        margin: 1rem 0;
        max-width: 75%;
    }

    .bot-bubble {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        color: white;
        padding: 1rem;
        border-radius: 18px 18px 18px 4px;
        float: left;
        clear: both;
        margin: 1rem 0;
        max-width: 75%;
        border: 1px solid rgba(16,185,129,0.3);
    }

    .bubble-label {
        font-size: .8rem;
        font-weight: 700;
        color: #10b981;
        margin-bottom: .3rem;
        display: block;
    }

    </style>
"""

# ---------------------------------------------------
# APPLY STYLES
# ---------------------------------------------------
st.markdown(STYLES, unsafe_allow_html=True)

# ---------------------------------------------------
# API CONFIG
# ---------------------------------------------------
API_CONFIG = {
    "key": "AIzaSyDZNcF91pZ1rmh4QOY2IZCL3T2cAyxBKDk",
    "model": "models/gemini-2.0-flash",
    "url": "https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={key}"
}

SYSTEM_INSTRUCTION = """
You are a medical AI assistant.
- Keep answers to the point and safe (3-5 sentences).
- Never diagnose, just advise.
- Tell user to see doctor for serious issues.
- If emergency symptoms → urge calling 108 immediately.
"""

def api_url():
    return API_CONFIG["url"].format(
        model=API_CONFIG["model"],
        key=API_CONFIG["key"]
    )

def ask_gemini(history):
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": SYSTEM_INSTRUCTION}]},
            *[
                {"role": m["role"], "parts": [{"text": m["content"]}]}
                for m in history
            ]
        ]
    }
    try:
        r = requests.post(api_url(), json=payload, timeout=10)
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "⚠ Error contacting AI."

def safe(text):
    return text.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")


# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>💬 Chat History</div>", unsafe_allow_html=True)

        if "chat_sessions" not in st.session_state:
            st.session_state.chat_sessions = []

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # New chat
        if st.button("➕ New Chat", use_container_width=True):
            if st.session_state.messages:
                st.session_state.chat_sessions.append({
                    "messages": st.session_state.messages.copy(),
                    "time": datetime.now().strftime("%H:%M")
                })
            st.session_state.messages = []
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Existing chats
        if st.session_state.chat_sessions:
            for i, s in enumerate(st.session_state.chat_sessions):
                preview = s["messages"][0]["content"][:35] + "..."
                if st.button(f"💬 {preview}\n🕒 {s['time']}", key=f"h{i}", use_container_width=True):
                    st.session_state.messages = s["messages"].copy()
                    st.rerun()
        else:
            st.markdown("<div class='no-history'>No chat history.</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.session_state.chat_sessions:
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.chat_sessions = []
                st.session_state.messages = []
                st.rerun()


# ---------------------------------------------------
# MAIN CHAT WINDOW RENDER
# ---------------------------------------------------
def render_header():
    st.markdown("""
        <div class='chat-header'>
            <h1 class='chat-title'>💬 AI Health Assistant</h1>
            <p class='chat-subtitle'>Ask your health questions safely</p>
        </div>
    """, unsafe_allow_html=True)

def render_chat():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        text = safe(msg["content"])
        if msg["role"] == "user":
            st.markdown(
                f"<div class='user-bubble'><span class='bubble-label'>You</span>{text}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div class='bot-bubble'><span class='bubble-label'>AI Assistant</span>{text}</div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------
# APP ENTRYPOINT
# ---------------------------------------------------
def main():

    # Init state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    render_sidebar()

    # Top-right Home button
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("index.py")


    render_header()
    render_chat()

    # Chat input
    user = st.chat_input("Ask something...")
    if user:
        st.session_state.messages.append({"role": "user", "content": user})
        reply = ask_gemini(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
