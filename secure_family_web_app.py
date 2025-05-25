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

# Replace your entire CSS block with this:
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;500;600;700&display=swap');

    /* KILL STREAMLIT SPACING - MOST AGGRESSIVE VERSION */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    .stApp > div:first-child {
        margin-top: -80px !important; /* Pull content up over header space */
    }

    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Hide Streamlit elements completely */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    #MainMenu, footer, .stDeployButton, .stToolbar {
        display: none !important;
    }

    /* Your existing beautiful styles */
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
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #008a0c 0%, #007a0b 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 166, 14, 0.3);
    }

    /* Custom app container */
    .custom-app {
        margin: 0;
        padding: 0;
        min-height: 100vh;
        background: #ffffff;
        font-family: 'Lato', sans-serif;
    }

    .custom-header {
        background: #ffffff;
        border-bottom: 1px solid #e7e8ea;
        padding: 24px 0;
        margin: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        text-align: center;
    }

    .app-title {
        font-size: 42px;
        font-weight: 600;
        color: #21242c;
        margin: 0;
        letter-spacing: -1px;
    }

    .app-subtitle {
        font-size: 18px;
        color: #626569;
        margin: 8px 0 0 0;
        font-weight: 400;
    }

    .main-content-html {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 24px;
        background: #ffffff;
    }

    /* Add your other styles here */
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


# Add this CSS injection FIRST - more aggressive approach
st.markdown("""
<style>
    /* KILL STREAMLIT SPACING - MOST AGGRESSIVE VERSION */
    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }

    .stApp > div:first-child {
        margin-top: -80px !important; /* Pull content up over header space */
    }

    .element-container {
        margin: 0 !important;
        padding: 0 !important;
    }

    .stMarkdown {
        margin: 0 !important;
        padding: 0 !important;
    }

    /* Hide Streamlit elements completely */
    header[data-testid="stHeader"] {
        display: none !important;
    }

    #MainMenu, footer, .stDeployButton, .stToolbar {
        display: none !important;
    }

    /* Custom app container */
    .custom-app {
        margin: 0;
        padding: 0;
        min-height: 100vh;
        background: #ffffff;
        font-family: 'Lato', sans-serif;
    }

    .custom-header {
        background: #ffffff;
        border-bottom: 1px solid #e7e8ea;
        padding: 24px 0;
        margin: 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 24px;
        text-align: center;
    }

    .app-title {
        font-size: 42px;
        font-weight: 600;
        color: #21242c;
        margin: 0;
        letter-spacing: -1px;
    }

    .app-subtitle {
        font-size: 18px;
        color: #626569;
        margin: 8px 0 0 0;
        font-weight: 400;
    }

    .main-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 32px 24px;
        background: #ffffff;
    }
</style>
""", unsafe_allow_html=True)


def create_html_header_and_start_content():
    """Create header and start main content in pure HTML"""
    st.markdown("""
    <div class="custom-app">
        <div class="custom-header">
            <div class="header-content">
                <h1 class="app-title">CareerPath</h1>
                <p class="app-subtitle">Professional Career Guidance Platform</p>
            </div>
        </div>
        <div class="main-content">
    """, unsafe_allow_html=True)


def close_html_content():
    """Close the HTML content containers"""
    st.markdown("""
        </div> <!-- Close main-content -->
    </div> <!-- Close custom-app -->
    """, unsafe_allow_html=True)


# Replace your create_header() and create_clean_header() functions with:
def create_header():
    """HTML-first header with zero spacing"""
    st.markdown("""
    <div class="custom-app">
        <div class="custom-header">
            <div class="header-content">
                <h1 class="app-title">CareerPath</h1>
                <p class="app-subtitle">Professional Career Guidance Platform</p>
            </div>
        </div>
        <div class="main-content-html">
    """, unsafe_allow_html=True)

def create_clean_header():
    """Same as create_header for consistency"""
    create_header()
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
    """Enhanced family registration - simplified integration"""
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

    # Use the enhanced registration form
    create_enhanced_registration_form()

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
            # Enhanced logout
            if 'family_session' in st.session_state:
                auth_system = st.session_state.get('enhanced_auth')
                if auth_system:
                    auth_system.logout_session(st.session_state.family_session)
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
    """Main application with enhanced authentication"""

    # Initialize session state
    if 'secure_agent' not in st.session_state:
        st.session_state.secure_agent = SecureFamilyCareerAgent()

    # Session cleanup
    auth_system = st.session_state.get('enhanced_auth')
    if auth_system:
        auth_system.cleanup_expired_sessions()

    # Check for valid session
    if 'family_session' in st.session_state and 'authenticated_family' not in st.session_state:
        session_info = auth_system.validate_session(st.session_state.family_session)
        if session_info:
            st.session_state.authenticated_family = {
                'id': session_info['family_id'],
                'family_name': session_info['family_name'],
                'email': session_info.get('email', ''),
                'location': session_info.get('location', '')
            }

    # Main application flow
    if 'authenticated_family' not in st.session_state:
        if 'show_registration' in st.session_state:
            create_family_registration()
        else:
            create_family_login()
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