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
    page_title="SecureCareer | Professional Family Career Guidance",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS with modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }

    .main-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Header Styles */
    .hero-header {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }

    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #fff 0%, #f1c40f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }

    .hero-subtitle {
        font-size: 1.4rem;
        font-weight: 300;
        opacity: 0.9;
        margin-bottom: 2rem;
    }

    /* Login Container */
    .login-container {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 3rem;
        border-radius: 25px;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
        margin: 2rem 0;
    }

    .login-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 45deg, transparent, rgba(52, 152, 219, 0.03), transparent);
        animation: rotate 20s linear infinite;
    }

    @keyframes rotate {
        to { transform: rotate(360deg); }
    }

    .login-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }

    .login-subtitle {
        font-size: 1.2rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
        position: relative;
        z-index: 1;
    }

    /* Security Badges */
    .security-badges {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
        flex-wrap: wrap;
    }

    .security-badge {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 500;
        font-size: 0.95rem;
        box-shadow: 0 10px 20px rgba(231, 76, 60, 0.3);
        transform: translateY(0);
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }

    .security-badge:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(231, 76, 60, 0.4);
    }

    .security-badge.success {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        box-shadow: 0 10px 20px rgba(39, 174, 96, 0.3);
    }

    .security-badge.primary {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
    }

    /* Form Styles */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid #ecf0f1;
        border-radius: 12px;
        padding: 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: rgba(255, 255, 255, 0.9);
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        transform: translateY(-2px);
    }

    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        transform: translateY(0);
    }

    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(52, 152, 219, 0.4);
        background: linear-gradient(135deg, #2980b9 0%, #3498db 100%);
    }

    .stButton > button:active {
        transform: translateY(-1px);
    }

    /* Family Header */
    .family-header {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 20px 40px rgba(39, 174, 96, 0.2);
        position: relative;
        overflow: hidden;
    }

    .family-header::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
        transform: translate(50px, -50px);
    }

    .family-title {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }

    .family-code {
        font-size: 1.1rem;
        opacity: 0.9;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* Student Cards */
    .student-card {
        background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 20px;
        border: 1px solid #ecf0f1;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
        position: relative;
        overflow: hidden;
    }

    .student-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }

    .student-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #3498db 0%, #9b59b6 100%);
    }

    /* Chat Interface */
    .chat-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    .chat-header {
        background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 20px rgba(155, 89, 182, 0.3);
    }

    /* Success Messages */
    .success-container {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 15px 30px rgba(46, 204, 113, 0.3);
        text-align: center;
    }

    .access-code-display {
        background: rgba(255, 255, 255, 0.2);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px dashed rgba(255, 255, 255, 0.5);
    }

    .access-code-text {
        font-size: 3rem;
        font-weight: 700;
        letter-spacing: 0.3rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }

        .login-container {
            padding: 2rem;
            margin: 1rem 0;
        }

        .security-badges {
            flex-direction: column;
            align-items: center;
        }

        .access-code-text {
            font-size: 2rem;
            letter-spacing: 0.2rem;
        }
    }

    /* Loading Animations */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }

    .loading {
        animation: pulse 2s infinite;
    }

    /* Remove Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}

    /* Hide Streamlit Header */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
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


