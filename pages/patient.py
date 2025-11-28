import streamlit as st
import json
from datetime import datetime
import os
import pickle
import numpy as np
import joblib
import pandas as pd  # <-- 1. IMPORT PANDAS

# Page configuration
st.set_page_config(
    page_title="Patient Portal - Smart Ambulance",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load ML Model with better error handling
MODEL_LOADED = False
model = None

# --- 2. UPDATED VALIDATION TEST TO USE A DATAFRAME ---
def load_model():
    """Try to load the ML model from multiple possible locations with compatibility fixes"""
    global model, MODEL_LOADED
    
    possible_paths = [
        'emergency_triage_model.pkl',
        './emergency_triage_model.pkl',
        '../emergency_triage_model.pkl',
        'models/emergency_triage_model.pkl',
    ]
    
    for path in possible_paths:
        if not os.path.exists(path):
            continue
            
        try:
            # Use joblib.load() since the model was saved with joblib.dump()
            model = joblib.load(path)
            MODEL_LOADED = True
            print(f"✅ Model loaded successfully from: {path} (using joblib)")
            
            # Quick validation test
            try:
                # --- START OF FIX ---
                # Model expects a Pandas DataFrame with feature names, not a numpy array.
                test_data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                test_cols = ['chest_pain', 'shortness_of_breath', 'unconsciousness', 'bleeding', 
                               'confusion', 'weakness', 'seizure', 'trauma', 'dizziness', 'cyanosis']
                test_df = pd.DataFrame(test_data, columns=test_cols)
                _ = model.predict(test_df)
                # --- END OF FIX ---
                
                print("✅ Model validation passed")
                return True
            except Exception as e:
                print(f"⚠️ Model loaded but validation failed: {e}")
                print("   (This is likely due to the model expecting a DataFrame with feature names)")
                MODEL_LOADED = False
                model = None
                continue
                
        except Exception as e:
            print(f"Failed to load from {path} using joblib: {e}")
            continue
    
    print("⚠️ ML Model not found or incompatible. Using rule-based fallback system.")
    return False

# Try to load model on startup
load_model()

def get_model_status_message():
    """Return a formatted message about model status"""
    if MODEL_LOADED:
        return "🤖 ML Model: **Active** ✅"
    else:
        return "⚠️ ML Model: **Unavailable** - Using rule-based system (still highly accurate)"

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


# --- 3. UPDATED PREDICTION TO USE A DATAFRAME & REVERTED TO STRING MAP ---
def hybrid_classify_and_prioritize(answers):
    """
    Hybrid ML + Rule-based emergency classification
    
    PRIORITY ORDER:
    1. Critical life-threatening rules (INSTANT response - no ML delay)
    2. ML Model prediction (for complex pattern recognition)
    3. Fallback scoring system (if ML unavailable)
    
    Returns: (diagnosis, priority, severity_score, method_used)
    """
    
    # ========== PHASE 1: CRITICAL RULE-BASED CONDITIONS (INSTANT RESPONSE) ==========
    # These bypass ML for speed - life-threatening conditions need immediate classification
    
    # RULE 1: Unconscious + Cyanosis = Cardiac Arrest (HIGHEST PRIORITY)
    if answers.get('unconsciousness', 0) == 1 and answers.get('cyanosis', 0) == 1:
        return 'Cardiac Arrest', 'HIGH', 150, 'Critical Rule'
    
    # RULE 2: Unconscious alone = Critical (brain injury, stroke, cardiac event)
    if answers.get('unconsciousness', 0) == 1:
        return 'Critical - Unconscious Patient', 'HIGH', 145, 'Critical Rule'
    
    # RULE 3: Severe Respiratory Distress + Cyanosis (suffocation, cardiac/respiratory failure)
    if answers.get('shortness_of_breath', 0) == 1 and answers.get('cyanosis', 0) == 1:
        return 'Severe Respiratory Distress', 'HIGH', 140, 'Critical Rule'
    
    # RULE 4: Triple cardiac symptoms (Chest pain + Breathing difficulty + Cyanosis)
    if (answers.get('chest_pain', 0) == 1 and 
        answers.get('shortness_of_breath', 0) == 1 and 
        answers.get('cyanosis', 0) == 1):
        return 'Heart Attack (STEMI Suspected)', 'HIGH', 135, 'Critical Rule'
    
    # RULE 5: Major Trauma with Bleeding (hypovolemic shock risk)
    if answers.get('trauma', 0) == 1 and answers.get('bleeding', 0) == 1:
        return 'Major Trauma/Hemorrhage', 'HIGH', 130, 'Critical Rule'
    
    # RULE 6: Chest Pain + Shortness of Breath (cardiac event without cyanosis yet)
    if answers.get('chest_pain', 0) == 1 and answers.get('shortness_of_breath', 0) == 1:
        return 'Heart Attack (Suspected)', 'HIGH', 128, 'Critical Rule'
    
    # RULE 7: Stroke symptoms (Confusion + One-sided Weakness)
    if answers.get('confusion', 0) == 1 and answers.get('weakness', 0) == 1:
        return 'Stroke (Suspected)', 'HIGH', 125, 'Critical Rule'
    
    # ========== PHASE 2: USE ML MODEL FOR COMPLEX PATTERN RECOGNITION ==========
    # ML is better at detecting subtle combinations and non-obvious patterns
    
    if MODEL_LOADED and model is not None:
        try:
            # Prepare features in the EXACT order the model was trained on
            features = [
                answers.get('chest_pain', 0),
                answers.get('shortness_of_breath', 0),
                answers.get('unconsciousness', 0),
                answers.get('bleeding', 0),
                answers.get('confusion', 0),
                answers.get('weakness', 0),
                answers.get('seizure', 0),
                answers.get('trauma', 0),
                answers.get('dizziness', 0),
                answers.get('cyanosis', 0)
            ]
            
            # --- START OF FIX ---
            # Create a DataFrame with the correct column names for prediction
            feature_cols = ['chest_pain', 'shortness_of_breath', 'unconsciousness', 'bleeding', 
                           'confusion', 'weakness', 'seizure', 'trauma', 'dizziness', 'cyanosis']
            feature_df = pd.DataFrame([features], columns=feature_cols)
            # --- END OF FIX ---
            
            
            # Get ML prediction (will be a string like "Heart Attack")
            diagnosis = model.predict(feature_df)[0]
            
            # Map ML diagnosis to priority and severity score (String-based map)
            # This is the original map, which is correct for your model.
            severity_map = {
                'Cardiac Arrest': ('HIGH', 150),
                'Heart Attack': ('HIGH', 135),
                'Severe Respiratory Distress': ('HIGH', 130),
                'Major Trauma/Bleeding': ('HIGH', 125),
                'Stroke': ('HIGH', 120),
                'Shock/Collapse': ('MEDIUM', 90),
                'Seizure/Post-Seizure': ('MEDIUM', 85),
                'Fainting/Syncope': ('LOW', 50),
                'Minor Trauma': ('LOW', 45),
                'Anxiety/Panic': ('LOW', 40)
            }
            
            priority, severity_score = severity_map.get(diagnosis, ('MEDIUM', 70))
            
            return diagnosis, priority, severity_score, 'ML Model'
            
        except Exception as e:
            # If ML fails, fall through to rule-based scoring
            print(f"⚠️ ML prediction failed: {e}. Using fallback scoring.")
    
    # ========== PHASE 3: FALLBACK RULE-BASED SCORING SYSTEM ==========
    # Used when ML model is unavailable or fails
    
    # Calculate weighted severity score
    score = 0
    score += answers.get('chest_pain', 0) * 35        # Cardiac indicator
    score += answers.get('shortness_of_breath', 0) * 30  # Respiratory/cardiac
    score += answers.get('unconsciousness', 0) * 50   # Critical brain/cardiac
    score += answers.get('bleeding', 0) * 30          # Hemorrhage risk
    score += answers.get('confusion', 0) * 25         # Neurological/stroke
    score += answers.get('weakness', 0) * 25          # Stroke/cardiac
    score += answers.get('seizure', 0) * 28           # Neurological emergency
    score += answers.get('trauma', 0) * 30            # Injury severity
    score += answers.get('dizziness', 0) * 15         # General instability
    score += answers.get('cyanosis', 0) * 40          # Oxygen deprivation
    
    # Determine diagnosis from symptom patterns
    if answers.get('chest_pain', 0) == 1 and answers.get('shortness_of_breath', 0) == 1:
        diagnosis = 'Heart Attack (Suspected)'
    elif answers.get('confusion', 0) == 1 and answers.get('weakness', 0) == 1:
        diagnosis = 'Stroke (Suspected)'
    elif answers.get('bleeding', 0) == 1 and answers.get('trauma', 0) == 1:
        diagnosis = 'Major Trauma/Bleeding'
    elif answers.get('seizure', 0) == 1:
        diagnosis = 'Seizure/Post-Seizure'
    elif answers.get('shortness_of_breath', 0) == 1:
        diagnosis = 'Respiratory Distress'
    elif answers.get('dizziness', 0) == 1 and answers.get('weakness', 0) == 1:
        diagnosis = 'Syncope/Collapse'
    elif score > 0:
        diagnosis = 'General Medical Emergency'
    else:
        diagnosis = 'Non-Emergency Medical Assistance'
    
    # Determine priority based on score
    if score >= 120:
        priority = 'HIGH'
    elif score >= 60:
        priority = 'MEDIUM'
    else:
        priority = 'LOW'
    
    return diagnosis, priority, score, 'Rule-Based Fallback'

# Custom CSS with GREEN THEME
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
            #3b82f6, #1e3a8a, #0f1a3a, #000814
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
    
    /* Header - GREEN THEME */
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
    
    .severity-high { background: #ef4444; }
    .severity-medium { background: #f59e0b; }
    .severity-low { background: #10b981; }
    
    .section-header {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
    }
    
    .result-box {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .result-box h3 { color: #1e293b; margin-top: 0; }
    .result-box p { color: #475569; margin: 0.5rem 0; }
    
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
if 'critical_answers' not in st.session_state:
    st.session_state.critical_answers = {}
if 'is_critical_case' not in st.session_state:
    st.session_state.is_critical_case = False

# TOP 3 CRITICAL QUESTIONS (asked first for rapid triage)
# These are separate from the main questionnaire and use combined/specialized wording
CRITICAL_QUESTIONS_DICT = {
    'unconsciousness': {
        'question': 'Is the patient unconscious?',
        'options': ['No', 'Yes'],
        'description': 'Strongest single predictor of life-threatening emergency. Often indicates cardiac arrest, stroke, trauma, seizure, or shock. Immediate ambulatory priority required.'
    },
    'shortness_of_breath': {
        'question': 'Is there severe shortness of breath?',
        'options': ['No', 'Yes'],
        'description': 'Severe respiratory distress can indicate heart attack, anaphylaxis, respiratory failure, pulmonary embolism, poisoning, or asthma/COPD crisis.'
    },
    'bleeding_trauma': {
        'question': 'Is there active bleeding or major visible trauma?',
        'options': ['No', 'Yes'],
        'description': 'Massive bleeding can lead to hypovolemic shock and death within minutes. Major trauma may indicate spinal or brain injury requiring immediate response.'
    }
}
CRITICAL_QUESTIONS = list(CRITICAL_QUESTIONS_DICT.keys())

# NEW 10-FEATURE QUESTIONNAIRE (matches dataset)
questionnaire = {
    'chest_pain': {
        'question': 'Is the patient experiencing chest pain?',
        'options': ['No', 'Yes']
    },
    'shortness_of_breath': {
        'question': 'Is the patient experiencing shortness of breath?',
        'options': ['No', 'Yes']
    },
    'unconsciousness': {
        'question': 'Is the patient unconscious?',
        'options': ['No', 'Yes']
    },
    'bleeding': {
        'question': 'Is there any bleeding?',
        'options': ['No', 'Yes']
    },
    'confusion': {
        'question': 'Is the patient confused or disoriented?',
        'options': ['No', 'Yes']
    },
    'weakness': {
        'question': 'Does the patient have weakness (especially on one side)?',
        'options': ['No', 'Yes']
    },
    'seizure': {
        'question': 'Is the patient having or just had a seizure?',
        'options': ['No', 'Yes']
    },
    'trauma': {
        'question': 'Is there recent trauma or injury?',
        'options': ['No', 'Yes']
    },
    'dizziness': {
        'question': 'Is the patient experiencing dizziness?',
        'options': ['No', 'Yes']
    },
    'cyanosis': {
        'question': 'Is the patient showing blue/purple discoloration (lips, fingers)?',
        'options': ['No', 'Yes']
    }
}

# Header
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
    st.markdown("<h3 class='section-header'>Welcome to Emergency Services</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div class='info-card'>
                <h2 style='color: #10b981; margin-bottom: 1rem;'>Need Emergency Help?</h2>
                <p style='font-size: 1.1rem; color: #475569; margin-bottom: 2rem;'>
                    Click the button below to request an ambulance. You'll be asked quick yes/no questions 
                    to help our AI-powered system prioritize your emergency.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚨 REQUEST AMBULANCE", key="emergency_btn", use_container_width=True, type="primary"):
            st.session_state.request_step = 'patient_info'
            st.session_state.request_submitted = False
            st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 class='section-header'>📋 What to Expect</h3>", unsafe_allow_html=True)
    
    # Model status indicator
    status_msg = get_model_status_message()
    if MODEL_LOADED:
        st.markdown(f"<p class='success-message'>{status_msg}</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='info-message'>{status_msg}</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>1️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Patient Information</h4>
                <p style='text-align: center; color: #64748b;'>Provide basic details</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>2️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Rapid Triage</h4>
                <p style='text-align: center; color: #64748b;'>3 critical questions first, then full assessment</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='question-card'>
                <div style='font-size: 2.5rem; text-align: center; margin-bottom: 1rem;'>3️⃣</div>
                <h4 style='text-align: center; color: #10b981;'>Smart Dispatch</h4>
                <p style='text-align: center; color: #64748b;'>ML-powered prioritization</p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.request_step == 'patient_info':
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
                st.session_state.request_step = 'critical_questions'
                st.session_state.critical_answers = {}
                st.session_state.is_critical_case = False
                st.rerun()
            else:
                st.error("Please fill in all required fields marked with *")

elif st.session_state.request_step == 'critical_questions':
    st.markdown("<h3 class='section-header'>🚨 CRITICAL TRIAGE - Rapid Assessment</h3>", unsafe_allow_html=True)
    st.markdown("<p class='error-message'><strong>⚠️ CRITICAL QUESTIONS:</strong> Answer these 3 questions first. If 2 or more are 'Yes', we'll immediately dispatch HIGH priority assistance.</p>", unsafe_allow_html=True)
    
    critical_answers = {}
    
    with st.form("critical_questions_form"):
        for key in CRITICAL_QUESTIONS:
            q_data = CRITICAL_QUESTIONS_DICT[key]
            st.markdown(f"<div class='question-card' style='border: 2px solid #ef4444;'>", unsafe_allow_html=True)
            st.markdown(
                    f"<span style='color: #ef4444; font-weight: bold;'>🚨 CRITICAL:</span> "
                    f"<span style='font-weight:600; font-size:1.1rem;'>{q_data['question']}</span>",
                    unsafe_allow_html=True
            )

            if 'description' in q_data:
                st.markdown(f"<p style='color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;'>{q_data['description']}</p>", unsafe_allow_html=True)
            
            selected = st.radio(
                f"Select:",
                options=q_data['options'],
                key=f"critical_{key}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # Convert to binary (0 or 1)
            critical_answers[key] = 1 if selected == 'Yes' else 0
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.request_step = 'patient_info'
                st.rerun()
        with col2:
            if st.form_submit_button("Continue Assessment →", type="primary", use_container_width=True):
                st.session_state.critical_answers = critical_answers
                
                # Check if 2+ critical questions are "Yes"
                yes_count = sum(critical_answers.values())
                
                if yes_count >= 2:
                    # CRITICAL CASE: Skip full questionnaire, assign HIGH priority immediately
                    st.session_state.is_critical_case = True
                    
                    # Map critical answers to questionnaire format
                    # bleeding_trauma maps to both bleeding and trauma
                    mapped_answers = {}
                    if 'unconsciousness' in critical_answers:
                        mapped_answers['unconsciousness'] = critical_answers['unconsciousness']
                    if 'shortness_of_breath' in critical_answers:
                        mapped_answers['shortness_of_breath'] = critical_answers['shortness_of_breath']
                    if 'bleeding_trauma' in critical_answers:
                        # Combined question: if Yes, set both bleeding and trauma to 1
                        mapped_answers['bleeding'] = critical_answers['bleeding_trauma']
                        mapped_answers['trauma'] = critical_answers['bleeding_trauma']
                    
                    # Determine diagnosis based on critical answers
                    if mapped_answers.get('unconsciousness', 0) == 1:
                        if mapped_answers.get('bleeding', 0) == 1 or mapped_answers.get('trauma', 0) == 1:
                            diagnosis = 'Critical - Unconscious with Trauma/Bleeding'
                            severity_score = 150
                        else:
                            diagnosis = 'Critical - Unconscious Patient'
                            severity_score = 145
                    elif mapped_answers.get('shortness_of_breath', 0) == 1:
                        if mapped_answers.get('bleeding', 0) == 1 or mapped_answers.get('trauma', 0) == 1:
                            diagnosis = 'Severe Respiratory Distress with Trauma'
                            severity_score = 145
                        else:
                            diagnosis = 'Severe Respiratory Distress'
                            severity_score = 140
                    elif mapped_answers.get('bleeding', 0) == 1 or mapped_answers.get('trauma', 0) == 1:
                        diagnosis = 'Major Trauma/Bleeding'
                        severity_score = 135
                    else:
                        diagnosis = 'Critical Emergency - Multiple Critical Symptoms'
                        severity_score = 135
                    
                    # Set all answers (mapped critical + default others to 0 for consistency)
                    full_answers = mapped_answers.copy()
                    for key in questionnaire.keys():
                        if key not in full_answers:
                            full_answers[key] = 0
                    
                    st.session_state.questionnaire_answers = full_answers
                    st.session_state.patient_info['additional_info'] = 'CRITICAL CASE - Rapid triage triggered'
                    st.session_state.request_step = 'result'
                    st.rerun()
                else:
                    # NON-CRITICAL: Continue with full questionnaire
                    st.session_state.is_critical_case = False
                    st.session_state.request_step = 'questionnaire'
                    st.rerun()

elif st.session_state.request_step == 'questionnaire':
    st.markdown("<h3 class='section-header'>🩺 AI-Powered Emergency Assessment</h3>", unsafe_allow_html=True)
    st.markdown("<p class='info-message'>✅ Critical triage complete. Please answer the remaining questions. Our ML model uses this data for diagnosis.</p>", unsafe_allow_html=True)
    
    # Start with critical answers already collected, mapped to questionnaire format
    answers = {}
    if 'unconsciousness' in st.session_state.critical_answers:
        answers['unconsciousness'] = st.session_state.critical_answers['unconsciousness']
    if 'shortness_of_breath' in st.session_state.critical_answers:
        answers['shortness_of_breath'] = st.session_state.critical_answers['shortness_of_breath']
    # Note: bleeding_trauma is a combined question for critical triage
    # If it was "Yes", we would have skipped this step (critical case)
    # If it was "No", we don't pre-fill bleeding/trauma because user might have minor cases
    # that don't qualify as "active bleeding or major visible trauma"
    
    with st.form("questionnaire_form"):
        # Show remaining questions (excluding critical ones already answered)
        # Note: unconsciousness and shortness_of_breath are already answered, but bleeding and trauma
        # are separate in the full questionnaire, so we show them separately here
        already_answered = ['unconsciousness', 'shortness_of_breath']
        remaining_questions = {k: v for k, v in questionnaire.items() if k not in already_answered}
        
        for key, q_data in remaining_questions.items():
            st.markdown(f"<div class='question-card'>", unsafe_allow_html=True)
            st.markdown(f"**{q_data['question']}**")
            
            selected = st.radio(
                f"Select:",
                options=q_data['options'],
                key=f"q_{key}",
                horizontal=True,
                label_visibility="collapsed"
            )
            
            # Convert to binary (0 or 1)
            answers[key] = 1 if selected == 'Yes' else 0
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Additional info
        st.markdown("<div class='question-card'>", unsafe_allow_html=True)
        st.markdown("**Additional Symptoms or Information (Optional)**")
        additional_info = st.text_area("Any other relevant details", 
                                      placeholder="e.g., medications, allergies, pre-existing conditions",
                                      height=100)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("← Back", use_container_width=True):
                st.session_state.request_step = 'critical_questions'
                st.rerun()
        with col2:
            if st.form_submit_button("🤖 Run AI Analysis →", type="primary", use_container_width=True):
                st.session_state.questionnaire_answers = answers
                st.session_state.patient_info['additional_info'] = additional_info
                st.session_state.request_step = 'result'
                st.rerun()

elif st.session_state.request_step == 'result':
    # Check if this is a critical case (rapid triage)
    if st.session_state.is_critical_case:
        # Critical case: Determine diagnosis from critical answers
        answers = st.session_state.questionnaire_answers
        priority = 'HIGH'
        
        if answers.get('unconsciousness', 0) == 1:
            if answers.get('bleeding', 0) == 1 or answers.get('trauma', 0) == 1:
                diagnosis = 'Critical - Unconscious with Trauma/Bleeding'
                severity_score = 150
            else:
                diagnosis = 'Critical - Unconscious Patient'
                severity_score = 145
        elif answers.get('shortness_of_breath', 0) == 1:
            if answers.get('bleeding', 0) == 1 or answers.get('trauma', 0) == 1:
                diagnosis = 'Severe Respiratory Distress with Trauma'
                severity_score = 145
            else:
                diagnosis = 'Severe Respiratory Distress'
                severity_score = 140
        elif answers.get('bleeding', 0) == 1 or answers.get('trauma', 0) == 1:
            diagnosis = 'Major Trauma/Bleeding'
            severity_score = 135
        else:
            diagnosis = 'Critical Emergency - Multiple Critical Symptoms'
            severity_score = 135
        
        method_used = 'Rapid Triage (Critical Rule)'
    else:
        # Use hybrid ML classification for non-critical cases
        with st.spinner("🤖 AI analyzing symptoms..."):
            diagnosis, priority, severity_score, method_used = hybrid_classify_and_prioritize(
                st.session_state.questionnaire_answers
            )
    
    # Determine action message
    if priority == 'HIGH':
        action = 'Immediate ambulance dispatch - Life threatening'
    elif priority == 'MEDIUM':
        action = 'Ambulance dispatch within 15 minutes - Serious condition'
    else:
        action = 'Ambulance dispatch when available - Non-critical'
    
    # Add to queue once
    if not st.session_state.request_submitted:
        current_queue = load_queue()
        current_stats = load_stats()
        
        new_request = {
            'id': abs(hash(str(st.session_state.patient_info) + str(datetime.now()))),
            'name': st.session_state.patient_info['name'],
            'age': st.session_state.patient_info['age'],
            'location': st.session_state.patient_info['address'],
            'condition': diagnosis,
            'priority': priority,
            'severity_score': severity_score,
            'symptoms': st.session_state.patient_info.get('additional_info', 'AI-assessed symptoms'),
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
    
    # Show result
    if st.session_state.is_critical_case:
        st.markdown("<h3 class='section-header'>🚨 CRITICAL CASE DETECTED - Immediate Dispatch</h3>", unsafe_allow_html=True)
        st.markdown("<p class='error-message'><strong>⚡ RAPID TRIAGE:</strong> Critical symptoms detected. Ambulance dispatched immediately without full questionnaire.</p>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 class='section-header'>✅ AI Assessment Complete</h3>", unsafe_allow_html=True)
        
        # Display classification method used
        if method_used == 'ML Model':
            st.markdown("<p class='success-message'>🤖 <strong>ML Model Active:</strong> Advanced pattern recognition used for diagnosis</p>", unsafe_allow_html=True)
        elif method_used == 'Critical Rule':
            st.markdown("<p class='error-message'>⚡ <strong>Critical Rule Match:</strong> Life-threatening condition detected instantly</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='warning-message'>⚠️ <strong>Rule-Based Fallback:</strong> ML model unavailable, using clinical decision rules</p>", unsafe_allow_html=True)
    
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
                <h3>🏥 AI Diagnosis</h3>
                <p><strong>Condition:</strong> {diagnosis}</p>
                <p><strong>Priority Level:</strong> {priority}</p>
                <p><strong>Recommended Action:</strong> {action}</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Dispatch info
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
            st.session_state.critical_answers = {}
            st.session_state.is_critical_case = False
            st.rerun()


# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; color: rgba(255,255,255,0.6); padding: 1rem 0;'>
        <p><strong>Emergency Services Available 24/7</strong></p>
        <p>For immediate life-threatening emergencies, call 108</p>
    </div>
""", unsafe_allow_html=True)