import streamlit as st
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Patient Portal - Smart Ambulance",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# File paths for shared data
QUEUE_FILE = "emergency_queue.json"
STATS_FILE = "system_stats.json"

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
    """Save queue to file with deduplication"""
    try:
        seen = set()
        unique_queue = []
        for entry in queue:
            entry_id = entry.get("id")
            if entry_id and entry_id not in seen:
                unique_queue.append(entry)
                seen.add(entry_id)
        
        with open(QUEUE_FILE, 'w') as f:
            json.dump(unique_queue, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving queue: {e}")
        return False

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

# Custom CSS with dark gradient background - GREEN THEME
st.markdown("""
    <style>
    /* Hide sidebar and default elements */
    [data-testid="stSidebar"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ✅ BLUE → DARK NAVY DYNAMIC BACKGROUND */
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
    
    .main {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
    }
    
    /* Header styles - GREEN THEME */
    .dashboard-header {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(5, 150, 105, 0.3));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    .dashboard-title {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
    }
    
    /* White cards */
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    
    .info-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        text-align: center;
    }
    
    /* Priority indicators */
    .priority-indicator {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    
    .severity-high {
        background: #ef4444;
    }
    
    .severity-medium {
        background: #f59e0b;
    }
    
    .severity-low {
        background: #10b981;
    }
    
    /* Section headers */
    .section-header {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    /* Result boxes */
    .result-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .result-box h3 {
        color: #1e293b;
        margin-top: 0;
    }
    
    .result-box p {
        color: #475569;
        margin: 0.5rem 0;
    }
    
    /* Info messages */
    .info-message {
        background: rgba(96, 165, 250, 0.15);
        border-left: 4px solid #60a5fa;
        padding: 1rem;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.9);
        margin: 1rem 0;
    }
    
    .warning-message {
        background: rgba(251, 191, 36, 0.15);
        border-left: 4px solid #fbbf24;
        padding: 1rem;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.9);
        margin: 1rem 0;
    }
    
    .success-message {
        background: rgba(34, 197, 94, 0.15);
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.9);
        margin: 1rem 0;
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 1rem;
        border-radius: 8px;
        color: rgba(255, 255, 255, 0.9);
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_type' not in st.session_state or st.session_state.user_type != "patient":
    st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem;'>
            <h2 style='color: white;'>⚠️ Access Restricted</h2>
            <p style='color: rgba(255,255,255,0.7); font-size: 1.2rem;'>Please login as a patient first</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("🏠 Go to Home", type="primary"):
        st.switch_page("index.py")
    st.stop()

if 'request_step' not in st.session_state:
    st.session_state.request_step = 'home'
if 'questionnaire_answers' not in st.session_state:
    st.session_state.questionnaire_answers = {}
if 'patient_info' not in st.session_state:
    st.session_state.patient_info = {}
if 'request_submitted' not in st.session_state:
    st.session_state.request_submitted = False

# Questionnaire data
questionnaire = {
    'consciousness': {
        'question': 'Is the patient conscious?',
        'options': ['Fully conscious', 'Drowsy but responsive', 'Unconscious'],
        'weights': [0, 20, 40]
    },
    'breathing': {
        'question': 'Breathing status?',
        'options': ['Normal breathing', 'Difficulty breathing', 'Severe breathing difficulty', 'Not breathing'],
        'weights': [0, 20, 35, 50]
    },
    'chest_pain': {
        'question': 'Any chest pain?',
        'options': ['No chest pain', 'Mild discomfort', 'Moderate pain', 'Severe crushing pain'],
        'weights': [0, 10, 20, 35]
    },
    'bleeding': {
        'question': 'Any bleeding?',
        'options': ['No bleeding', 'Minor bleeding', 'Moderate bleeding', 'Severe/uncontrolled bleeding'],
        'weights': [0, 5, 15, 30]
    },
    'mobility': {
        'question': 'Can the patient move?',
        'options': ['Can move normally', 'Limited movement', 'Cannot move', 'Suspected spinal injury'],
        'weights': [0, 10, 20, 35]
    },
    'pain_level': {
        'question': 'Pain level (1-10)?',
        'options': ['1-3 (Mild)', '4-6 (Moderate)', '7-8 (Severe)', '9-10 (Extreme)'],
        'weights': [0, 10, 20, 25]
    }
}

def calculate_severity(answers):
    """Calculate severity score from questionnaire answers"""
    total_score = sum(answers.values())
    
    if total_score >= 80:
        return 'HIGH', total_score, 'Immediate ambulance dispatch - Life threatening'
    elif total_score >= 40:
        return 'MEDIUM', total_score, 'Ambulance dispatch within 15 minutes - Serious condition'
    else:
        return 'LOW', total_score, 'Ambulance dispatch when available - Non-critical'

def get_condition_from_answers(answers):
    """Determine likely condition based on answers"""
    conditions = []
    
    if 'chest_pain' in answers and answers['chest_pain'] >= 20:
        conditions.append('Suspected Heart Attack')
    if 'breathing' in answers and answers['breathing'] >= 20:
        conditions.append('Respiratory Distress')
    if 'consciousness' in answers and answers['consciousness'] >= 20:
        conditions.append('Altered Consciousness')
    if 'bleeding' in answers and answers['bleeding'] >= 15:
        conditions.append('Hemorrhage')
    if 'mobility' in answers and answers['mobility'] >= 20:
        conditions.append('Trauma/Injury')
    
    return ' | '.join(conditions) if conditions else 'General Medical Emergency'

# Header - GREEN THEME
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("""
        <div class='dashboard-header'>
            <h1 class='dashboard-title'>🤕 Patient Emergency Portal</h1>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="home_btn", use_container_width=True):
        st.session_state.user_type = None
        st.session_state.logged_in = False
        st.session_state.request_step = 'home'
        st.switch_page("index.py")

# Main content based on step
if st.session_state.request_step == 'home':
    # Home screen with emergency button
    st.markdown("<h3 class='section-header'>Welcome to Emergency Services</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class='info-card'>
                <h2 style='color: #10b981; margin-bottom: 1rem;'>Need Emergency Help?</h2>
                <p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>
                    Click the button below to request an ambulance. You'll be asked a few quick questions 
                    to help us prioritize your emergency and dispatch the appropriate medical response.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚨 REQUEST AMBULANCE", key="emergency_btn", use_container_width=True, type="primary"):
            st.session_state.request_step = 'patient_info'
            st.session_state.request_submitted = False
            st.rerun()
    
    # Information cards - GREEN THEME
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>📋 What to Expect</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>1️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Patient Information</h4>
                <p style='text-align: center; color: #64748b;'>Provide basic details about the patient</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>2️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Quick Assessment</h4>
                <p style='text-align: center; color: #64748b;'>Answer questions about the emergency</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>3️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Ambulance Dispatch</h4>
                <p style='text-align: center; color: #64748b;'>Get confirmation and estimated arrival</p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.request_step == 'patient_info':
    # Patient information form
    st.markdown("<h3 class='section-header'>👤 Patient Information</h3>", unsafe_allow_html=True)
    st.markdown("<p class='info-message'>Please provide the following information about the patient</p>", unsafe_allow_html=True)
    
    with st.form("patient_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Patient Name *", placeholder="Full name")
            age = st.number_input("Age *", min_value=0, max_value=120, value=30)
            phone = st.text_input("Contact Number *", placeholder="+1234567890")
        
        with col2:
            address = st.text_area("Current Location/Address *", placeholder="Street address, landmarks", height=100)
            relationship = st.selectbox("Your relationship to patient", 
                                       ["Self", "Family member", "Friend", "Bystander", "Healthcare worker"])
        
        submitted = st.form_submit_button("Continue to Assessment", type="primary", use_container_width=True)
        
        if submitted:
            if name and age and phone and address:
                st.session_state.patient_info = {
                    'name': name,
                    'age': age,
                    'phone': phone,
                    'address': address,
                    'relationship': relationship,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.request_step = 'questionnaire'
                st.rerun()
            else:
                st.error("Please fill in all required fields marked with *")

elif st.session_state.request_step == 'questionnaire':
    # Emergency questionnaire
    st.markdown("<h3 class='section-header'>🩺 Emergency Assessment Questionnaire</h3>", unsafe_allow_html=True)
    st.markdown("<p class='warning-message'>⚠️ Please answer all questions accurately. This helps us prioritize your emergency.</p>", unsafe_allow_html=True)
    
    answers = {}
    
    with st.form("questionnaire_form"):
        for key, q_data in questionnaire.items():
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q_data['question']}**")
            
            selected = st.radio(
                f"Select one:",
                options=q_data['options'],
                key=f"q_{key}",
                label_visibility="collapsed"
            )
            
            selected_idx = q_data['options'].index(selected)
            answers[key] = q_data['weights'][selected_idx]
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional symptoms
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)
        st.markdown("**Additional Symptoms or Information**")
        additional_info = st.text_area("Describe any other symptoms or relevant information", 
                                      placeholder="e.g., medications, allergies, pre-existing conditions",
                                      height=100)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.request_step = 'patient_info'
                st.rerun()
        with col2:
            if st.form_submit_button("Submit Assessment →", type="primary", use_container_width=True):
                st.session_state.questionnaire_answers = answers
                st.session_state.patient_info['additional_info'] = additional_info
                st.session_state.request_step = 'result'
                st.rerun()

elif st.session_state.request_step == 'result':
    # Calculate severity and show result
    priority, severity_score, action = calculate_severity(st.session_state.questionnaire_answers)
    condition = get_condition_from_answers(st.session_state.questionnaire_answers)
    
    # Only add to queue once
    if not st.session_state.request_submitted:
        current_queue = load_queue()
        current_stats = load_stats()
        
        new_request = {
            'id': abs(hash(str(st.session_state.patient_info) + str(datetime.now()))),
            'name': st.session_state.patient_info['name'],
            'age': st.session_state.patient_info['age'],
            'location': st.session_state.patient_info['address'],
            'condition': condition,
            'priority': priority,
            'severity_score': severity_score,
            'symptoms': st.session_state.patient_info.get('additional_info', 'Various symptoms'),
            'time': 'Just now',
            'phone': st.session_state.patient_info['phone']
        }
        
        request_id = new_request['id']
        existing_ids = {req.get('id') for req in current_queue}
        
        if request_id not in existing_ids:
            current_queue.append(new_request)
            save_queue(current_queue)
            
            current_stats['calls_today'] += 1
            save_stats(current_stats)
        
        st.session_state.request_submitted = True
    
    # Show result with priority indicator
    st.markdown("<h3 class='section-header'>✅ Request Submitted Successfully</h3>", unsafe_allow_html=True)
    
    priority_class = {
        'HIGH': 'severity-high',
        'MEDIUM': 'severity-medium',
        'LOW': 'severity-low'
    }[priority]
    
    if priority == 'HIGH':
        st.markdown(f"<p class='error-message'><span class='priority-indicator {priority_class}'></span><strong>CRITICAL EMERGENCY - Priority: {priority}</strong><br>Severity Score: {severity_score}/150</p>", unsafe_allow_html=True)
    elif priority == 'MEDIUM':
        st.markdown(f"<p class='warning-message'><span class='priority-indicator {priority_class}'></span><strong>URGENT - Priority: {priority}</strong><br>Severity Score: {severity_score}/150</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='success-message'><span class='priority-indicator {priority_class}'></span><strong>NON-CRITICAL - Priority: {priority}</strong><br>Severity Score: {severity_score}/150</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class='result-box'>
                <h3>📋 Patient Details</h3>
                <p><strong>Name:</strong> {}</p>
                <p><strong>Age:</strong> {} years</p>
                <p><strong>Location:</strong> {}</p>
                <p><strong>Contact:</strong> {}</p>
            </div>
        """.format(
            st.session_state.patient_info['name'],
            st.session_state.patient_info['age'],
            st.session_state.patient_info['address'],
            st.session_state.patient_info['phone']
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='result-box'>
                <h3>🏥 Assessment Results</h3>
                <p><strong>Condition:</strong> {condition}</p>
                <p><strong>Priority Level:</strong> {priority}</p>
                <p><strong>Recommended Action:</strong> {action}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dispatch information
    if priority == 'HIGH':
        st.markdown("""
            <p class='success-message'>
                <strong>🚑 Ambulance is being dispatched IMMEDIATELY!</strong><br>
                <strong>Estimated Arrival Time:</strong> 5-8 minutes<br><br>
                <strong>While waiting:</strong><br>
                • Stay with the patient<br>
                • Keep the patient comfortable<br>
                • Do not give food or water<br>
                • Call back if condition worsens
            </p>
        """, unsafe_allow_html=True)
    elif priority == 'MEDIUM':
        st.markdown("""
            <p class='success-message'>
                <strong>🚑 Ambulance will be dispatched within 15 minutes</strong><br>
                <strong>Estimated Arrival Time:</strong> 15-25 minutes<br><br>
                <strong>While waiting:</strong><br>
                • Monitor patient's condition<br>
                • Keep patient comfortable and calm<br>
                • Have medical history ready if available
            </p>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <p class='info-message'>
                <strong>🚑 Your request has been queued</strong><br>
                <strong>Estimated Arrival Time:</strong> 25-40 minutes<br><br>
                <strong>While waiting:</strong><br>
                • Keep patient comfortable<br>
                • Monitor for any changes<br>
                • Call back if condition worsens
            </p>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📞 Call Emergency Hotline", use_container_width=True):
            st.info("📞 Emergency Hotline: 108")
    with col2:
        if st.button("🏠 Return to Home", use_container_width=True, type="primary"):
            st.session_state.request_step = 'home'
            st.session_state.questionnaire_answers = {}
            st.session_state.patient_info = {}
            st.session_state.request_submitted = False
            st.rerun()

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.6); padding: 1rem 0;'>
        <p><strong>Emergency Services Available 24/7</strong></p>
        <p>For immediate life-threatening emergencies, call 108</p>
    </div>
""", unsafe_allow_html=True)