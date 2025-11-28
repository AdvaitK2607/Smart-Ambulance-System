import streamlit as st
import json
from datetime import datetime
import time
import os

# Page configuration
st.set_page_config(
    page_title="Technician Dashboard - Smart Ambulance",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------------------------------------
# AUTO REFRESH (every 5 seconds)
# -------------------------------------------------------
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000, key="auto_refresh_tech")


# File paths for shared data
QUEUE_FILE = "emergency_queue.json"
STATS_FILE = "system_stats.json"
FLEET_FILE = "fleet_status.json"

def load_queue():
    """Load queue from file"""
    try:
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        return []
    except:
        return []

def save_queue(queue):
    """Save queue to file without duplicates"""
    try:
        seen = set()
        unique_queue = []
        for entry in queue:
            entry_id = entry.get("id") or entry.get("name")
            if entry_id not in seen:
                unique_queue.append(entry)
                seen.add(entry_id)

        with open(QUEUE_FILE, 'w') as f:
            json.dump(unique_queue, f, indent=2)
    except Exception as e:
        st.error(f"Error saving queue: {e}")

def load_stats():
    """Load stats from file"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {
            'calls_today': 0,
            'dispatched': 0,
            'avg_response': 8.5,
            'success_rate': 95
        }
    except:
        return {
            'calls_today': 0,
            'dispatched': 0,
            'avg_response': 8.5,
            'success_rate': 95
        }

def save_stats(stats):
    """Save stats to file"""
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        st.error(f"Error saving stats: {e}")

def load_fleet_status():
    """Load fleet status from file"""
    try:
        if os.path.exists(FLEET_FILE):
            with open(FLEET_FILE, 'r') as f:
                return json.load(f)
        return {
            'total': 10,
            'available': 8,
            'en_route': 0,
            'maintenance': 2
        }
    except:
        return {
            'total': 10,
            'available': 8,
            'en_route': 0,
            'maintenance': 2
        }

def save_fleet_status(fleet):
    """Save fleet status to file"""
    try:
        with open(FLEET_FILE, 'w') as f:
            json.dump(fleet, f, indent=2)
    except Exception as e:
        st.error(f"Error saving fleet status: {e}")

# Custom CSS with GREEN theme matching patient portal
st.markdown("""
    <style>
    /* Hide sidebar and default elements */
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* BLUE → DARK NAVY DYNAMIC BACKGROUND */
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
    
    /* Main container */
    .main {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
    }
    
    /* Stat cards - WHITE with GREEN accents */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #10b981;
    }
    
    .stat-label {
        color: #374151;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Queue items - WHITE background with BLACK text */
    .queue-item {
        background: white;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        color: #000000;
        position: relative;
    }
    
    .queue-item:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Priority indicator boxes */
    .priority-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 8px;
        vertical-align: middle;
    }
    
    .priority-high {
        background-color: #ef4444;
        box-shadow: 0 0 10px rgba(239, 68, 68, 0.5);
    }
    
    .priority-medium {
        background-color: #f59e0b;
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
    }
    
    .priority-low {
        background-color: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    .queue-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #000000;
        margin-bottom: 0.5rem;
    }
    
    .queue-detail {
        color: #374151;
        font-size: 0.95rem;
        margin: 0.3rem 0;
    }
    
    .queue-detail strong {
        color: #000000;
    }
    
    /* Header styling - GREEN theme */
    .dashboard-header {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(5, 150, 105, 0.3));
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .dashboard-title {
        color: white;
        font-size: 2.5rem;
        font-weight: 900;
        margin: 0;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    }
    
    /* Section headers - GREEN */
    .section-header {
        color: #10b981;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 2px 10px rgba(16, 185, 129, 0.3);
    }
    
    .section-subheader {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Custom button styling - BLACK with WHITE text */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        background-color: #000000 !important;
        color: white !important;
        border: none !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        background-color: #1a1a1a !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Primary button variant */
    .stButton > button[kind="primary"] {
        background-color: #000000 !important;
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #1a1a1a !important;
    }
    
    /* Ambulance fleet cards - WHITE */
    .fleet-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .fleet-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }
    
    /* Info box - WHITE */
    .info-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin: 1rem 0;
    }
    
    .info-box p {
        color: #10b981;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0;
        text-align: center;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.5), transparent);
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Check if user is logged in as technician
if 'user_type' not in st.session_state or st.session_state.user_type != "technician":
    st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem;'>
            <h2 style='color: white;'>⚠️ Access Restricted</h2>
            <p style='color: rgba(255,255,255,0.7); font-size: 1.2rem;'>Please login as a technician first</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🏠 Go to Home", type="primary"):
        st.switch_page("index.py")
    st.stop()

