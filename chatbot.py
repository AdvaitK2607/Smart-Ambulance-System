import streamlit as st
import requests
import json

# --------------------------------------------------
# 🎨 ADD GRADIENT BACKGROUND (BLUE → DARK NAVY)
# --------------------------------------------------
st.markdown("""
    <style>
    /* 🔵 Gradient Background */
    .stApp {
        background: linear-gradient(-45deg, 
            #3b82f6,   /* Blue */
            #1e3a8a,   /* Navy */
            #0f1a3a,   /* Deep Navy */
            #000814    /* Dark Navy */
        );
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
""", unsafe_allow_html=True)


# ------------------------------
# 🔐 GEMINI API SETTINGS
# ------------------------------
API_KEY = "AIzaSyDZNcF91pZ1rmh4QOY2IZCL3T2cAyxBKDk"
MODEL = "models/gemini-2.0-flash"

API_URL = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}"


# ------------------------------
# 💾 SYSTEM INSTRUCTION (not shown to the user)
# ------------------------------
SYSTEM_INSTRUCTION = (
    "You are a certified medical AI assistant. Follow these rules:\n"
    "- Provide medically safe, accurate explanations.\n"
    "- Explain symptoms, risks, causes, red flags, and emergencies.\n"
    "- Never give a confirmed diagnosis.\n"
    "- Never prescribe medication.\n"
    "- Encourage consulting a doctor.\n"
)


# ------------------------------
# 🤖 SEND MESSAGE TO GEMINI (REST API)
# ------------------------------
def ask_gemini(messages):
    headers = {"Content-Type": "application/json"}

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": SYSTEM_INSTRUCTION}]
            },
            *[
                {
                    "role": m["role"],
                    "parts": [{"text": m["content"]}]
                }
                for m in messages
            ]
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()

    if "candidates" in data:
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except:
            return "⚠️ Parsing Error:\n" + json.dumps(data, indent=2)

    return "⚠️ API Error:\n" + json.dumps(data, indent=2)


# ------------------------------
# 💾 SESSION STATE
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ------------------------------
# 🌐 PAGE HEADING
# ------------------------------
st.markdown("<h1 style='text-align:center; color:white;'>💬 AI Health Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>Ask any medical question or describe your symptoms.</p>", unsafe_allow_html=True)


# ------------------------------
# 💬 DISPLAY CHAT HISTORY
# ------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.25); padding:12px;
                    border-radius:10px; margin:8px 0; color:white; white-space:pre-wrap;'>
            <b>You:</b><br>{msg["content"].replace("<", "&lt;").replace(">", "&gt;")}
        </div>
        """, unsafe_allow_html=True)

    elif msg["role"] == "assistant":
        st.markdown(f"""
        <div style='background:rgba(0,0,0,0.45); padding:12px;
                    border-radius:10px; margin:8px 0; color:white; white-space:pre-wrap;'>
            <b>AI Assistant:</b><br>{msg["content"].replace("<", "&lt;").replace(">", "&gt;")}
        </div>
        """, unsafe_allow_html=True)


# ------------------------------
# 📝 USER INPUT BOX
# ------------------------------
user_input = st.chat_input("Describe your symptoms or ask a medical question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    reply = ask_gemini(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

