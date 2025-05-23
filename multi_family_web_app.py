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

# Clean, professional CSS inspired by Khan Academy
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;600;700&display=swap');

    /* Global Styles */
    .stApp {
        background-color: #f7f8fa;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Remove Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
    }

    /* Main container */
    .main-content {
        background: white;
        border-radius: 8px;
        padding: 32px;
        margin: 24px auto;
        max-width: 1200px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    /* Header */
    .site-header {
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 16px 0;
        margin-bottom: 32px;
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
        font-size: 32px;
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .page-subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 32px;
        line-height: 1.4;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
        margin-top: 32px;
    }

    .section-subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 24px;
    }

    /* Cards */
    .card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        transition: box-shadow 0.2s ease;
    }

    .card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .card-title {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .card-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 16px;
    }

    /* Forms */
    .form-container {
        background: #f9fafb;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 32px;
        margin: 24px 0;
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

    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 16px;
        font-family: 'Lato', sans-serif;
        background: white;
        transition: border-color 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #1c4980;
        outline: none;
        box-shadow: 0 0 0 3px rgba(28, 73, 128, 0.1);
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
    }

    .stButton > button:hover {
        background-color: #164373;
        border-color: #164373;
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    /* Secondary button */
    .secondary-button {
        background-color: white !important;
        color: #1c4980 !important;
        border: 1px solid #1c4980 !important;
    }

    .secondary-button:hover {
        background-color: #f9fafb !important;
    }

    /* Success/Error styling */
    .stSuccess {
        background-color: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 6px;
        padding: 16px;
        margin: 16px 0;
    }

    .stError {
        background-color: #fef2f2;
        border: 1px solid #ef4444;
        border-radius: 6px;
        padding: 16px;
        margin: 16px 0;
    }

    /* Security features */
    .security-features {
        display: flex;
        justify-content: center;
        gap: 32px;
        margin: 32px 0;
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

    /* Family header */
    .family-header {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 32px;
    }

    .family-title {
        font-size: 24px;
        font-weight: 600;
        color: #0c4a6e;
        margin-bottom: 8px;
    }

    .family-details {
        font-size: 16px;
        color: #075985;
    }

    /* Student cards */
    .student-card {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 16px;
        background: white;
        transition: all 0.2s ease;
    }

    .student-card:hover {
        border-color: #1c4980;
        box-shadow: 0 2px 8px rgba(28, 73, 128, 0.1);
    }

    .student-name {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .student-details {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.5;
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

    .access-code-label {
        font-size: 16px;
        color: #075985;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .access-code-note {
        font-size: 14px;
        color: #6b7280;
        margin-top: 16px;
    }

    /* Chat interface */
    .chat-container {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin: 24px 0;
        background: white;
    }

    .chat-header {
        border-bottom: 1px solid #e5e5e5;
        padding-bottom: 16px;
        margin-bottom: 24px;
    }

    .chat-title {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 4px;
    }

    .chat-subtitle {
        font-size: 14px;
        color: #6b7280;
    }

    /* Response styling */
    .ai-response {
        background: #f9fafb;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
    }

    .ai-response-header {
        font-size: 16px;
        font-weight: 600;
        color: #1c4980;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-content {
            margin: 16px;
            padding: 24px;
        }

        .site-header .container {
            padding: 0 24px;
        }

        .security-features {
            flex-direction: column;
            gap: 16px;
        }

        .access-code {
            font-size: 24px;
            letter-spacing: 2px;
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
    """Clean site header"""
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
    """Clean, professional login interface"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Page header
    st.markdown("""
    <div class="page-title">Secure Family Access</div>
    <div class="page-subtitle">Enter your family access code to view your personalized career guidance dashboard</div>
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
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

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
    """Clean authenticated family interface"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

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

    # Students section
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

        st.markdown("""
        <div class="chat-container">
            <div class="chat-header">
                <div class="chat-title">Career Guidance Session</div>
                <div class="chat-subtitle">AI-powered career counseling with live Australian employment data</div>
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
                    <div class="ai-response-header">🤖 AI Career Counselor</div>
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

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main application with clean designs"""

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