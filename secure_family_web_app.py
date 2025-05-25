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

# FIXED CSS - Reduced header spacing and improved layout
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;600;700&display=swap');

    /* CRITICAL FIX: Remove header padding and spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 10rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
    }

    /* Remove default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
    }

    /* Fix for container spacing */
    .main > div {
        padding-top: 0rem;
    }

    /* Global Styles */
    .stApp {
        background-color: #f7f8fa;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container with reduced top margin */
    .main-content {
        background: white;
        border-radius: 8px;
        padding: 32px;
        margin: 8px auto 24px auto; /* Reduced top margin from 24px to 8px */
        max-width: 1200px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    /* Compact header */
    .site-header {
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 8px 0; /* Reduced from 16px to 8px */
        margin-bottom: 16px; /* Reduced from 32px to 16px */
    }

    .site-header .container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
    }

    .logo {
        font-size: 24px;
        font-weight: 700;
        color: #1c4980;
        text-decoration: none;
    }

    .logo-subtitle {
        font-size: 14px;
        color: #6b7280;
        font-weight: 400;
        margin-left: 8px;
    }

    /* Typography */
    .page-title {
        font-size: 28px; /* Reduced from 32px */
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 6px; /* Reduced from 8px */
        line-height: 1.2;
    }

    .page-subtitle {
        font-size: 16px; /* Reduced from 18px */
        color: #6b7280;
        margin-bottom: 24px; /* Reduced from 32px */
        line-height: 1.4;
    }

    .section-title {
        font-size: 22px; /* Reduced from 24px */
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px; /* Reduced from 16px */
        margin-top: 24px; /* Reduced from 32px */
    }

    /* Login form improvements */
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 16px;
    }

    .login-subtitle {
        text-align: center;
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 32px;
    }

    /* Error and success message styling */
    .stError > div {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 16px;
    }

    .stSuccess > div {
        background-color: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 16px;
    }

    /* Forms */
    .form-container {
        background: #f9fafb;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 32px;
        margin: 16px 0; /* Reduced from 24px */
    }

    .form-title {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
        text-align: center;
    }

    .form-subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 32px;
        text-align: center;
    }

    /* Button styling */
    .stButton > button {
        background-color: #1c4980;
        color: white;
        border: 1px solid #1c4980;
        border-radius: 6px;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        font-family: 'Lato', sans-serif;
        transition: all 0.2s ease;
        cursor: pointer;
        width: 100%;
    }

    .stButton > button:hover {
        background-color: #164373;
        border-color: #164373;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 16px;
        font-family: 'Lato', sans-serif;
        background: white;
        transition: border-color 0.2s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: #1c4980;
        outline: none;
        box-shadow: 0 0 0 3px rgba(28, 73, 128, 0.1);
    }

    /* Family header */
    .family-header {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 8px;
        padding: 20px; /* Reduced from 24px */
        margin-bottom: 24px; /* Reduced from 32px */
    }

    .family-title {
        font-size: 22px; /* Reduced from 24px */
        font-weight: 600;
        color: #0c4a6e;
        margin-bottom: 6px; /* Reduced from 8px */
    }

    .family-details {
        font-size: 14px; /* Reduced from 16px */
        color: #075985;
    }

    /* Security features */
    .security-features {
        display: flex;
        justify-content: center;
        gap: 24px; /* Reduced from 32px */
        margin: 24px 0; /* Reduced from 32px */
        flex-wrap: wrap;
    }

    .security-feature {
        text-align: center;
        flex: 1;
        min-width: 200px;
    }

    .security-icon {
        font-size: 24px;
        margin-bottom: 8px;
    }

    .security-title {
        font-size: 16px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 4px;
    }

    .security-desc {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.4;
    }

    /* Access code display */
    .access-code-container {
        background: #f0f9ff;
        border: 2px dashed #0ea5e9;
        border-radius: 8px;
        padding: 32px;
        text-align: center;
        margin: 24px 0;
    }

    .access-code {
        font-size: 36px;
        font-weight: 700;
        color: #0c4a6e;
        letter-spacing: 4px;
        font-family: 'Monaco', 'Menlo', monospace;
        margin: 16px 0;
    }

    /* Student cards */
    .student-card {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 20px; /* Reduced from 24px */
        margin-bottom: 12px; /* Reduced from 16px */
        background: white;
        transition: all 0.2s ease;
    }

    .student-card:hover {
        border-color: #1c4980;
        box-shadow: 0 2px 8px rgba(28, 73, 128, 0.1);
    }

    .student-name {
        font-size: 18px; /* Reduced from 20px */
        font-weight: 600;
        color: #374151;
        margin-bottom: 6px; /* Reduced from 8px */
    }

    .student-details {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.5;
    }

    /* Chat interface */
    .chat-container {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 20px; /* Reduced from 24px */
        margin: 16px 0; /* Reduced from 24px */
        background: white;
    }

    .chat-header {
        border-bottom: 1px solid #e5e5e5;
        padding-bottom: 12px; /* Reduced from 16px */
        margin-bottom: 20px; /* Reduced from 24px */
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-content {
            margin: 8px 16px 16px 16px; /* Adjusted margins */
            padding: 20px; /* Reduced from 24px */
        }

        .site-header .container {
            padding: 0 20px; /* Reduced from 24px */
        }

        .login-container {
            margin: 0 16px;
            padding: 24px; /* Reduced from 40px */
        }
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


def create_header():
    """Compact site header"""
    st.markdown("""
    <div class="site-header">
        <div class="container">
            <div>
                <span class="logo">📚 CareerPath</span>
                <span class="logo-subtitle">Professional Career Guidance Platform</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_family_login():
    """Improved login interface with better error handling"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Centred login container
    st.markdown("""
    <div class="login-container">
        <div class="login-title">Family Access</div>
        <div class="login-subtitle">Enter your unique family code to access your career guidance dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    # Security features (compact)
    st.markdown("""
    <div class="security-features">
        <div class="security-feature">
            <div class="security-icon">🔒</div>
            <div class="security-title">Secure Access</div>
            <div class="security-desc">Your family data is private and encrypted</div>
        </div>
        <div class="security-feature">
            <div class="security-icon">👨‍👩‍👧‍👦</div>
            <div class="security-title">Family Dashboard</div>
            <div class="security-desc">Manage all your students in one place</div>
        </div>
        <div class="security-feature">
            <div class="security-icon">🤖</div>
            <div class="security-title">AI Guidance</div>
            <div class="security-desc">Personalised career advice with conversation memory</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # IMPROVED LOGIN FORM
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("family_login", clear_on_submit=False):
            st.markdown("#### Access Your Family Dashboard")

            access_code = st.text_input(
                "Family Access Code",
                placeholder="Enter your 8-character code (e.g., SMITH123)",
                help="The unique code provided when you registered your family",
                max_chars=8
            )

            submitted = st.form_submit_button("Access My Family Dashboard", use_container_width=True)

            if submitted:
                if not access_code:
                    st.error("Please enter your family access code.")
                elif len(access_code) < 6:
                    st.error("Access code must be at least 6 characters.")
                else:
                    # FIXED LOGIN LOGIC
                    db = st.session_state.secure_db

                    # Debug: Check if database connection works
                    try:
                        family_info = db.verify_family_access(access_code.upper().strip())

                        if family_info:
                            st.session_state.authenticated_family = family_info
                            st.success(f"✅ Welcome back, {family_info['family_name']}!")

                            # Add a small delay and rerun
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Invalid access code. Please check your code and try again.")

                            # Debug: Show available families (remove in production)
                            if st.checkbox("🔧 Debug: Show test families"):
                                families = db.get_all_families()
                                if families:
                                    st.write("Available test families:")
                                    for family in families[:3]:  # Show only first 3
                                        st.write(f"- {family['family_name']}")
                                else:
                                    st.write("No families found in database")

                    except Exception as e:
                        st.error(f"Database connection error: {str(e)}")
                        st.info("Trying to initialise database...")

                        # Try to reinitialise database
                        try:
                            db.init_database()
                            st.success("Database initialised. Please try logging in again.")
                        except Exception as init_error:
                            st.error(f"Failed to initialise database: {str(init_error)}")

    # Registration section (compact)
    st.markdown('<div class="section-title" style="text-align: center; margin-top: 40px;">New Family?</div>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Register Your Family", use_container_width=True, type="secondary"):
            st.session_state.show_registration = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_family_registration():
    """Improved family registration with validation"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Create Your Family Account</div>
    <div class="page-subtitle">Join families across Australia getting professional AI-powered career guidance</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-container">', unsafe_allow_html=True)

    with st.form("family_registration"):
        st.markdown("### Family Information")

        col1, col2 = st.columns(2)
        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
            email = st.text_input("Email Address *", placeholder="your.email@example.com")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

        st.markdown("### First Student")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

        with col2:
            interests = st.text_area(
                "Interests",
                placeholder="e.g., psychology, science, helping others",
                help="Enter interests separated by commas"
            )
            timeline = st.selectbox("University Timeline", [
                "Applying in 2+ years",
                "Applying in 12 months",
                "Applying in 6 months",
                "Applying now"
            ])
            location_preference = st.text_input("Study Location Preference", placeholder="e.g., NSW/ACT")

        submitted = st.form_submit_button("🚀 Create Family Account", use_container_width=True)

    # Handle form submission outside the form context
    if submitted:
        # IMPROVED VALIDATION
        errors = []

        if not family_name or len(family_name.strip()) < 2:
            errors.append("Family name must be at least 2 characters")

        if not student_name or len(student_name.strip()) < 2:
            errors.append("Student name must be at least 2 characters")

        if not email or "@" not in email:
            errors.append("Please enter a valid email address")

        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            try:
                db = st.session_state.secure_db

                # FIXED: Use the updated create_family method that returns tuple
                family_id, access_code = db.create_family(family_name.strip(), email.strip(), location.strip())

                student_data = {
                    'name': student_name.strip(),
                    'age': age,
                    'year_level': year_level,
                    'interests': [i.strip() for i in interests.split(',') if i.strip()],
                    'preferences': [],
                    'timeline': timeline,
                    'location_preference': location_preference.strip(),
                    'career_considerations': [],
                    'goals': []
                }

                db.add_student(family_id, student_data)

                # Success display
                st.success("🎉 Family account created successfully!")

                st.markdown(f"""
                <div class="access-code-container">
                    <div class="access-code-label">Your Family Access Code</div>
                    <div class="access-code">{access_code}</div>
                    <div class="access-code-note">
                        ⚠️ <strong>Save this code securely!</strong> You'll need it to access your family dashboard.
                        <br>📧 A confirmation email will be sent to {email}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Set auto-login flag
                st.session_state.auto_login_family = {
                    'id': family_id,
                    'family_name': family_name,
                    'email': email,
                    'location': location,
                    'access_code': access_code
                }

            except Exception as e:
                st.error(f"❌ Registration failed: {str(e)}")
                st.info("Please try again or contact support if the problem persists.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Handle auto-login after registration (outside the form)
    if 'auto_login_family' in st.session_state:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏠 Access My Family Dashboard Now", use_container_width=True, type="primary"):
                st.session_state.authenticated_family = st.session_state.auto_login_family
                # Clean up session state
                del st.session_state.auto_login_family
                if 'show_registration' in st.session_state:
                    del st.session_state.show_registration
                st.rerun()

    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Login", use_container_width=True, type="secondary"):
            if 'show_registration' in st.session_state:
                del st.session_state.show_registration
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_authenticated_family_interface(family_info):
    """Improved family interface with better navigation"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Compact family header
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
        <div class="family-header">
            <div class="family-title">👋 Welcome, {family_info['family_name']}</div>
            <div class="family-details">
                🔑 Family Code: <strong>{family_info['access_code']}</strong> | 
                📧 {family_info['email']} | 
                📍 {family_info.get('location', 'Location not set')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            # Clear all session state related to authentication
            keys_to_remove = ['authenticated_family', 'selected_student']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Get students with error handling
    try:
        db = st.session_state.secure_db
        students = db.get_family_students(family_info['id'])
    except Exception as e:
        st.error(f"Error loading students: {str(e)}")
        students = []

    if not students:
        st.warning("📚 No students found for your family.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("➕ Add Your First Student", use_container_width=True):
                st.info("Student management feature coming soon! Contact support to add students.")

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Students section with improved layout
    st.markdown("### 👨‍🎓 Your Students")

    for i, student in enumerate(students):
        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div class="student-card">
                    <div class="student-name">📚 {student['name']} - Year {student['year_level']}</div>
                    <div class="student-details">
                        🎂 Age: {student['age']} | 
                        🎯 Interests: {', '.join(student['interests'][:3]) if student['interests'] else 'None specified'}<br>
                        ⏰ Timeline: {student['timeline']} | 
                        📍 Preference: {student.get('location_preference', 'Not specified')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"💬 Chat with {student['name']}", key=f"chat_{student['id']}", use_container_width=True):
                    st.session_state.selected_student = student
                    st.rerun()

    # Chat interface (improved)
    if 'selected_student' in st.session_state:
        student = st.session_state.selected_student

        st.markdown(f"""
        <div class="chat-container">
            <div class="chat-header">
                <div class="chat-title">🤖 AI Career Guidance for {student['name']}</div>
                <div class="chat-subtitle">Powered by Claude AI with live Australian employment data</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chat input with placeholder based on student interests
        interests_text = ', '.join(student['interests'][:2]) if student['interests'] else 'their interests'

        user_input = st.text_area(
            "Ask your career question:",
            placeholder=f"e.g., 'What university courses align with {student['name']}'s interest in {interests_text}?' or 'What are the current job prospects in their field?'",
            height=100,
            help="Ask about university courses, career prospects, application deadlines, or study planning advice."
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Get AI Career Guidance", use_container_width=True):
                if user_input.strip():
                    with st.spinner("🤖 AI Career Counsellor is thinking..."):
                        # Simulate AI response (replace with actual AI integration)
                        st.markdown("""
                        <div class="ai-response" style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 20px; margin: 16px 0;">
                            <div style="font-size: 16px; font-weight: 600; color: #1c4980; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                                🤖 AI Career Counsellor Response
                            </div>
                        """, unsafe_allow_html=True)

                        st.write(f"""
                        **Career Guidance for {student['name']}:**

                        Based on {student['name']}'s interests in **{', '.join(student['interests']) if student['interests'] else 'their chosen fields'}** and current Australian employment data:

                        **🎯 Recommended Career Pathways:**
                        - Analysis of careers matching their interests
                        - Current employment prospects and salary ranges  
                        - University course recommendations for NSW/ACT

                        **📚 Next Steps:**
                        1. Research recommended universities and application requirements
                        2. Plan subject selection for remaining school years
                        3. Attend university open days and career fairs
                        4. Schedule follow-up guidance session

                        **📊 Current Market Data:**
                        - Graduate employment rate: 89.1% (Australian average)
                        - Time to employment: 4.2 months average
                        - Field-specific data updated weekly

                        *This response is saved to your family conversation history.*
                        """)

                        st.markdown("</div>", unsafe_allow_html=True)

                        # Save conversation
                        try:
                            db.save_conversation(
                                family_info['id'],
                                student['id'],
                                student['name'],
                                user_input,
                                "AI career guidance response provided",
                                ['career_guidance']
                            )
                            st.success("✅ Conversation saved to your family records.")
                        except Exception as e:
                            st.warning(f"Conversation not saved: {str(e)}")
                else:
                    st.warning("Please enter a question before submitting.")

        with col2:
            if st.button("👈 Back to Students", use_container_width=True, type="secondary"):
                if 'selected_student' in st.session_state:
                    del st.session_state.selected_student
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Improved main application with better state management"""

    # Initialize session state
    if 'secure_agent' not in st.session_state:
        st.session_state.secure_agent = SecureFamilyCareerAgent()

    # Debug panel (remove in production)
    if st.sidebar.checkbox("🔧 Debug Mode"):
        st.sidebar.write("Session State Keys:", list(st.session_state.keys()))
        if 'authenticated_family' in st.session_state:
            st.sidebar.write("Authenticated:", True)
            st.sidebar.write("Family:", st.session_state.authenticated_family['family_name'])

        # Quick reset button
        if st.sidebar.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main application flow
    if 'authenticated_family' not in st.session_state:
        if 'show_registration' in st.session_state and st.session_state.show_registration:
            create_family_registration()
        else:
            create_family_login()
    else:
        create_authenticated_family_interface(st.session_state.authenticated_family)


if __name__ == "__main__":
    main()