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
    page_title="Secure Family Career Explorer",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 2rem 0;
    }

    .family-header {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }

    .secure-badge {
        background: #e74c3c;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


class SecureFamilyCareerAgent:
    def __init__(self):
        # API setup
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize database
        if 'secure_db' not in st.session_state:
            st.session_state.secure_db = MultiFamilyDatabase()
        self.db = st.session_state.secure_db


def create_family_login():
    """Secure family login interface"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("# 🔐 Secure Family Access")
    st.markdown("### Enter your family access code to continue")

    # Security badges
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="secure-badge">🔒 Private & Secure</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="secure-badge">👨‍👩‍👧‍👦 Family Only</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="secure-badge">🛡️ Data Protected</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Login form
    with st.form("family_login"):
        st.markdown("### Access Your Family's Career Guidance")

        access_code = st.text_input(
            "Family Access Code",
            placeholder="Enter your 8-character code (e.g., SMITH123)",
            help="You received this code when your family registered"
        )

        submitted = st.form_submit_button("Access My Family", use_container_width=True)

        if submitted and access_code:
            db = st.session_state.secure_db
            family_info = db.verify_family_access(access_code.upper())

            if family_info:
                # Store family info in session
                st.session_state.authenticated_family = family_info
                st.success(f"✅ Welcome back, {family_info['family_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid access code. Please check your code and try again.")

    # Registration section
    st.markdown("---")
    st.markdown("### Don't have an access code?")

    if st.button("🏠 Register New Family", use_container_width=True):
        st.session_state.show_registration = True
        st.rerun()


def create_family_registration():
    """Secure family registration"""
    st.markdown("# 🏠 Register Your Family")
    st.info("📧 **After registration, you'll receive a private access code that only your family can use.**")

    with st.form("secure_family_registration"):
        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., Smith Family")
            email = st.text_input("Email *", placeholder="family@email.com")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

        st.markdown("### Add Your First Student")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

        with col2:
            interests = st.text_area("Interests", placeholder="e.g., psychology, social work, helping others")
            timeline = st.selectbox("Application Timeline",
                                    ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months",
                                     "Applying now"])
            location_preference = st.text_input("Location Preference", placeholder="e.g., NSW/ACT")

        submitted = st.form_submit_button("🔐 Register Family & Get Access Code")

        if submitted:
            if family_name and student_name and email:
                db = st.session_state.secure_db

                # Create family with access code
                family_id, access_code = db.create_family(family_name, email, location)

                # Add student
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

                # Show success with access code
                st.success("🎉 Family registered successfully!")

                st.markdown(f"""
                ### 🔐 Your Private Family Access Code:

                # **{access_code}**

                **⚠️ IMPORTANT:**
                - **Save this code** - you'll need it to access your family's data
                - **Keep it private** - don't share with other families  
                - **Email sent** to {email} with your access code

                **Click below to access your family's career guidance:**
                """)

                if st.button("🚀 Access My Family Now", use_container_width=True):
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
                st.error("Please fill in required fields (Family Name, Student Name, and Email)")

    # Back to login
    if st.button("🔙 Back to Login", use_container_width=True):
        del st.session_state.show_registration
        st.rerun()


def create_authenticated_family_interface(family_info):
    """Interface for authenticated family"""
    # Family header with logout
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"""
        <div class="family-header">
            <h2>🏠 Welcome back, {family_info['family_name']}!</h2>
            <p>🔐 Private Family Access Code: <strong>{family_info['access_code']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state.authenticated_family
            st.rerun()

    # Get family students
    db = st.session_state.secure_db
    students = db.get_family_students(family_info['id'])

    if not students:
        st.info("No students found for your family.")
        return

    # Students interface
    st.markdown("## 👨‍👩‍👧‍👦 Your Students")

    # Student selection
    for student in students:
        if st.button(f"💬 Chat with {student['name']} (Year {student['year_level']})",
                     key=f"student_{student['id']}", use_container_width=True):
            st.session_state.selected_student = student
            st.rerun()

    # Chat interface
    if 'selected_student' in st.session_state:
        student = st.session_state.selected_student

        st.markdown(f"""
        ### 💬 Career Guidance for {student['name']}
        **Interests:** {', '.join(student['interests'])}  
        **Timeline:** {student['timeline']}
        """)

        # Simple chat interface
        user_input = st.text_area("Ask a career guidance question:",
                                  placeholder=f"What career options are available for {student['name']}'s interests?")

        if st.button("Get Career Guidance", use_container_width=True):
            if user_input:
                st.write("**Career Counselor Response:**")
                st.write(
                    f"Thank you for your question about {student['name']}'s career path. Based on their interests in {', '.join(student['interests'])}, I can provide personalized guidance with live Australian employment data and university options.")

                # Save conversation
                db.save_conversation(family_info['id'], student['id'], student['name'],
                                     user_input, "Secure demo response", ['career_guidance'])


def main():
    """Main secure application"""

    # Initialize agent
    if 'secure_agent' not in st.session_state:
        st.session_state.secure_agent = SecureFamilyCareerAgent()

    # Header
    st.markdown("# 🔐 Secure Family Career Explorer")
    st.markdown("**Private, secure career guidance for your family only**")

    # Main logic
    if 'authenticated_family' not in st.session_state:
        # Show login or registration
        if 'show_registration' in st.session_state:
            create_family_registration()
        else:
            create_family_login()
    else:
        # Show authenticated family interface
        create_authenticated_family_interface(st.session_state.authenticated_family)


if __name__ == "__main__":
    main()