# Load data from files - Always load queue fresh (not cached in session state)
# Queue should always reflect the latest file contents
current_queue = load_queue()
stats_from_file = load_stats()
fleet_from_file = load_fleet_status()

# Stats and fleet can be cached in session state for performance
if 'stats_data' not in st.session_state:
    st.session_state.stats_data = stats_from_file
else:
    st.session_state.stats_data = load_stats()

if 'fleet_status' not in st.session_state:
    st.session_state.fleet_status = fleet_from_file
else:
    st.session_state.fleet_status = load_fleet_status()

# Header - GREEN theme
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("""
        <div class='dashboard-header'>
            <h1 class='dashboard-title'>🚑 Technician Dashboard</h1>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="home_btn", type="primary"):
        st.session_state.user_type = None
        st.session_state.logged_in = False
        st.switch_page("index.py")

# Stats section - WHITE cards with GREEN values
st.markdown("<h3 class='section-header'>📊 Today's Statistics</h3>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='stat-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>📞</div>
            <div class='stat-value'>{st.session_state.stats_data['calls_today']}</div>
            <div class='stat-label'>Calls Today</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='stat-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🚑</div>
            <div class='stat-value'>{st.session_state.stats_data['dispatched']}</div>
            <div class='stat-label'>Dispatched</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='stat-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>⏱️</div>
            <div class='stat-value'>{st.session_state.stats_data['avg_response']:.1f}m</div>
            <div class='stat-label'>Avg. Response</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='stat-card'>
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>💓</div>
            <div class='stat-value'>{st.session_state.stats_data['success_rate']}%</div>
            <div class='stat-label'>Success Rate</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Always use fresh queue data from file (not session state)
# Display queue
if len(current_queue) == 0:
    st.markdown("""
        <div class='info-box'>
            <p>✅ No pending emergency requests. All clear!</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # Sort by priority and severity
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    sorted_queue = sorted(current_queue, 
                         key=lambda x: (priority_order[x['priority']], -x['severity_score']))
    
    for idx, patient in enumerate(sorted_queue):
        priority_class = f"priority-{patient['priority'].lower()}"
        
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                    <div class='queue-item'>
                        <div class='queue-header'>
                            <span class='priority-indicator {priority_class}'></span>
                            #{idx + 1} - {patient['name']} ({patient['age']} years old)
                        </div>
                        <div class='queue-detail'><strong>Condition:</strong> {patient['condition']}</div>
                        <div class='queue-detail'><strong>Symptoms:</strong> {patient['symptoms']}</div>
                        <div class='queue-detail'><strong>Location:</strong> {patient['location']}</div>
                        <div class='queue-detail'>
                            <strong>Priority:</strong> {patient['priority']} | 
                            <strong>Severity Score:</strong> {patient['severity_score']} | 
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # Check if ambulances are available
                if st.session_state.fleet_status['available'] > 0:
                    if st.button(f"🚑 Dispatch", key=f"dispatch_{patient['id']}", type="primary", use_container_width=True):
                        st.success(f"✅ Ambulance dispatched to {patient['name']}!")
                        st.balloons()
                        
                        # Update stats
                        st.session_state.stats_data['dispatched'] += 1
                        save_stats(st.session_state.stats_data)
                        
                        # Update fleet status
                        st.session_state.fleet_status['available'] -= 1
                        st.session_state.fleet_status['en_route'] += 1
                        save_fleet_status(st.session_state.fleet_status)
                        
                        # Remove from queue - reload fresh queue, remove the dispatched one, and save
                        updated_queue = load_queue()
                        updated_queue = [p for p in updated_queue if p['id'] != patient['id']]
                        save_queue(updated_queue)
                        st.rerun()
                else:
                    st.button(f"⚠️ No Ambulances", key=f"no_amb_{patient['id']}", disabled=True, use_container_width=True)

# Ambulance availability section - WHITE cards
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 class='section-header'>🚑 Ambulance Fleet Status</h3>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class='fleet-card'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🚑</div>
            <div style='font-size: 2.5rem; font-weight: 700; color: #10b981;'>{st.session_state.fleet_status['available']}</div>
            <div style='color: #374151; font-weight: 600; margin-top: 0.5rem;'>Available</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='fleet-card'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🚑</div>
            <div style='font-size: 2.5rem; font-weight: 700; color: #f59e0b;'>{st.session_state.fleet_status['en_route']}</div>
            <div style='color: #374151; font-weight: 600; margin-top: 0.5rem;'>En Route</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='fleet-card'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🚑</div>
            <div style='font-size: 2.5rem; font-weight: 700; color: #ef4444;'>{st.session_state.fleet_status['maintenance']}</div>
            <div style='color: #374151; font-weight: 600; margin-top: 0.5rem;'>Maintenance</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class='fleet-card'>
            <div style='font-size: 2.5rem; margin-bottom: 0.5rem;'>🚑</div>
            <div style='font-size: 2.5rem; font-weight: 700; color: #10b981;'>{st.session_state.fleet_status['total']}</div>
            <div style='color: #374151; font-weight: 600; margin-top: 0.5rem;'>Total Fleet</div>
        </div>
    """, unsafe_allow_html=True)

# Initialize fleet button state
if 'fleet_action_taken' not in st.session_state:
    st.session_state.fleet_action_taken = False

# Fleet management buttons
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Reset Fleet Status", key="reset_fleet_unique", use_container_width=True):
        st.session_state.fleet_status = {
            'total': 10,
            'available': 8,
            'en_route': 0,
            'maintenance': 2
        }
        save_fleet_status(st.session_state.fleet_status)
        st.session_state.fleet_action_taken = True

with col2:
    if st.button("✅ Complete En Route Mission", key="complete_mission_unique", use_container_width=True):
        if st.session_state.fleet_status['en_route'] > 0:
            st.session_state.fleet_status['en_route'] -= 1
            st.session_state.fleet_status['available'] += 1
            save_fleet_status(st.session_state.fleet_status)
            st.session_state.fleet_action_taken = True

with col3:
    if st.button("🔧 Send to Maintenance", key="send_maintenance_unique", use_container_width=True):
        if st.session_state.fleet_status['available'] > 0:
            st.session_state.fleet_status['available'] -= 1
            st.session_state.fleet_status['maintenance'] += 1
            save_fleet_status(st.session_state.fleet_status)
            st.session_state.fleet_action_taken = True

# Reset fleet action flag for next iteration
if st.session_state.fleet_action_taken:
    st.session_state.fleet_action_taken = False

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align: center; color: rgba(255,255,255,0.9); padding: 1rem 0;'>
        <p style='color: #10b981; font-weight: 700; font-size: 1.1rem;'>Emergency Response System</p>
        <p style='font-size: 0.95rem;'>Last updated: {datetime.now().strftime("%H:%M:%S")}</p>
        <p style='font-size: 0.9rem; margin-top: 0.5rem;'>
            Fleet Status: {st.session_state.fleet_status['available']} Available | 
            {st.session_state.fleet_status['en_route']} En Route | 
            {st.session_state.fleet_status['maintenance']} Maintenance
        </p>
    </div>
""", unsafe_allow_html=True)