import streamlit as st

st.set_page_config(
    page_title="Real-Time Routing - Coming Soon",
    page_icon="🗺️",
    layout="wide"
)

# ---- STYLING ----
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(-45deg, #1e3a8a, #2563eb, #3b82f6, #60a5fa);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .main {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 3rem;
    }

    .coming-soon-container {
        text-align: center;
        padding: 4rem 2rem;
    }

    .icon-large {
        font-size: 8rem;
        margin-bottom: 2rem;
        animation: bounce 2s ease-in-out infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-20px); }
    }

    .title {
        font-size: 3rem;
        font-weight: 900;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }

    .subtitle {
        font-size: 1.4rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 3rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.8;
    }

    .feature-box {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        text-align: left;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }

    .feature-box:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateY(-5px);
    }

    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }

    .feature-desc {
        color: rgba(255, 255, 255, 0.85);
        font-size: 1rem;
    }

    /* Black Buttons */
    .stButton > button {
        width: 220px !important;
        margin: 2rem auto !important;
        display: block !important;
        background: #000 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: all 0.3s ease;
        border: none !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        background: #111 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255,255,255,0.25);
    }
    </style>
""", unsafe_allow_html=True)

# ---- MAIN CONTENT ----
st.markdown("""
    <div class='coming-soon-container'>
        <div class='icon-large'>🗺️</div>
        <h1 class='title'>Real-Time Ambulance Routing</h1>
        <p class='subtitle'>
            Advanced GPS tracking, dynamic traffic-aware navigation, and AI-based route optimization for emergency vehicles.
        </p>
    </div>
""", unsafe_allow_html=True)

# ---- FEATURES SECTION ----
st.markdown("### 🚀 Planned Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class='feature-box'>
            <h3 class='feature-title'>📍 Live GPS Tracking</h3>
            <p class='feature-desc'>Real-time monitoring of all ambulances across the network for efficient dispatch.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='feature-box'>
            <h3 class='feature-title'>🛣️ Optimal Route Calculation</h3>
            <p class='feature-desc'>AI-powered route planning that adapts to live road and traffic conditions.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='feature-box'>
            <h3 class='feature-title'>🗺️ Interactive Map View</h3>
            <p class='feature-desc'>Visual dashboard showing all active ambulances, patients, and hospital destinations.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class='feature-box'>
            <h3 class='feature-title'>🚦 Dynamic Traffic Integration</h3>
            <p class='feature-desc'>Live traffic updates help ambulances reach patients faster and avoid congested areas.</p>
        </div>
    """, unsafe_allow_html=True)

# ---- BACK BUTTON ----
st.markdown("<br>", unsafe_allow_html=True)
if st.button("⬅️ Back to Home", key="back_btn", use_container_width=False):
    st.switch_page("index.py")

# ---- FOOTER ----
st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.8); margin-top: 3rem;'>
        <p>Integrating Google Maps API, OpenStreetMap, and predictive route intelligence.</p>
        <p style='margin-top: 1rem; font-size: 0.9rem;'>This innovation aims to reduce emergency response times by 30–40%.</p>
    </div>
""", unsafe_allow_html=True)
