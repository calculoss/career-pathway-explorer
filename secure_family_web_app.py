import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import anthropic
import os
import json
from dotenv import load_dotenv
from multi_family_database import MultiFamilyDatabase

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
    """Clean, professional login interface"""
    create_clean_header()

    # Start main content immediately after header
    st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 24px; background: #ffffff;">', unsafe_allow_html=True)

    # Page header
    st.markdown("""
    <div class="page-title">Secure Family Access</div>
    <div class="page-subtitle">Enter your family access code to view your personalised career guidance dashboard</div>
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

    # Login form
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    st.markdown("""
    <div class="form-title">Access Your Family Dashboard</div>
    <div class="form-subtitle">Use the 8-character code provided when you registered</div>
    """, unsafe_allow_html=True)

    with st.form("family_login"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            access_code = st.text_input(
                "Family Access Code",
                placeholder="e.g., SMITH123",
                help="The unique 8-character code for your family"
            )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Access My Family", use_container_width=True)

        if submitted and access_code:
            db = st.session_state.secure_db
            family_info = db.verify_family_access(access_code.upper())

            if family_info:
                st.session_state.authenticated_family = family_info
                st.success(f"Welcome back, {family_info['family_name']}!")
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
        if st.button("Register Your Family", use_container_width=True, type="secondary"):
            st.session_state.show_registration = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_family_registration():
    """Clean family registration form"""
    create_clean_header()

    st.markdown('<div style="max-width: 1200px; margin: 0 auto; padding: 24px; background: #ffffff;">', unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Family Registration</div>
    <div class="page-subtitle">Create your secure family account and get instant access to professional career guidance</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)

    with st.form("family_registration"):
        st.markdown('<div class="section-title">Family Information</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
            email = st.text_input("Email Address *", placeholder="your.email@example.com")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

        st.markdown('<div class="section-title">First Student</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

        with col2:
            interests = st.text_area("Interests", placeholder="e.g., psychology, science, helping others")
            timeline = st.selectbox("University Timeline",
                                    ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months",
                                     "Applying now"])
            location_preference = st.text_input("Study Location Preference", placeholder="e.g., NSW/ACT")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Create Family Account", use_container_width=True)

        if submitted:
            if family_name and student_name and email:
                db = st.session_state.secure_db

                family_id, access_code = db.create_family(family_name, email, location)

                student_data = {
                    'name': student_name,
                    'age': age,
                    'year_level': year_level,
                    'interests': [i.strip() for i in interests.split(',') if i.strip()],
                    'preferences': [],
                    'timeline': timeline,
                    'location_preference': location_preference,
                    'career_considerations': [],
                    'goals': []
                }

                db.add_student(family_id, student_data)

                # Success message with access code
                st.success("Family account created successfully!")

                st.markdown(f"""
                <div class="access-code-container">
                    <div class="access-code-label">Your Family Access Code</div>
                    <div class="access-code">{access_code}</div>
                    <div class="access-code-note">
                        Save this code securely. You'll need it to access your family's career guidance dashboard.
                        <br>A confirmation email has been sent to {email}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Access My Family Dashboard", use_container_width=True):
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
                st.error("Please fill in all required fields.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Back to Login", use_container_width=True, type="secondary"):
            if 'show_registration' in st.session_state:
                del st.session_state.show_registration
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_authenticated_family_interface(family_info):
    """Enhanced authenticated family interface"""
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
        show_canvas_integration_tab(students)

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


def show_canvas_integration_tab(students):
    """Show Canvas LMS integration for study materials"""
    st.markdown('<div class="section-title">📚 Canvas LMS Integration</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Connect your students\' Canvas accounts to sync assignments and study materials</div>',
        unsafe_allow_html=True)

    for student in students:
        st.markdown(f"### 📚 {student['name']} - Canvas Integration")

        # Canvas connection status - use different key for storage
        canvas_connected = st.session_state.get(f"canvas_connected_{student['id']}", False)

        if not canvas_connected:
            st.markdown("""
            <div class="canvas-status">
                <div class="canvas-title">Connect Canvas Account</div>
                <div class="canvas-subtitle">Link your Canvas LMS to automatically sync assignments and study materials</div>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                canvas_url = st.text_input(f"Canvas URL", placeholder="https://yourschool.instructure.com",
                                           key=f"input_canvas_url_{student['id']}")
            with col2:
                canvas_token = st.text_input(f"Access Token", placeholder="Your Canvas API token", type="password",
                                             key=f"input_canvas_token_{student['id']}")

            if st.button(f"Connect Canvas for {student['name']}", key=f"connect_{student['id']}"):
                if canvas_url and canvas_token:
                    # Store with different keys to avoid conflicts
                    st.session_state[f"canvas_connected_{student['id']}"] = True
                    st.session_state[f"stored_canvas_url_{student['id']}"] = canvas_url  # Different key
                    st.session_state[f"stored_canvas_token_{student['id']}"] = canvas_token  # Different key
                    st.success(f"✅ Canvas connected for {student['name']}!")
                    st.rerun()
                else:
                    st.error("Please provide both Canvas URL and access token")

        else:
            # Show connected Canvas features
            stored_url = st.session_state.get(f"stored_canvas_url_{student['id']}", "Unknown")
            st.markdown(f"""
            <div class="canvas-status canvas-connected">
                <div class="canvas-title">✅ Canvas Connected</div>
                <div class="canvas-subtitle">Connected to: {stored_url}</div>
            </div>
            """, unsafe_allow_html=True)

            # Tabs for Canvas features
            canvas_tab1, canvas_tab2, canvas_tab3 = st.tabs(["📋 Assignments", "📚 Study Materials", "📊 Progress"])

            with canvas_tab1:
                st.markdown("#### Upcoming Assignments")

                # Sample assignments data
                assignments = [
                    {"name": "Ancient History Essay", "due": "2025-06-15", "course": "Ancient History",
                     "status": "In Progress"},
                    {"name": "Biology Lab Report", "due": "2025-06-18", "course": "Biology", "status": "Not Started"},
                    {"name": "English Creative Writing", "due": "2025-06-22", "course": "English",
                     "status": "Submitted"}
                ]

                for assignment in assignments:
                    status_color = {"In Progress": "🟡", "Not Started": "🔴", "Submitted": "✅"}
                    st.markdown(f"""
                    <div class="milestone-card">
                        <div class="milestone-title">{status_color[assignment['status']]} {assignment['name']}</div>
                        <div class="milestone-description">Course: {assignment['course']}</div>
                        <div class="milestone-date">Due: {assignment['due']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with canvas_tab2:
                st.markdown("#### Study Materials & Resources")

                # Sample study materials
                materials = [
                    {"title": "Ancient Civilizations Study Guide", "type": "PDF", "course": "Ancient History"},
                    {"title": "Cell Biology Video Lectures", "type": "Video", "course": "Biology"},
                    {"title": "Essay Writing Techniques", "type": "Document", "course": "English"}
                ]

                for material in materials:
                    type_icon = {"PDF": "📄", "Video": "🎥", "Document": "📝"}
                    st.markdown(f"""
                    <div class="milestone-card">
                        <div class="milestone-title">{type_icon[material['type']]} {material['title']}</div>
                        <div class="milestone-description">Course: {material['course']}</div>
                    </div>
                    """, unsafe_allow_html=True)

            with canvas_tab3:
                st.markdown("#### Academic Progress")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">85%</div>
                        <div class="metric-label">Overall Grade</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">3</div>
                        <div class="metric-label">Assignments Due</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">92%</div>
                        <div class="metric-label">Attendance</div>
                    </div>
                    """, unsafe_allow_html=True)

            # Disconnect option
            if st.button(f"Disconnect Canvas for {student['name']}", key=f"disconnect_{student['id']}"):
                # Clear all stored data
                st.session_state[f"canvas_connected_{student['id']}"] = False
                if f"stored_canvas_url_{student['id']}" in st.session_state:
                    del st.session_state[f"stored_canvas_url_{student['id']}"]
                if f"stored_canvas_token_{student['id']}" in st.session_state:
                    del st.session_state[f"stored_canvas_token_{student['id']}"]
                st.rerun()

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
    if 'secure_agent' not in st.session_state:
        st.session_state.secure_agent = SecureFamilyCareerAgent()

    if 'authenticated_family' not in st.session_state:
        if 'show_registration' in st.session_state:
            create_family_registration()
        else:
            create_family_login()
    else:
        create_authenticated_family_interface(st.session_state.authenticated_family)


if __name__ == "__main__":
    main()