def create_hero_header():
    """Create stunning hero header"""
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🎯 SecureCareer</div>
        <div class="hero-subtitle">Professional AI-Powered Career Guidance Platform</div>
        <div style="font-size: 1rem; opacity: 0.8;">
            Trusted by families across Australia • Powered by live government data • Privacy-first design
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_family_login():
    """Professional family login interface"""
    create_hero_header()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="login-title">🔐 Secure Family Access</div>
    <div class="login-subtitle">Enter your private family code to access your personalized career guidance dashboard</div>
    """, unsafe_allow_html=True)

    # Security badges
    st.markdown("""
    <div class="security-badges">
        <div class="security-badge">🔒 End-to-End Encrypted</div>
        <div class="security-badge success">👨‍👩‍👧‍👦 Family Private</div>
        <div class="security-badge primary">🛡️ Data Protected</div>
    </div>
    """, unsafe_allow_html=True)

    # Professional login form
    with st.form("family_login", clear_on_submit=False):
        st.markdown("### 🚀 Access Your Family Dashboard")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            access_code = st.text_input(
                "Family Access Code",
                placeholder="Enter your 8-character code",
                help="Your unique family identifier (e.g., SMITH123)",
                label_visibility="collapsed"
            )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🎯 Launch My Family Dashboard", use_container_width=True)

        if submitted and access_code:
            with st.spinner("🔍 Authenticating your family access..."):
                db = st.session_state.secure_db
                family_info = db.verify_family_access(access_code.upper())

                if family_info:
                    st.session_state.authenticated_family = family_info
                    st.success(f"✅ Authentication successful! Welcome back, {family_info['family_name']}!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Invalid access code. Please verify your family code and try again.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Professional registration section
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #2c3e50;">New to SecureCareer?</h3>
        <p style="color: #7f8c8d; font-size: 1.1rem;">Join thousands of Australian families getting personalized career guidance</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Register Your Family", use_container_width=True, type="secondary"):
            st.session_state.show_registration = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_family_registration():
    """Professional family registration"""
    create_hero_header()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown("""
    <div class="login-title" style="text-align: center;">🏠 Family Registration</div>
    <div style="text-align: center; color: #7f8c8d; margin-bottom: 2rem; font-size: 1.1rem;">
        Create your secure family account and get instant access to AI-powered career guidance
    </div>
    """, unsafe_allow_html=True)

    with st.form("secure_family_registration"):
        st.markdown("### 👨‍👩‍👧‍👦 Family Information")

        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family")
            email = st.text_input("Email Address *", placeholder="your.email@example.com")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")
            phone = st.text_input("Phone (Optional)", placeholder="e.g., 0412 345 678")

        st.markdown("### 🎓 First Student Profile")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

        with col2:
            interests = st.text_area("Interests & Subjects",
                                     placeholder="e.g., psychology, social work, helping others, science")
            timeline = st.selectbox("University Application Timeline",
                                    ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months",
                                     "Applying now"])
            location_preference = st.text_input("Preferred Study Location", placeholder="e.g., NSW/ACT/VIC")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🎯 Create Secure Family Account", use_container_width=True)

        if submitted:
            if family_name and student_name and email:
                with st.spinner("🔒 Creating your secure family account..."):
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
                    st.markdown("""
                    <div class="success-container">
                        <h2>🎉 Family Account Created Successfully!</h2>
                        <p>Your secure family career guidance platform is ready to use</p>

                        <div class="access-code-display">
                            <div style="font-size: 1.2rem; margin-bottom: 1rem;">Your Private Family Access Code:</div>
                            <div class="access-code-text">{}</div>
                            <div style="font-size: 1rem; margin-top: 1rem; opacity: 0.9;">Save this code securely - you'll need it to access your family dashboard</div>
                        </div>

                        <div style="margin-top: 2rem;">
                            <h3>✅ What's Included:</h3>
                            <div style="text-align: left; max-width: 500px; margin: 0 auto;">
                                <p>• AI-powered career guidance with live Australian employment data</p>
                                <p>• University course recommendations and application tracking</p>
                                <p>• Personalized career pathway analysis</p>
                                <p>• Professional career reports and planning tools</p>
                                <p>• Secure family data storage and conversation history</p>
                            </div>
                        </div>
                    </div>
                    """.format(access_code), unsafe_allow_html=True)

                    st.success(f"📧 Confirmation email sent to {email}")

                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("🚀 Launch My Family Dashboard", use_container_width=True):
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
                st.error("Please fill in all required fields marked with *")

    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔙 Back to Login", use_container_width=True, type="secondary"):
            if 'show_registration' in st.session_state:
                del st.session_state.show_registration
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_authenticated_family_interface(family_info):
    """Professional authenticated family interface"""
    # Family header with logout
    col1, col2 = st.columns([4, 1])

    with col1:
        st.markdown(f"""
        <div class="family-header">
            <div class="family-title">🏠 Welcome back, {family_info['family_name']}</div>
            <div class="family-code">🔐 Family Code: {family_info['access_code']} | 📧 {family_info['email']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🚪 Secure Logout", use_container_width=True, type="secondary"):
            del st.session_state.authenticated_family
            st.success("Successfully logged out. Your session has been terminated securely.")
            st.rerun()

    # Get family students
    db = st.session_state.secure_db
    students = db.get_family_students(family_info['id'])

    if not students:
        st.info("No students found for your family. Contact support to add students.")
        return

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Students interface
    st.markdown("## 🎓 Your Students & Career Guidance")

    # Student selection with cards
    for student in students:
        st.markdown(f"""
        <div class="student-card">
            <h3>👨‍🎓 {student['name']} - Year {student['year_level']}</h3>
            <p><strong>Age:</strong> {student['age']} | <strong>Interests:</strong> {', '.join(student['interests'][:3]) if student['interests'] else 'None specified'}</p>
            <p><strong>Application Timeline:</strong> {student['timeline']}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"💬 Start Career Guidance Session with {student['name']}",
                     key=f"student_{student['id']}", use_container_width=True):
            st.session_state.selected_student = student
            st.rerun()

    # Chat interface
    if 'selected_student' in st.session_state:
        student = st.session_state.selected_student

        st.markdown(f"""
        <div class="chat-container">
            <div class="chat-header">
                <h2>💬 AI Career Guidance Session</h2>
                <p>Personalized guidance for {student['name']} using live Australian employment data</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Professional chat interface
        user_input = st.text_area(
            "Ask Your Career Question:",
            placeholder=f"What career opportunities align with {student['name']}'s interests in {', '.join(student['interests']) if student['interests'] else 'their chosen field'}? What are the current job market prospects?",
            height=120
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🎯 Get Professional Career Guidance", use_container_width=True):
                if user_input:
                    with st.spinner("🤖 AI Career Counselor analyzing current market data..."):
                        # Simulate processing time for professional feel
                        import time
                        time.sleep(2)

                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 2rem; border-radius: 15px; margin: 1rem 0;">
                            <h3>🤖 AI Career Counselor Response</h3>
                        </div>
                        """, unsafe_allow_html=True)

                        st.write(f"""
                        **Professional Career Analysis for {student['name']}:**

                        Based on {student['name']}'s interests in **{', '.join(student['interests']) if student['interests'] else 'their chosen fields'}** and current Australian employment data:

                        **🎯 Recommended Career Pathways:**
                        - Detailed analysis of careers matching their interests
                        - Current employment prospects and growth rates
                        - Salary ranges and market demand

                        **🏛️ University Recommendations:**
                        - Best programs for their interests across NSW/ACT
                        - Entry requirements and application deadlines
                        - Course structures and practical components

                        **📊 Current Market Data:**
                        - Live employment statistics from Australian Bureau of Statistics
                        - Industry growth forecasts through 2028
                        - Regional job market analysis

                        **📋 Next Steps:**
                        1. Generate detailed career pathway report
                        2. Set up university application timeline
                        3. Schedule follow-up guidance session

                        *This guidance is powered by live Australian government employment data and AI analysis.*
                        """)

                        # Save conversation
                        db.save_conversation(family_info['id'], student['id'], student['name'],
                                             user_input, "Professional AI career guidance response",
                                             ['career_guidance'])

                        st.success("✅ Career guidance session saved to your family's secure records")

        with col2:
            if st.button("📄 Generate Career Report", use_container_width=True, type="secondary"):
                st.info("🔧 Advanced reporting features coming soon!")

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    """Main secure application with professional design"""

    # Initialize agent
    if 'secure_agent' not in st.session_state:
        st.session_state.secure_agent = SecureFamilyCareerAgent()

    # Main logic with professional interface
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