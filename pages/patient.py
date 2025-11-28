import streamlit as st
import time

# Page configuration
st.set_page_config(
    page_title="Smart Hospital System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---- MODERN STYLING ----
st.markdown("""
    <style>
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    
    /* Modern animated gradient background - Blue → Dark Navy */
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
    
    /* Glass morphism container */
    .main {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 2rem;
    }
    
    /* Hero section */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 3rem 1rem;
        animation: fadeInDown 1s ease-out;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5),
                     0 0 60px rgba(255, 255, 255, 0.3);
        margin-bottom: 0.5rem;
        animation: pulse 3s ease-in-out infinite;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: rgba(255, 255, 255, 0.95);
        font-weight: 300;
        max-width: 900px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Stats container */
    .stats-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0 3rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stat-box {
        text-align: center;
        padding: 1rem;
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Module cards */
    .module-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
        height: 100%;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .module-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .module-card:hover::before {
        left: 100%;
    }
    
    .module-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        border-color: rgba(37, 99, 235, 0.5);
    }
    
    .module-card.coming-soon {
        opacity: 0.75;
        background: rgba(255, 255, 255, 0.85);
    }
    
    .module-card.coming-soon:hover {
        transform: translateY(-5px) scale(1.01);
    }
    
    .module-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    .module-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #2b6cb0;
        margin-bottom: 0.8rem;
    }
    
    .module-description {
        color: #555;
        font-size: 1rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }
    
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .badge-active {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
    }
    
    .badge-beta {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
    }
    
    .badge-coming {
        background: linear-gradient(135deg, #6b7280, #4b5563);
        color: white;
    }
    
    /* Custom buttons */
    .stButton > button {
        width: 100%;
        height: 50px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
    }
    
    /* Section headers */
    .section-header {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        margin: 2.5rem 0 1.5rem 0;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.4);
    }
    
    .section-subheader {
        text-align: center;
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 2rem;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
        margin: 3rem 0;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 3rem;
    }
    
    .custom-footer p {
        margin: 0.5rem 0;
        font-size: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---- SESSION STATE ----
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

st.markdown("""
    <style>
    .hero-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 4rem 1rem 3rem 1rem;
        color: white;
        text-align: center;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 15px rgba(255,255,255,0.5),
                     0 0 40px rgba(37,99,235,0.6);
        margin-bottom: 0.8rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: rgba(255,255,255,0.9);
        max-width: 850px;
        text-align: center;
        margin: 0 auto;
        line-height: 1.6;
        word-spacing: 4px;
        letter-spacing: 0.3px;
    }
    </style>

    <div class='hero-container'>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>🏥</div>
        <h1 class='hero-title'>SMART HOSPITAL SYSTEM</h1>
        <p class='hero-subtitle'>
            Unified Digital Healthcare Platform • AI-Powered Emergency Response • Comprehensive Patient Care
        </p>
    </div>
""", unsafe_allow_html=True)


# ---- LIVE STATS SECTION ----
st.markdown("""
    <div class='stats-container'>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.5rem;'>
            <div class='stat-box'>
                <span class='stat-number'>24/7</span>
                <span class='stat-label'>Active</span>
            </div>
            <div class='stat-box'>
                <span class='stat-number'>< 8min</span>
                <span class='stat-label'>Response Time</span>
            </div>
            <div class='stat-box'>
                <span class='stat-number'>AI</span>
                <span class='stat-label'>Powered</span>
            </div>
            <div class='stat-box'>
                <span class='stat-number'>100%</span>
                <span class='stat-label'>Coverage</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---- ACTIVE MODULES SECTION ----
st.markdown("""
    <style>
    .section-header {
        text-align: center;
        font-size: 2.7rem;
        font-weight: 900;
        color: white;
        text-shadow: 0 0 25px rgba(255, 255, 255, 0.4);
        margin-bottom: 0.5rem;
    }

    .section-subheader {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 1.3rem;
        margin-bottom: 3rem;
    }

    .module-card {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 2.5rem 1.8rem;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.15);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
    }

    .module-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        border-color: rgba(255,255,255,0.3);
    }

    .module-icon {
        font-size: 4.5rem;
        margin-bottom: 1.5rem;
        animation: floatIcon 3s ease-in-out infinite;
    }

    @keyframes floatIcon {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .module-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.8rem;
    }

    .module-description {
        font-size: 1.15rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 1.2rem;
        line-height: 1.6;
    }

    .badge {
        display: inline-block;
        font-weight: 700;
        font-size: 1rem;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        letter-spacing: 0.5px;
    }

    .badge-active {
        background: rgba(46, 204, 113, 0.2);
        color: #2ecc71;
        border: 1px solid rgba(46,204,113,0.5);
    }

    .badge-beta {
        background: rgba(241,196,15,0.2);
        color: #f1c40f;
        border: 1px solid rgba(241,196,15,0.5);
    }

    /* Buttons */
    .stButton > button {
        width: 100% !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        height: 60px !important;
        border-radius: 12px !important;
        color: white !important;
        background: #000 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: #111 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255,255,255,0.25);
    }
    </style>
""", unsafe_allow_html=True)

# ---- TITLE SECTION ----
st.markdown("""
    <h2 class='section-header'>🚀 Active Services</h2>
    <p class='section-subheader'>Fully operational modules - Click to access</p>
""", unsafe_allow_html=True)

# ---- MODULE CARDS ----
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class='module-card'>
            <div class='module-icon'>🚑</div>
            <h3 class='module-title'>Patient Portal</h3>
            <p class='module-description'>
                Request an emergency ambulance with our AI-powered priority dispatch system.
            </p>
            <span class='badge badge-active'>● ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚨 Access Emergency", key="emergency_btn", type="primary"):
        with st.spinner("Connecting to emergency services..."):
            time.sleep(0.4)
        st.session_state.user_type = "patient"
        st.session_state.logged_in = True
        st.switch_page("pages/patient.py")

with col2:
    st.markdown("""
        <div class='module-card'>
            <div class='module-icon'>👨‍⚕️</div>
            <h3 class='module-title'>Technician Portal</h3>
            <p class='module-description'>
                Manage queues, dispatch ambulances, and coordinate emergency response operations.
            </p>
            <span class='badge badge-active'>● ACTIVE</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔐 Technician Login", key="tech_btn", type="primary"):
        with st.spinner("Authenticating..."):
            time.sleep(0.4)
        st.session_state.user_type = "technician"
        st.session_state.logged_in = True
        st.switch_page("pages/technician.py")

with col3:
    st.markdown("""
        <div class='module-card'>
            <div class='module-icon'>💬</div>
            <h3 class='module-title'>AI Health Assistant</h3>
            <p class='module-description'>
                Chat with our AI assistant for health queries, symptom checks, and hospital navigation.
            </p>
            <span class='badge badge-beta'>BETA</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("💬 Open Chatbot", key="chatbot_btn", type="primary"):
        with st.spinner("Launching AI assistant..."):
            time.sleep(0.4)
        st.switch_page("pages/chatbot.py")

# ---- UPCOMING FEATURE SECTION: REAL-TIME ROUTING ----
import streamlit as st

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h2 class='section-header'>🚧 Real-Time Ambulance Routing System (Coming Soon)</h2>", unsafe_allow_html=True)

# ---- STYLING ----
st.markdown("""
    <style>
    .routing-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    .routing-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        border-radius: 20px;
        padding: 2.5rem;
        width: 400px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease-in-out;
        animation: fadeInUp 1s ease-out;
    }

    .routing-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        border-color: rgba(255,255,255,0.3);
    }

    .routing-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: floatIcon 3s ease-in-out infinite;
    }

    @keyframes floatIcon {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    .routing-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.8rem;
    }

    .routing-description {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }

    .coming-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: white;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        border-radius: 25px;
        letter-spacing: 1px;
        font-size: 0.9rem;
    }

    /* Black Button Styling - Same width as card */
    .stButton > button {
        display: block !important;
        width: 400px !important;
        margin: 1.5rem auto 0 auto !important;
        text-align: center !important;
        background: #111 !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.8rem 0 !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: all 0.3s ease !important;
        border: none !important;
        letter-spacing: 0.5px;
    }

    .stButton > button:hover {
        background: #000 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255,255,255,0.3);
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)

# ---- CARD CONTENT ----
st.markdown("""
    <div class='routing-container'>
        <div class='routing-card'>
            <div class='routing-icon'>🗺️</div>
            <div class='routing-title'>Ambulance Routing</div>
            <div class='routing-description'>
                Use efficient, real-time routes for emergency vehicles to reach hospitals faster.
            </div>
            <span class='coming-badge'>COMING SOON</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---- MATCHING BUTTON (same width as tile) ----
if st.button("View Details", use_container_width=False):
    st.switch_page("pages/routing.py")

# ---- FOOTER ----
st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.8); margin-top: 3rem;'>
        <p>Integrating Google Maps API, OpenStreetMap, and AI-driven route prediction</p>
    </div>
""", unsafe_allow_html=True)


# ---- FOOTER ----
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div class='custom-footer'>
        <p><strong>Smart Hospital System © 2025</strong></p>
        <p>Powered by Advanced AI • Digital Healthcare Innovation</p>
        <p style='font-size: 0.9rem; margin-top: 1rem; opacity: 0.8;'>
            Developed by:- Aaryan Tamhane, Advait Kulkarni, Soham Shrawankar
        </p>
    </div>

""", unsafe_allow_html=True)
