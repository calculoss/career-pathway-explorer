import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import anthropic
import os
import json
from dotenv import load_dotenv
from multi_family_database import MultiFamilyDatabase
from canvas_integration import CanvasIntegrator, SimpleMilestoneGenerator, show_canvas_setup
from enhanced_auth import EnhancedAuthSystem, create_enhanced_login_form, create_enhanced_registration_form
import hashlib
import secrets

# Page configuration
st.set_page_config(
    page_title="CareerPath | Family Career Guidance",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# NUCLEAR SPACING FIX
st.markdown("""
<style>
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        margin-top: 0rem !important;
    }
    .main .block-container {
        padding-top: 0rem !important;
        max-width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    .stMarkdown {
        margin-bottom: 0rem !important;
    }
    div[data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0rem !important;
    }
    .auth-form-container {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Session info styling */
.session-info {
    background: #e3f2fd;
    border: 1px solid #90caf9;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
    font-size: 0.9em;
    color: #1565c0;
}

/* Enhanced button hover effects */
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(28, 73, 128, 0.3);
}

/* Login method tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
    justify-content: center;
}

.stTabs [data-baseweb="tab"] {
    padding: 1rem 2rem;
    border-radius: 8px;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
}

/* Error message styling */
.stError {
    border-left: 4px solid #dc3545;
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}

/* Success message styling */
.stSuccess {
    border-left: 4px solid #28a745;
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}
</style>
""", unsafe_allow_html=True)

# Complete Khan Academy-inspired CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;500;600;700&display=swap');

    /* =================== GLOBAL STYLES =================== */
    .stApp {
        background-color: #ffffff;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #21242c;
    }

    /* Remove Streamlit elements AND spacing */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
    }

    /* CRITICAL: Remove all Streamlit default spacing */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        max-width: none !important;
    }

    .main .block-container {
        padding-top: 0rem !important;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }

    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0rem !important;
    }

    /* =================== MAIN LAYOUT =================== */
    .main-header {
        background: #ffffff;
        border-bottom: 1px solid #e7e8ea;
        padding: 16px 0;
        margin: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .header-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
    }

    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 24px;
        background: #ffffff;
    }

    /* =================== GLOBAL STYLES =================== */
    .stApp {
        background-color: #ffffff;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #21242c;
    }

    /* Remove Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
    }

    /* Fix Streamlit spacing issues */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
    }

    .element-container {
        margin: 0 !important;
    }

    .stMarkdown {
        margin-bottom: 0 !important;
    }

    div[data-testid="stVerticalBlock"] > div:first-child {
        margin-top: 0 !important;
    }

    /* =================== MAIN LAYOUT =================== */
    .main-header {
        background: #ffffff;
        border-bottom: 1px solid #e7e8ea;
        padding: 16px 0;
        margin-bottom: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .header-container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 24px;
    }

    .logo-section {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .app-logo {
        width: 40px;
        height: 40px;
        background: #00a60e;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 20px;
        font-weight: 700;
    }

    .app-title {
        font-size: 24px;
        font-weight: 600;
        color: #21242c;
        margin: 0;
    }

    .app-subtitle {
        font-size: 14px;
        color: #626569;
        margin: 0;
        margin-top: 2px;
    }

    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 24px;
        background: #ffffff;
        min-height: calc(100vh - 120px);
    }

    /* Fix gap between header and content */
    .block-container {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .element-container {
        margin: 0 !important;
    }

    /* Override Streamlit's default spacing */
    .stApp > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* =================== TYPOGRAPHY =================== */
    .page-title {
        font-size: 32px;
        font-weight: 600;
        color: #21242c;
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .page-subtitle {
        font-size: 18px;
        color: #626569;
        margin-bottom: 32px;
        line-height: 1.4;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: #21242c;
        margin-bottom: 16px;
        margin-top: 32px;
    }

    .section-subtitle {
        font-size: 16px;
        color: #626569;
        margin-bottom: 24px;
        line-height: 1.5;
    }

    /* =================== NAVIGATION TABS =================== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: transparent;
        border-bottom: 2px solid #e7e8ea;
        margin-bottom: 32px;
        padding: 0;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        border-radius: 0;
        border: none;
        background: transparent;
        color: #626569;
        font-weight: 500;
        font-size: 16px;
        border-bottom: 3px solid transparent;
        transition: all 0.2s ease;
        margin-bottom: -2px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #21242c;
        background: rgba(0, 166, 14, 0.05);
    }

    .stTabs [aria-selected="true"] {
        color: #00a60e !important;
        border-bottom-color: #00a60e !important;
        background: transparent !important;
        font-weight: 600 !important;
    }

    /* =================== CARDS & CONTAINERS =================== */
    .family-header {
        background: linear-gradient(135deg, #00a60e 0%, #008a0c 100%);
        color: white;
        border-radius: 12px;
        padding: 32px;
        margin-bottom: 32px;
        box-shadow: 0 4px 16px rgba(0, 166, 14, 0.2);
    }

    .family-title {
        font-size: 28px;
        font-weight: 600;
        margin: 0 0 8px 0;
    }

    .family-details {
        font-size: 16px;
        margin: 0;
        opacity: 0.9;
    }

    .student-card {
        background: #ffffff;
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .student-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: #00a60e;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .student-card:hover {
        border-color: #00a60e;
        box-shadow: 0 8px 24px rgba(0, 166, 14, 0.15);
        transform: translateY(-2px);
    }

    .student-card:hover::before {
        opacity: 1;
    }

    .student-name {
        font-size: 20px;
        font-weight: 600;
        color: #21242c;
        margin: 0 0 8px 0;
    }

    .student-details {
        font-size: 14px;
        color: #626569;
        line-height: 1.6;
        margin: 0;
    }

    /* =================== CANVAS INTEGRATION =================== */
    .canvas-status {
        background: #ffffff;
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        transition: all 0.2s ease;
    }

    .canvas-connected {
        border-color: #00a60e;
        background: linear-gradient(135deg, #f0f9f1 0%, #e8f5e8 100%);
    }

    .canvas-title {
        font-size: 18px;
        font-weight: 600;
        color: #21242c;
        margin: 0 0 4px 0;
    }

    .canvas-subtitle {
        font-size: 14px;
        color: #626569;
        margin: 0;
    }

    /* =================== BUTTONS =================== */
    .stButton > button {
        background: linear-gradient(135deg, #00a60e 0%, #008a0c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 14px 28px;
        font-size: 16px;
        font-weight: 600;
        font-family: 'Lato', sans-serif;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0, 166, 14, 0.2);
        text-transform: none;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #008a0c 0%, #007a0b 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 166, 14, 0.3);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(0, 166, 14, 0.2);
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: #ffffff;
        color: #21242c;
        border: 2px solid #c4c6ca;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .stButton > button[kind="secondary"]:hover {
        background: #f7f8fa;
        border-color: #9ca0a5;
        transform: translateY(-1px);
    }

    /* =================== FORMS & INPUTS =================== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        border: 2px solid #c4c6ca;
        border-radius: 8px;
        padding: 14px 16px;
        font-size: 16px;
        font-family: 'Lato', sans-serif;
        background: #ffffff;
        color: #21242c;
        transition: all 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00a60e;
        outline: none;
        box-shadow: 0 0 0 3px rgba(0, 166, 14, 0.1);
    }

    /* Form labels */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stNumberInput > label {
        font-weight: 500;
        color: #21242c;
        margin-bottom: 8px;
    }

    /* =================== FORMS CONTAINERS =================== */
    .form-container {
        background: #f7f8fa;
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 40px;
        margin: 32px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .form-title {
        font-size: 28px;
        font-weight: 600;
        color: #21242c;
        margin-bottom: 8px;
        text-align: center;
    }

    .form-subtitle {
        font-size: 16px;
        color: #626569;
        margin-bottom: 32px;
        text-align: center;
        line-height: 1.5;
    }

    /* =================== ALERTS & MESSAGES =================== */
    .stSuccess {
        background: linear-gradient(135deg, #f0f9f1 0%, #e8f5e8 100%);
        border: 2px solid #00a60e;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }

    .stError {
        background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }

    .stInfo {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }

    .stWarning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
    }

    /* =================== ACCESS CODE DISPLAY =================== */
    .access-code-container {
        background: linear-gradient(135deg, #00a60e 0%, #008a0c 100%);
        color: white;
        border-radius: 16px;
        padding: 40px;
        text-align: center;
        margin: 32px 0;
        box-shadow: 0 8px 24px rgba(0, 166, 14, 0.3);
    }

    .access-code {
        font-size: 42px;
        font-weight: 700;
        color: white;
        letter-spacing: 6px;
        font-family: 'Monaco', 'Menlo', monospace;
        margin: 20px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        padding: 16px;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        border: 2px dashed rgba(255,255,255,0.3);
    }

    .access-code-label {
        font-size: 20px;
        color: white;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .access-code-note {
        font-size: 16px;
        color: rgba(255,255,255,0.9);
        margin-top: 20px;
        line-height: 1.6;
    }

    /* =================== MILESTONE CARDS =================== */
    .milestone-card {
        border-left: 4px solid #00a60e;
        padding: 20px;
        margin: 16px 0;
        background: #ffffff;
        border-radius: 8px;
        border: 1px solid #e7e8ea;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .milestone-card:hover {
        border-color: #c4c6ca;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }

    .milestone-title {
        font-weight: 600;
        font-size: 16px;
        color: #21242c;
        margin-bottom: 8px;
    }

    .milestone-description {
        color: #626569;
        margin: 6px 0;
        line-height: 1.6;
    }

    .milestone-date {
        font-size: 14px;
        font-weight: 500;
        color: #00a60e;
    }

    /* =================== SECURITY FEATURES =================== */
    .security-features {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 24px;
        margin: 40px 0;
    }

    .security-feature {
        text-align: center;
        padding: 32px 24px;
        background: #ffffff;
        border-radius: 12px;
        border: 2px solid #e7e8ea;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .security-feature:hover {
        border-color: #00a60e;
        box-shadow: 0 8px 24px rgba(0, 166, 14, 0.1);
        transform: translateY(-2px);
    }

    .security-icon {
        font-size: 40px;
        margin-bottom: 16px;
        color: #00a60e;
    }

    .security-title {
        font-size: 18px;
        font-weight: 600;
        color: #21242c;
        margin-bottom: 8px;
    }

    .security-desc {
        font-size: 14px;
        color: #626569;
        line-height: 1.6;
    }

    /* =================== CHAT INTERFACE =================== */
    .chat-container {
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 32px;
        margin: 32px 0;
        background: #ffffff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .chat-header {
        border-bottom: 2px solid #e7e8ea;
        padding-bottom: 20px;
        margin-bottom: 24px;
    }

    .chat-title {
        font-size: 24px;
        font-weight: 600;
        color: #21242c;
        margin-bottom: 4px;
    }

    .chat-subtitle {
        font-size: 16px;
        color: #626569;
    }

    .ai-response {
        background: linear-gradient(135deg, #f7f8fa 0%, #f0f1f3 100%);
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .ai-response-header {
        font-size: 18px;
        font-weight: 600;
        color: #00a60e;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* =================== METRICS & STATS =================== */
    .metric-card {
        background: #ffffff;
        border: 2px solid #e7e8ea;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        margin-bottom: 16px;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .metric-card:hover {
        border-color: #00a60e;
        box-shadow: 0 4px 12px rgba(0, 166, 14, 0.1);
    }

    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #00a60e;
        margin-bottom: 8px;
        line-height: 1;
    }

    .metric-label {
        font-size: 14px;
        color: #626569;
        font-weight: 500;
    }

    /* =================== PROGRESS BARS =================== */
    .stProgress .stProgress-bar {
        background: linear-gradient(90deg, #00a60e 0%, #008a0c 100%);
        border-radius: 8px;
        height: 12px;
    }

    /* =================== RESPONSIVE DESIGN =================== */
    @media (max-width: 768px) {
        .header-container,
        .main-content {
            padding: 16px;
        }

        .header-container {
            flex-direction: column;
            gap: 16px;
            text-align: center;
        }

        .app-title {
            font-size: 20px;
        }

        .page-title {
            font-size: 28px;
        }

        .access-code {
            font-size: 28px;
            letter-spacing: 3px;
        }

        .security-features {
            grid-template-columns: 1fr;
            gap: 16px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0 12px;
            font-size: 14px;
        }

        .form-container {
            padding: 24px;
        }

        .family-header {
            padding: 24px;
        }
    }

    /* =================== SIDEBAR ENHANCEMENTS =================== */
    .stSidebar {
        background: #f7f8fa;
        border-right: 2px solid #e7e8ea;
    }

    .stSidebar .stSelectbox > div > div > select,
    .stSidebar .stTextInput > div > div > input {
        background: #ffffff;
        border: 2px solid #e7e8ea;
    }

    /* =================== LOADING STATES =================== */
    .stSpinner > div {
        border-top-color: #00a60e;
    }

    /* =================== CLEAN TABLES =================== */
    .stDataFrame {
        border: 2px solid #e7e8ea;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .stDataFrame thead th {
        background-color: #f7f8fa;
        color: #21242c;
        font-weight: 600;
        border-bottom: 2px solid #e7e8ea;
    }

    .stDataFrame tbody td {
        border-bottom: 1px solid #e7e8ea;
    }
</style>
""", unsafe_allow_html=True)


class SecureFamilyCareerAgent:
    def __init__(self):
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)

        if 'secure_db' not in st.session_state:
            st.session_state.secure_db = MultiFamilyDatabase()
        self.db = st.session_state.secure_db

        if 'enhanced_auth' not in st.session_state:
            st.session_state.enhanced_auth = EnhancedAuthSystem()
        self.auth_system = st.session_state.enhanced_auth


def create_clean_header():
    """Minimalist professional header"""
    st.markdown("""
    <div style="background: #ffffff; padding: 32px 0 24px 0; margin: 0;">
        <div style="max-width: 1200px; margin: 0 auto; padding: 0 24px; text-align: center;">
            <h1 style="font-size: 42px; font-weight: 600; color: #21242c; margin: 0; letter-spacing: -1px;">CareerPath</h1>
            <p style="font-size: 18px; color: #626569; margin: 8px 0 0 0; font-weight: 400;">Professional Career Guidance Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_header():
    """Backward compatibility - calls create_clean_header"""
    create_clean_header()


def create_family_login():
    """Enhanced login interface with both email/password and access code options"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Check for session validation first
    if 'family_session' in st.session_state:
        auth_system = st.session_state.enhanced_auth
        session_info = auth_system.validate_session(st.session_state.family_session)

        if session_info:
            # Valid session exists, authenticate automatically
            st.session_state.authenticated_family = {
                'id': session_info['family_id'],
                'family_name': session_info['family_name'],
                'email': session_info['email']
            }
            st.rerun()

    # Page header
    st.markdown("""
    <div class="page-title">Secure Family Access</div>
    <div class="page-subtitle">Login to your personalised career guidance dashboard</div>
    """, unsafe_allow_html=True)

    # Security features
    st.markdown("""
    <div class="security-features">
        <div class="security-feature">
            <div class="security-icon">🔒</div>
            <div class="security-title">Private & Secure</div>
            <div class="security-desc">Your family's data is encrypted and completely private</div>
        </div>
        <div class="security-feature">
            <div class="security-icon">👨‍👩‍👧‍👦</div>
            <div class="security-title">Family Only</div>
            <div class="security-desc">Only your family can access your students and conversations</div>
        </div>
        <div class="security-feature">
            <div class="security-icon">🛡️</div>
            <div class="security-title">Data Protected</div>
            <div class="security-desc">We never share your information with other families</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Login method selection
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="form-title">Access Your Family Dashboard</div>
    <div class="form-subtitle">Choose your preferred login method</div>
    """, unsafe_allow_html=True)

    # Login method tabs
    tab1, tab2 = st.tabs(["📧 Email & Password", "🔑 Access Code"])

    with tab1:
        # Email/Password Login
        st.markdown("### Login with Email & Password")

        with st.form("email_login"):
            col1, col2 = st.columns(2)

            with col1:
                email = st.text_input("Email Address", placeholder="your.email@example.com")

            with col2:
                password = st.text_input("Password", type="password")

            remember_me = st.checkbox("Remember me for 30 days")

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                email_submitted = st.form_submit_button("Login with Email", use_container_width=True)

            with col2:
                forgot_password = st.form_submit_button("Forgot Password?", use_container_width=True)

            with col3:
                pass  # Empty column for spacing

            if email_submitted and email and password:
                auth_system = st.session_state.enhanced_auth
                family_info = auth_system.authenticate_family(email, password)

                if family_info:
                    if family_info.get('email_verified', True):  # Default to True for backward compatibility
                        # Create session
                        session_duration = 30 * 24 if remember_me else 24  # hours
                        session_id = auth_system.create_session(
                            family_info['id'],
                            st.context.headers.get('user-agent', ''),
                            st.context.headers.get('x-forwarded-for', '')
                        )

                        st.session_state.family_session = session_id
                        st.session_state.authenticated_family = family_info
                        st.success(f"Welcome back, {family_info['family_name']}! 🎉")

                        # Add login analytics
                        track_login_event(family_info['id'], 'email_password')

                        st.rerun()
                    else:
                        st.warning(
                            "Please verify your email address before logging in. Check your inbox for the verification link.")
                else:
                    st.error("Invalid email or password. Please try again.")

            if forgot_password:
                st.info(
                    "Password reset functionality coming soon! For now, please use your access code or contact support.")

    with tab2:
        # Access Code Login (Backward Compatibility)
        st.markdown("### Login with Access Code")
        st.info("💡 If you registered before our email system, use your 8-character access code")

        with st.form("access_code_login"):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                access_code = st.text_input(
                    "Family Access Code",
                    placeholder="e.g., SMITH123",
                    help="The unique 8-character code for your family"
                )

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                code_submitted = st.form_submit_button("Access My Family", use_container_width=True)

            if code_submitted and access_code:
                db = st.session_state.secure_db
                family_info = db.verify_family_access(access_code.upper())

                if family_info:
                    # Create session for access code users too
                    auth_system = st.session_state.enhanced_auth
                    session_id = auth_system.create_session(family_info['id'])

                    st.session_state.family_session = session_id
                    st.session_state.authenticated_family = family_info
                    st.success(f"Welcome back, {family_info['family_name']}! 🎉")

                    # Add login analytics
                    track_login_event(family_info['id'], 'access_code')

                    st.rerun()
                else:
                    st.error("Invalid access code. Please check your code and try again.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Registration section
    st.markdown('<div class="section-title">New to CareerPath?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Join families across Australia getting professional career guidance</div>',
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Create Family Account", use_container_width=True, type="secondary"):
            st.session_state.show_registration = True
            st.rerun()

    # Show recent login stats (optional)
    show_platform_stats()

    st.markdown("</div>", unsafe_allow_html=True)


def track_login_event(family_id: str, method: str):
    """Track login events for analytics"""
    try:
        conn = sqlite3.connect("community_career_explorer.db")
        cursor = conn.cursor()

        # Create login_events table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                login_method TEXT,
                login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_agent TEXT,
                success BOOLEAN DEFAULT TRUE
            )
        ''')

        cursor.execute('''
            INSERT INTO login_events (family_id, login_method)
            VALUES (?, ?)
        ''', (family_id, method))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Login tracking error: {e}")


def show_platform_stats():
    """Show encouraging platform statistics"""
    try:
        conn = sqlite3.connect("community_career_explorer.db")
        cursor = conn.cursor()

        # Get recent stats
        cursor.execute('SELECT COUNT(*) FROM families')
        total_families = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(DISTINCT family_id) FROM conversations 
            WHERE timestamp >= date('now', '-7 days')
        ''')
        active_this_week = cursor.fetchone()[0]

        conn.close()

        if total_families > 0:
            st.markdown("---")
            st.markdown("### 📊 Join the CareerPath Community")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Families Registered", total_families)

            with col2:
                st.metric("Students Guided", total_students)

            with col3:
                st.metric("Active This Week", active_this_week)

    except Exception as e:
        pass  # Silently fail if tables don't exist yet


def create_family_registration():
    """Enhanced family registration with email verification"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Create Your Family Account</div>
    <div class="page-subtitle">Join thousands of Australian families getting AI-powered career guidance</div>
    """, unsafe_allow_html=True)

    # Show benefits
    st.markdown("""
    <div class="features-grid">
        <div class="feature-item">🎯 Personalised AI Career Guidance</div>
        <div class="feature-item">📊 Live Australian Employment Data</div>
        <div class="feature-item">🎓 Canvas LMS Integration</div>
        <div class="feature-item">👨‍👩‍👧‍👦 Multi-Student Family Support</div>
        <div class="feature-item">🔒 Secure & Private</div>
        <div class="feature-item">🆓 Completely Free to Use</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)

    # Registration method selection
    registration_method = st.radio(
        "Choose Registration Method",
        ["📧 Email & Password (Recommended)", "🔑 Access Code Only (Legacy)"],
        help="Email registration provides better security and password recovery options"
    )

    if registration_method.startswith("📧"):
        # Enhanced email registration
        with st.form("enhanced_family_registration"):
            st.markdown('<div class="section-title">👨‍👩‍👧‍👦 Family Information</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
                email = st.text_input("Email Address *", placeholder="your.email@example.com")

            with col2:
                password = st.text_input("Password *", type="password",
                                         help="Minimum 8 characters, include letters and numbers")
                confirm_password = st.text_input("Confirm Password *", type="password")
                location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

            st.markdown('<div class="section-title">🎓 First Student</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
                age = st.number_input("Age", min_value=14, max_value=20, value=16)
                year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

            with col2:
                interests = st.text_area("Interests", placeholder="e.g., psychology, science, helping others")
                timeline = st.selectbox("University Timeline",
                                        ["Applying in 2+ years", "Applying in 12 months",
                                         "Applying in 6 months", "Applying now"])
                location_preference = st.text_input("Study Location Preference", placeholder="e.g., NSW/ACT")

            # Additional student fields
            st.markdown('<div class="section-title">📋 Additional Details (Optional)</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                career_considerations = st.text_area("Career Considerations",
                                                     placeholder="e.g., work-life balance, salary expectations, travel opportunities")
            with col2:
                goals = st.text_area("Goals",
                                     placeholder="e.g., find course with practical components, explore internship opportunities")

            # Terms and newsletter
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                terms_accepted = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
                newsletter = st.checkbox("Send me updates about new features and career insights")

            with col2:
                # Show password requirements
                st.markdown("""
                **Password Requirements:**
                - At least 8 characters
                - Include letters and numbers
                - Avoid common passwords
                """)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submitted = st.form_submit_button("Create Family Account", use_container_width=True)

            if submitted:
                # Enhanced validation
                errors = []

                if not all([family_name, email, password, confirm_password, student_name]):
                    errors.append("❌ Please fill in all required fields.")

                if password != confirm_password:
                    errors.append("❌ Passwords do not match.")

                if len(password) < 8:
                    errors.append("❌ Password must be at least 8 characters long.")

                if not any(c.isdigit() for c in password):
                    errors.append("❌ Password must include at least one number.")

                if not any(c.isalpha() for c in password):
                    errors.append("❌ Password must include at least one letter.")

                if '@' not in email or '.' not in email:
                    errors.append("❌ Please enter a valid email address.")

                if not terms_accepted:
                    errors.append("❌ Please accept the Terms of Service.")

                # Check if email already exists
                if not errors:
                    try:
                        conn = sqlite3.connect("community_career_explorer.db")
                        cursor = conn.cursor()
                        cursor.execute('SELECT id FROM families WHERE email = ?', (email,))
                        if cursor.fetchone():
                            errors.append("❌ An account with this email already exists. Try logging in instead.")
                        conn.close()
                    except Exception as e:
                        errors.append("❌ Database error. Please try again.")

                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Create enhanced account
                    try:
                        auth_system = st.session_state.enhanced_auth
                        result = auth_system.register_family_with_password(
                            family_name, email, password, location
                        )

                        if result['status'] == 'success':
                            family_id = result['family_id']
                            access_code = result['access_code']

                            # Add the first student
                            db = st.session_state.secure_db
                            student_data = {
                                'name': student_name,
                                'age': age,
                                'year_level': year_level,
                                'interests': [i.strip() for i in interests.split(',') if i.strip()],
                                'preferences': [],
                                'timeline': timeline,
                                'location_preference': location_preference,
                                'career_considerations': [c.strip() for c in career_considerations.split(',') if
                                                          c.strip()] if career_considerations else [],
                                'goals': [g.strip() for g in goals.split(',') if g.strip()] if goals else []
                            }

                            db.add_student(family_id, student_data)

                            # Success message with both email and access code
                            st.success("🎉 Family account created successfully!")

                            st.markdown(f"""
                            <div class="access-code-container">
                                <div class="access-code-label">Your Family Access Details</div>
                                <div style="background: white; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                                    <strong>Email:</strong> {email}<br>
                                    <strong>Backup Access Code:</strong> <span class="access-code" style="font-size: 24px;">{access_code}</span>
                                </div>
                                <div class="access-code-note">
                                    📧 <strong>Check your email</strong> for a verification link<br>
                                    🔑 <strong>Save your access code</strong> as a backup login method<br>
                                    🛡️ <strong>Keep these details secure</strong> - they're your keys to the platform
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Auto-login option
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                if st.button("Continue to Dashboard", use_container_width=True, type="primary"):
                                    # Auto-authenticate the newly created family
                                    session_id = auth_system.create_session(family_id)
                                    st.session_state.family_session = session_id
                                    st.session_state.authenticated_family = {
                                        'id': family_id,
                                        'family_name': family_name,
                                        'email': email,
                                        'location': location,
                                        'access_code': access_code
                                    }

                                    if 'show_registration' in st.session_state:
                                        del st.session_state.show_registration

                                    st.rerun()
                        else:
                            st.error("Registration failed. Please try again.")

                    except Exception as e:
                        st.error(f"An error occurred during registration: {str(e)}")

    else:
        # Legacy access code only registration
        st.info("🔑 Legacy registration method - you'll only get an access code (no password recovery)")

        with st.form("legacy_registration"):
            col1, col2 = st.columns(2)

            with col1:
                family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
                email = st.text_input("Email Address (Optional)", placeholder="your.email@example.com")

            with col2:
                location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

            st.markdown("### First Student")
            # ... (same student fields as above)

            submitted = st.form_submit_button("Create Account (Access Code Only)")

            if submitted and family_name:
                # Use original database method
                db = st.session_state.secure_db
                family_id, access_code = db.create_family(family_name, email, location)

                st.success("Account created!")
                st.markdown(f"""
                <div class="access-code-container">
                    <div class="access-code-label">Your Family Access Code</div>
                    <div class="access-code">{access_code}</div>
                    <div class="access-code-note">Save this code securely - it's your only way to access your account!</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Login", use_container_width=True, type="secondary"):
            if 'show_registration' in st.session_state:
                del st.session_state.show_registration
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_authenticated_family_interface(family_info):
    """Enhanced authenticated family interface"""
    if 'family_session' in st.session_state:
        auth_system = st.session_state.enhanced_auth
        session_info = auth_system.validate_session(st.session_state.family_session)

        if not session_info:
            # Session expired, clear and redirect to login
            if 'family_session' in st.session_state:
                del st.session_state.family_session
            if 'authenticated_family' in st.session_state:
                del st.session_state.authenticated_family
            st.warning("Your session has expired. Please log in again.")
            st.rerun()

    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Family header with enhanced info
    col1, col2 = st.columns([4, 1])

    with col1:
        # Show email if available, otherwise show access code
        contact_info = family_info.get('email', f"Access Code: {family_info.get('access_code', 'N/A')}")

        st.markdown(f"""
            <div class="family-header">
                <div class="family-title">Welcome, {family_info['family_name']} 👨‍👩‍👧‍👦</div>
                <div class="family-details">{contact_info} | {family_info.get('location', 'Location not set')}</div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            # Enhanced logout - clear session from database
            if 'family_session' in st.session_state:
                try:
                    auth_system = st.session_state.enhanced_auth
                    conn = sqlite3.connect(auth_system.db_path)
                    cursor = conn.cursor()
                    cursor.execute(
                        'UPDATE user_sessions SET is_active = FALSE WHERE id = ?',
                        (st.session_state.family_session,)
                    )
                    conn.commit()
                    conn.close()
                except:
                    pass  # Silently fail if session doesn't exist

                del st.session_state.family_session

            if 'authenticated_family' in st.session_state:
                del st.session_state.authenticated_family

            st.success("Logged out successfully!")
            st.rerun()

    create_clean_header()

    st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 24px; background: #ffffff;">', unsafe_allow_html=True)

    # Family header
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
        <div class="family-header">
            <div class="family-title">Welcome, {family_info['family_name']}</div>
            <div class="family-details">Family Code: {family_info['access_code']} | {family_info['email']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("Logout", use_container_width=True, type="secondary"):
            del st.session_state.authenticated_family
            st.rerun()

    # Get students
    db = st.session_state.secure_db
    students = db.get_family_students(family_info['id'])

    if not students:
        st.info("No students found. Contact support to add students to your family account.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Tab navigation
    tab1, tab2, tab3, tab4 = st.tabs(
        ["👥 Students & Career Guidance", "📚 Canvas LMS Integration", "📊 Progress & Reports", "⚙️ Family Settings"])

    with tab1:
        show_students_and_career_tab(students, family_info, db)

    with tab2:
        show_full_canvas_integration_tab(students)  # Changed from show_canvas_integration_tab

    with tab3:
        show_progress_and_reports_tab(students, family_info)

    with tab4:
        show_family_settings_tab(family_info, students)

    st.markdown("</div>", unsafe_allow_html=True)


def show_students_and_career_tab(students, family_info, db):
    """Show students and career guidance"""
    st.markdown('<div class="section-title">Your Students</div>', unsafe_allow_html=True)

    for student in students:
        st.markdown(f"""
        <div class="student-card">
            <div class="student-name">{student['name']} - Year {student['year_level']}</div>
            <div class="student-details">
                Age: {student['age']} | Interests: {', '.join(student['interests'][:3]) if student['interests'] else 'None specified'}<br>
                Timeline: {student['timeline']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"Start Career Guidance for {student['name']}",
                     key=f"student_{student['id']}", use_container_width=True):
            st.session_state.selected_student = student
            st.rerun()

    # Chat interface
    if 'selected_student' in st.session_state:
        student = st.session_state.selected_student

        st.markdown("---")
        st.markdown(f"""
        <div class="chat-container">
            <div class="chat-header">
                <div class="chat-title">Career Guidance for {student['name']}</div>
                <div class="chat-subtitle">AI-powered career counselling with live Australian employment data</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        user_input = st.text_area(
            "Ask your career question:",
            placeholder=f"What career opportunities align with {student['name']}'s interests? What are the current job prospects?",
            height=100
        )

        if st.button("Get Career Guidance", use_container_width=True):
            if user_input:
                st.markdown("""
                <div class="ai-response">
                    <div class="ai-response-header">🤖 AI Career Counsellor</div>
                """, unsafe_allow_html=True)

                st.write(f"""
                **Career Guidance for {student['name']}:**

                Based on {student['name']}'s interests in **{', '.join(student['interests']) if student['interests'] else 'their chosen fields'}** and current Australian employment data:

                **Recommended Career Pathways:**
                - Analysis of careers matching their interests
                - Current employment prospects and salary ranges
                - University course recommendations

                **Next Steps:**
                1. Research recommended universities and courses
                2. Plan application timeline
                3. Schedule follow-up guidance session

                *Powered by live Australian government employment data.*
                """)

                st.markdown("</div>", unsafe_allow_html=True)

                # Save conversation
                db.save_conversation(family_info['id'], student['id'], student['name'],
                                     user_input, "AI career guidance response", ['career_guidance'])

                st.success("Career guidance session saved to your family records.")


def show_progress_and_reports_tab(students, family_info):
    """Show progress tracking and reports"""
    st.markdown('<div class="section-title">📊 Progress Tracking & Reports</div>', unsafe_allow_html=True)

    for student in students:
        st.markdown(f"### 📈 {student['name']}'s Progress")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">5</div>
                <div class="metric-label">Career Sessions</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">3</div>
                <div class="metric-label">Universities Explored</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">8</div>
                <div class="metric-label">Career Paths Identified</div>
            </div>
            """, unsafe_allow_html=True)

        # Recent milestones
        st.markdown("#### 🎯 Recent Progress")
        st.markdown("""
        <div class="milestone-card">
            <div class="milestone-title">University Research Completed</div>
            <div class="milestone-description">Explored 3 universities matching interests</div>
            <div class="milestone-date">2 days ago</div>
        </div>
        """, unsafe_allow_html=True)

        if len(students) > 1:
            st.markdown("---")


def show_family_settings_tab(family_info, students):
    """Show family settings and management"""
    st.markdown('<div class="section-title">⚙️ Family Settings</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Family Information")
        st.text_input("Family Name", value=family_info['family_name'], disabled=True)
        st.text_input("Email", value=family_info['email'], disabled=True)
        st.text_input("Location", value=family_info.get('location', ''), disabled=True)

    with col2:
        st.markdown("#### Account Details")
        st.text_input("Access Code", value=family_info['access_code'], disabled=True)
        st.text_input("Students", value=f"{len(students)} students", disabled=True)

    st.markdown("#### Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Add New Student", use_container_width=True):
            st.info("Contact support to add additional students to your family account.")

    with col2:
        if st.button("Download Reports", use_container_width=True):
            st.info("Report generation feature coming soon!")

    with col3:
        if st.button("Contact Support", use_container_width=True):
            st.info("Support: support@careerpath.edu.au")


def show_full_canvas_integration_tab(students):
    """Show FULL Canvas LMS integration with complete functionality"""
    st.markdown('<div class="section-title">📚 Canvas LMS Integration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Connect your students\' Canvas accounts to sync assignments, exams, and generate AI study plans</div>',
        unsafe_allow_html=True)

    # Initialize Canvas integrator in session state
    if 'canvas_integrator' not in st.session_state:
        st.session_state.canvas_integrator = CanvasIntegrator()

    canvas_integrator = st.session_state.canvas_integrator

    for student in students:
        st.markdown(f"### 📚 {student['name']} - Canvas Integration")

        # Use the full Canvas setup from canvas_integration.py
        show_canvas_setup(student, canvas_integrator)

        if len(students) > 1:
            st.markdown("---")


def main():
    """Main application with clean design"""

    def main():
        """Main application with clean design"""

        # Force remove Streamlit spacing
        st.markdown("""
        <style>
        .block-container {
            padding-top: 0rem !important;
            margin-top: 0rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        # Initialize session state
        if 'secure_agent' not in st.session_state:
            st.session_state.secure_agent = SecureFamilyCareerAgent()

        # Enhanced authentication flow
        if 'authenticated_family' not in st.session_state:
            # Check for existing session first
            if 'family_session' in st.session_state:
                auth_system = st.session_state.enhanced_auth
                session_info = auth_system.validate_session(st.session_state.family_session)

                if session_info:
                    # Valid session found, auto-authenticate
                    st.session_state.authenticated_family = {
                        'id': session_info['family_id'],
                        'family_name': session_info['family_name'],
                        'email': session_info.get('email', ''),
                        'location': '',  # You might want to fetch this from the database
                    }

            # Show appropriate interface
            if 'authenticated_family' not in st.session_state:
                if 'show_registration' in st.session_state:
                    create_family_registration()
                else:
                    create_family_login()
            else:
                create_authenticated_family_interface(st.session_state.authenticated_family)
        else:
            create_authenticated_family_interface(st.session_state.authenticated_family)


def handle_email_verification():
    """Handle email verification from URL parameters"""
    # This function would handle email verification tokens
    # You'd typically call this from your main function if you detect verification parameters

    # Get URL parameters (Streamlit doesn't have built-in URL parameter support,
    # but you can implement this if needed)

    # For now, create a simple verification interface
    if st.sidebar.button("🔍 Verify Email"):
        st.markdown("### Email Verification")

        verification_token = st.text_input("Enter verification token from your email:")

        if st.button("Verify Email"):
            if verification_token:
                try:
                    auth_system = st.session_state.enhanced_auth
                    conn = sqlite3.connect(auth_system.db_path)
                    cursor = conn.cursor()

                    # Check token validity
                    cursor.execute('''
                        SELECT family_id FROM email_verification_tokens 
                        WHERE token = ? AND expires_at > ? AND used = FALSE
                    ''', (verification_token, datetime.now()))

                    result = cursor.fetchone()

                    if result:
                        family_id = result[0]

                        # Mark email as verified
                        cursor.execute('''
                            UPDATE families SET email_verified = TRUE WHERE id = ?
                        ''', (family_id,))

                        # Mark token as used
                        cursor.execute('''
                            UPDATE email_verification_tokens SET used = TRUE WHERE token = ?
                        ''', (verification_token,))

                        conn.commit()
                        conn.close()

                        st.success("✅ Email verified successfully! You can now log in.")

                        # Clear verification state
                        time.sleep(2)
                        st.rerun()

                    else:
                        st.error("Invalid or expired verification token.")
                        conn.close()

                except Exception as e:
                    st.error(f"Verification failed: {str(e)}")
            else:
                st.warning("Please enter your verification token.")
if __name__ == "__main__":
    main()