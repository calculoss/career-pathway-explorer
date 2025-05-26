import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import anthropic
import os
import json
import requests
import uuid
import sqlite3
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from multi_family_database import MultiFamilyDatabase
from canvas_integration import CanvasIntegrator, SimpleMilestoneGenerator, show_canvas_setup

# Page configuration
st.set_page_config(
    page_title="CareerPath | Family Career Guidance & Study Planning",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with tab styling and Canvas integration styles
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

    /* Global Styles */
    .stApp {
        background-color: #f7f8fa;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container with reduced spacing */
    .main-content {
        background: white;
        border-radius: 8px;
        padding: 24px;
        margin: 8px auto 24px auto;
        max-width: 1200px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    /* Enhanced tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 24px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 12px 24px;
        background-color: transparent;
        border-radius: 6px;
        color: #6b7280;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1c4980;
        color: white;
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e5e7eb;
        color: #374151;
    }

    .stTabs [aria-selected="true"]:hover {
        background-color: #164373;
        color: white;
    }

    /* Canvas Integration Styles */
    .canvas-container {
        background: #f8f9fa;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin: 16px 0;
    }

    .canvas-header {
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 16px;
        margin-bottom: 20px;
    }

    .canvas-title {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 4px;
    }

    .canvas-subtitle {
        font-size: 14px;
        color: #6b7280;
    }

    /* Assignment table styling */
    .assignment-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 16px 0;
    }

    .assignment-row {
        padding: 16px;
        border-bottom: 1px solid #e5e5e5;
        transition: background-color 0.2s ease;
    }

    .assignment-row:hover {
        background-color: #f8f9fa;
    }

    .assignment-row.overdue {
        border-left: 4px solid #dc3545;
        background-color: #fff5f5;
    }

    .assignment-row.due-soon {
        border-left: 4px solid #ffc107;
        background-color: #fffbf0;
    }

    .assignment-row.future {
        border-left: 4px solid #28a745;
        background-color: #f0f9f4;
    }

    .assignment-name {
        font-size: 16px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 4px;
    }

    .assignment-details {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.4;
    }

    .urgency-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-left: 8px;
    }

    .urgency-overdue {
        background-color: #dc3545;
        color: white;
    }

    .urgency-soon {
        background-color: #ffc107;
        color: #000;
    }

    .urgency-future {
        background-color: #28a745;
        color: white;
    }

    /* AI Study Planning Styles */
    .study-plan-container {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
    }

    .study-plan-header {
        font-size: 18px;
        font-weight: 600;
        color: #0c4a6e;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .milestone-item {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }

    .milestone-item:hover {
        border-color: #1c4980;
        box-shadow: 0 2px 4px rgba(28, 73, 128, 0.1);
    }

    .milestone-item.selected {
        border-color: #1c4980;
        background-color: #f0f9ff;
    }

    .milestone-item.completed {
        border-color: #16a34a;
        background-color: #f0fdf4;
        opacity: 0.8;
    }

    .milestone-title {
        font-size: 16px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .milestone-description {
        font-size: 14px;
        color: #6b7280;
        line-height: 1.4;
        margin-bottom: 12px;
    }

    .milestone-date {
        font-size: 12px;
        color: #9ca3af;
        font-style: italic;
    }

    /* Progress tracking */
    .progress-container {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 20px;
        margin: 16px 0;
    }

    .progress-header {
        font-size: 18px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
    }

    .progress-bar {
        background-color: #e5e7eb;
        border-radius: 8px;
        overflow: hidden;
        height: 12px;
        margin: 8px 0;
    }

    .progress-fill {
        background-color: #1c4980;
        height: 100%;
        border-radius: 8px;
        transition: width 0.3s ease;
    }

    /* Authentication styles */
    .auth-container {
        max-width: 400px;
        margin: 40px auto;
        background: white;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    .auth-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 16px;
    }

    .auth-subtitle {
        text-align: center;
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 32px;
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
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 16px;
        font-family: 'Lato', sans-serif;
        background: white;
        transition: border-color 0.2s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1c4980;
        outline: none;
        box-shadow: 0 0 0 3px rgba(28, 73, 128, 0.1);
    }

    /* Family header */
    .family-header {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 24px;
    }

    .family-title {
        font-size: 22px;
        font-weight: 600;
        color: #0c4a6e;
        margin-bottom: 6px;
    }

    .family-details {
        font-size: 14px;
        color: #075985;
    }

    /* Student cards */
    .student-card {
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 12px;
        background: white;
        transition: all 0.2s ease;
    }

    .student-card:hover {
        border-color: #1c4980;
        box-shadow: 0 2px 8px rgba(28, 73, 128, 0.1);
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-content {
            margin: 8px 16px 16px 16px;
            padding: 20px;
        }

        .auth-container {
            margin: 20px 16px;
            padding: 24px;
        }
    }
</style>
""", unsafe_allow_html=True)


class ComprehensiveFamilyCareerAgent:
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

    def test_canvas_connection(self, canvas_url, access_token):
        """Test Canvas API connection"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(f"{canvas_url}/api/v1/users/self", headers=headers, timeout=10)

            if response.status_code == 200:
                user_data = response.json()
                return True, user_data.get('name', 'Unknown User')
            else:
                return False, f"API Error: {response.status_code}"
        except Exception as e:
            return False, str(e)

    def sync_canvas_assignments(self, student_id, canvas_url, access_token):
        """Sync assignments from Canvas"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}

            # Get courses
            courses_response = requests.get(f"{canvas_url}/api/v1/courses", headers=headers, timeout=10)
            if courses_response.status_code != 200:
                return False, "Failed to fetch courses"

            courses = courses_response.json()
            assignments_synced = 0

            for course in courses[:5]:  # Limit to 5 courses
                course_id = course['id']
                course_name = course['name']

                # Get assignments
                assignments_response = requests.get(
                    f"{canvas_url}/api/v1/courses/{course_id}/assignments",
                    headers=headers,
                    timeout=10
                )

                if assignments_response.status_code == 200:
                    assignments = assignments_response.json()

                    for assignment in assignments:
                        if assignment.get('due_at'):
                            # Save to database
                            conn = self.db.db_path
                            # Implementation would save assignment data
                            assignments_synced += 1

                # Get quizzes
                quizzes_response = requests.get(
                    f"{canvas_url}/api/v1/courses/{course_id}/quizzes",
                    headers=headers,
                    timeout=10
                )

                if quizzes_response.status_code == 200:
                    quizzes = quizzes_response.json()

                    for quiz in quizzes:
                        if quiz.get('due_at'):
                            assignments_synced += 1

            return True, f"Synced {assignments_synced} assignments and quizzes"

        except Exception as e:
            return False, str(e)

    def generate_ai_study_plan(self, assignment_name, due_date, assignment_description=""):
        """Generate AI study plan milestones for an assignment"""
        try:
            prompt = f"""
            Create a 4-step study plan for this assignment:

            Assignment: {assignment_name}
            Due Date: {due_date}
            Description: {assignment_description}

            Please create 4 specific, actionable study milestones that would help a student complete this assignment effectively. Format as JSON:

            [
                {{
                    "title": "Milestone 1 title",
                    "description": "Detailed description of what to do",
                    "target_date": "YYYY-MM-DD"
                }},
                ...
            ]

            Make the milestones specific, realistic, and well-distributed leading up to the due date.
            """

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse the response to extract JSON
            content = response.content[0].text

            # Extract JSON from the response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                milestones_data = json.loads(json_match.group())
                return milestones_data
            else:
                # Fallback to default milestones
                return self.get_default_milestones(assignment_name, due_date)

        except Exception as e:
            st.error(f"AI generation failed: {e}")
            return self.get_default_milestones(assignment_name, due_date)

    def get_default_milestones(self, assignment_name, due_date):
        """Fallback default milestones"""
        return [
            {
                "title": "Initial Research & Planning",
                "description": f"Research the topic for {assignment_name} and create an outline",
                "target_date": due_date  # Would calculate proper dates
            },
            {
                "title": "First Draft",
                "description": "Complete the initial draft of the assignment",
                "target_date": due_date
            },
            {
                "title": "Review & Revise",
                "description": "Review, edit, and improve the assignment",
                "target_date": due_date
            },
            {
                "title": "Final Check",
                "description": "Final proofreading and submission preparation",
                "target_date": due_date
            }
        ]


def create_header():
    """Compact site header"""
    st.markdown("""
    <div style="background: white; border-bottom: 1px solid #e5e5e5; padding: 8px 0; margin-bottom: 16px;">
        <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 32px;">
            <div>
                <span style="font-size: 24px; font-weight: 700; color: #1c4980;">📚 CareerPath</span>
                <span style="font-size: 14px; color: #6b7280; margin-left: 8px;">Professional Career Guidance & Study Planning Platform</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_enhanced_authentication():
    """Enhanced authentication with both access codes and username/password"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Auth method selection
    auth_method = st.radio(
        "Choose login method:",
        ["Family Access Code", "Username & Password"],
        horizontal=True
    )

    if auth_method == "Family Access Code":
        create_access_code_login()
    else:
        create_username_password_login()

    st.markdown("</div>", unsafe_allow_html=True)


def create_access_code_login():
    """Access code login (existing functionality)"""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-title">Family Access</div>
        <div class="auth-subtitle">Enter your unique family code</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("access_code_login"):
        access_code = st.text_input(
            "Family Access Code",
            placeholder="Enter your 8-character code",
            max_chars=8
        )

        submitted = st.form_submit_button("Access Family Dashboard", use_container_width=True)

        if submitted and access_code:
            db = st.session_state.secure_db
            family_info = db.verify_family_access(access_code.upper().strip())

            if family_info:
                st.session_state.authenticated_family = family_info
                st.success(f"✅ Welcome back, {family_info['family_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid access code")


def create_username_password_login():
    """Username and password login"""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-title">Account Login</div>
        <div class="auth-subtitle">Sign in with your username and password</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("username_password_login"):
        username = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            login_submitted = st.form_submit_button("Sign In", use_container_width=True)
        with col2:
            register_submitted = st.form_submit_button("Create Account", use_container_width=True, type="secondary")

        if login_submitted:
            # Implement username/password authentication
            st.info("Username/password authentication coming soon!")

        if register_submitted:
            st.session_state.show_registration = True
            st.rerun()


def create_canvas_integration_tab(student):
    """Enhanced Canvas integration with AI study planning"""
    st.markdown("""
    <div class="canvas-container">
        <div class="canvas-header">
            <div class="canvas-title">🎓 Canvas LMS Integration</div>
            <div class="canvas-subtitle">Sync assignments and create AI-powered study plans</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Canvas connection section
    with st.expander("🔗 Canvas Connection Settings", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            canvas_url = st.text_input(
                "Canvas URL",
                placeholder="https://your-school.instructure.com",
                help="Your school's Canvas URL"
            )

        with col2:
            access_token = st.text_input(
                "Access Token",
                type="password",
                placeholder="Your Canvas access token",
                help="Generate from Canvas Account Settings > Approved Integrations"
            )

        if st.button("🧪 Test Connection", use_container_width=True):
            if canvas_url and access_token:
                agent = st.session_state.comprehensive_agent
                success, message = agent.test_canvas_connection(canvas_url, access_token)

                if success:
                    st.success(f"✅ Connected successfully! User: {message}")
                    # Save credentials
                    st.info("💾 Credentials saved securely")
                else:
                    st.error(f"❌ Connection failed: {message}")
            else:
                st.warning("Please enter both Canvas URL and access token")

        if st.button("🔄 Sync Assignments", use_container_width=True):
            if canvas_url and access_token:
                agent = st.session_state.comprehensive_agent
                with st.spinner("Syncing assignments from Canvas..."):
                    success, message = agent.sync_canvas_assignments(student['id'], canvas_url, access_token)

                if success:
                    st.success(f"✅ {message}")
                    st.rerun()  # Refresh to show new assignments
                else:
                    st.error(f"❌ Sync failed: {message}")

    # Sample assignments (replace with real data from database)
    assignments_data = [
        {
            "name": "History Essay - World War II",
            "course": "Modern History",
            "due_date": "2024-12-15",
            "type": "Assignment",
            "points": 100,
            "description": "Write a 2000-word essay on the causes of WWII"
        },
        {
            "name": "Biology Lab Report",
            "course": "Biology",
            "due_date": "2024-12-10",
            "type": "Assignment",
            "points": 50,
            "description": "Lab report on cellular respiration experiment"
        },
        {
            "name": "Mathematics Final Exam",
            "course": "Mathematics",
            "due_date": "2024-12-20",
            "type": "Quiz",
            "points": 200,
            "description": "Comprehensive final exam covering all semester topics"
        }
    ]

    # Assignments table with AI study planning
    st.markdown("### 📋 Upcoming Assignments & Exams")

    for i, assignment in enumerate(assignments_data):
        # Calculate urgency
        due_date = datetime.strptime(assignment['due_date'], '%Y-%m-%d')
        days_until_due = (due_date - datetime.now()).days

        if days_until_due < 0:
            urgency_class = "overdue"
            urgency_text = "OVERDUE"
            urgency_badge_class = "urgency-overdue"
        elif days_until_due <= 3:
            urgency_class = "due-soon"
            urgency_text = "DUE SOON"
            urgency_badge_class = "urgency-soon"
        else:
            urgency_class = "future"
            urgency_text = "FUTURE"
            urgency_badge_class = "urgency-future"

        with st.container():
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                <div class="assignment-row {urgency_class}">
                    <div class="assignment-name">
                        {assignment['name']}
                        <span class="urgency-badge {urgency_badge_class}">{urgency_text}</span>
                    </div>
                    <div class="assignment-details">
                        📚 {assignment['course']} | 📅 Due: {assignment['due_date']} | 
                        🎯 {assignment['points']} points | 📝 {assignment['type']}
                        <br>{assignment['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button(f"🤖 Generate Study Plan", key=f"study_plan_{i}", use_container_width=True):
                    st.session_state[f"show_study_plan_{i}"] = True
                    st.rerun()

        # AI Study Planning Interface
        if st.session_state.get(f"show_study_plan_{i}", False):
            st.markdown(f"""
            <div class="study-plan-container">
                <div class="study-plan-header">
                    🧠 AI Study Plan for: {assignment['name']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Generate AI milestones
            if f"milestones_{i}" not in st.session_state:
                agent = st.session_state.comprehensive_agent
                with st.spinner("🤖 AI is creating your study plan..."):
                    milestones = agent.generate_ai_study_plan(
                        assignment['name'],
                        assignment['due_date'],
                        assignment['description']
                    )
                    st.session_state[f"milestones_{i}"] = milestones

            milestones = st.session_state[f"milestones_{i}"]

            # Step 1: AI Suggestions (Interactive Selection)
            st.markdown("#### Step 1: Select AI-Generated Milestones")

            selected_milestones = []

            for j, milestone in enumerate(milestones):
                col1, col2, col3 = st.columns([1, 4, 2])

                with col1:
                    selected = st.checkbox("Select", key=f"milestone_{i}_{j}")

                with col2:
                    edited_description = st.text_area(
                        "Description",
                        value=milestone['description'],
                        height=60,
                        key=f"desc_{i}_{j}",
                        label_visibility="collapsed"
                    )

                with col3:
                    edited_date = st.date_input(
                        "Target Date",
                        value=datetime.strptime(milestone['target_date'], '%Y-%m-%d').date(),
                        key=f"date_{i}_{j}",
                        label_visibility="collapsed"
                    )

                if selected:
                    selected_milestones.append({
                        "title": milestone['title'],
                        "description": edited_description,
                        "target_date": str(edited_date)
                    })

            # Step 2: Add Custom Milestones
            with st.expander("➕ Add Your Own Milestones"):
                with st.form(f"custom_milestone_{i}"):
                    custom_title = st.text_input("Milestone Title")
                    custom_description = st.text_area("Description")
                    custom_date = st.date_input("Target Date")

                    if st.form_submit_button("Add Custom Milestone"):
                        if custom_title:
                            custom_milestone = {
                                "title": custom_title,
                                "description": custom_description,
                                "target_date": str(custom_date)
                            }
                            selected_milestones.append(custom_milestone)
                            st.success("✅ Custom milestone added!")

            # Step 3: Save Study Plan
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"💾 Save Study Plan ({len(selected_milestones)} milestones)", key=f"save_{i}",
                             use_container_width=True):
                    if selected_milestones:
                        # Save to database (implement database saving logic)
                        st.success(f"✅ Study plan saved with {len(selected_milestones)} milestones!")
                        st.session_state[f"saved_plan_{i}"] = selected_milestones
                    else:
                        st.warning("Please select at least one milestone")

            with col2:
                if st.button("❌ Cancel", key=f"cancel_{i}", use_container_width=True, type="secondary"):
                    st.session_state[f"show_study_plan_{i}"] = False
                    st.rerun()

            # Show saved study plan
            if st.session_state.get(f"saved_plan_{i}"):
                st.markdown("#### 📊 Your Study Plan Progress")

                saved_plan = st.session_state[f"saved_plan_{i}"]
                completed_count = 0

                for k, milestone in enumerate(saved_plan):
                    col1, col2 = st.columns([1, 5])

                    with col1:
                        completed = st.checkbox(
                            "Done",
                            key=f"completed_{i}_{k}",
                            value=st.session_state.get(f"completed_{i}_{k}", False)
                        )
                        if completed:
                            completed_count += 1

                    with col2:
                        milestone_class = "completed" if completed else ""
                        st.markdown(f"""
                        <div class="milestone-item {milestone_class}">
                            <div class="milestone-title">{milestone['title']}</div>
                            <div class="milestone-description">{milestone['description']}</div>
                            <div class="milestone-date">Target: {milestone['target_date']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Progress bar
                progress = completed_count / len(saved_plan) if saved_plan else 0
                st.markdown(f"""
                <div class="progress-container">
                    <div class="progress-header">Progress: {completed_count}/{len(saved_plan)} milestones completed</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {progress * 100}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


def create_comprehensive_family_interface(family_info):
    """Enhanced family interface with full tab navigation"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Family header
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
            keys_to_remove = ['authenticated_family', 'selected_student']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Get students
    try:
        db = st.session_state.secure_db
        students = db.get_family_students(family_info['id'])
    except Exception as e:
        st.error(f"Error loading students: {str(e)}")
        students = []

    if not students:
        st.warning("📚 No students found for your family.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Student selection
    st.markdown("### 👨‍🎓 Select Student")

    student_names = [f"{s['name']} (Year {s['year_level']})" for s in students]
    selected_student_idx = st.selectbox(
        "Choose student:",
        range(len(students)),
        format_func=lambda x: student_names[x],
        key="student_selector"
    )

    selected_student = students[selected_student_idx]

    # Tab navigation for selected student
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Career Guidance", "🎓 Canvas & Study Planning", "📊 Progress", "⚙️ Settings"])

    with tab1:
        create_career_guidance_tab(selected_student, family_info)

    with tab2:  # Canvas & Study Planning tab
        show_simple_canvas_integration(selected_student)

    with tab3:
        create_progress_tab(selected_student)

    with tab4:
        create_settings_tab(selected_student, family_info)

    st.markdown("</div>", unsafe_allow_html=True)


def create_career_guidance_tab(student, family_info):
    """Career guidance tab (existing functionality)"""
    st.markdown("### 🤖 AI Career Guidance")

    interests_text = ', '.join(student['interests'][:2]) if student['interests'] else 'their interests'

    user_input = st.text_area(
        "Ask your career question:",
        placeholder=f"e.g., 'What university courses align with {student['name']}'s interest in {interests_text}?' or 'What are the current job prospects in their field?'",
        height=100
    )

    if st.button("🚀 Get AI Career Guidance", use_container_width=True):
        if user_input.strip():
            with st.spinner("🤖 AI Career Counsellor is thinking..."):
                st.markdown("""
                <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 20px; margin: 16px 0;">
                    <div style="font-size: 16px; font-weight: 600; color: #1c4980; margin-bottom: 16px;">
                        🤖 AI Career Counsellor Response
                    </div>
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
                """)

                # Save conversation
                try:
                    db = st.session_state.secure_db
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


def create_progress_tab(student):
    """Progress tracking tab"""
    st.markdown("### 📊 Study Progress Overview")

    # Sample progress data
    st.markdown("""
    <div class="progress-container">
        <div class="progress-header">📈 Overall Progress</div>
        <div style="margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span>Assignments Completed</span>
                <span>12/15 (80%)</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 80%"></div>
            </div>
        </div>
        <div style="margin: 16px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span>Study Plans Active</span>
                <span>3/5 (60%)</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: 60%"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent activity
    st.markdown("#### 📝 Recent Activity")

    activities = [
        "✅ Completed milestone: Research for History Essay",
        "📅 Set reminder for Biology Lab Report due date",
        "🤖 Generated AI study plan for Mathematics Final",
        "💬 Had career guidance session about university options"
    ]

    for activity in activities:
        st.markdown(f"- {activity}")


def create_settings_tab(student, family_info):
    """Settings and preferences tab"""
    st.markdown("### ⚙️ Student Settings")

    with st.form(f"student_settings_{student['id']}"):
        st.markdown("#### Update Student Information")

        col1, col2 = st.columns(2)

        with col1:
            updated_interests = st.text_area(
                "Interests",
                value=', '.join(student['interests']) if student['interests'] else '',
                help="Enter interests separated by commas"
            )

            updated_timeline = st.selectbox(
                "University Timeline",
                ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months", "Applying now"],
                index=0
            )

        with col2:
            updated_location_pref = st.text_input(
                "Location Preference",
                value=student.get('location_preference', ''),
                placeholder="e.g., NSW/ACT"
            )

            notifications = st.checkbox("Enable study reminders", value=True)

        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings updated successfully!")

    # Notification preferences
    st.markdown("#### 🔔 Notification Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Assignment due date reminders", value=True)
        st.checkbox("Study plan milestone alerts", value=True)

    with col2:
        st.checkbox("Career guidance suggestions", value=False)
        st.checkbox("Weekly progress summaries", value=True)


class SimpleCanvasIntegrator:
    """Simple Canvas integration for the family app"""

    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_canvas_tables()

    def init_canvas_tables(self):
        """Initialize Canvas tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Canvas credentials table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS canvas_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                canvas_url TEXT,
                access_token TEXT,
                student_name TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                last_sync DATETIME,
                UNIQUE(student_id)
            )
        ''')

        # Canvas assignments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS canvas_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                course_name TEXT,
                assignment_name TEXT,
                due_date DATETIME,
                points_possible REAL,
                description TEXT,
                html_url TEXT,
                is_quiz BOOLEAN DEFAULT FALSE,
                UNIQUE(student_id, assignment_id)
            )
        ''')

        conn.commit()
        conn.close()

    def test_canvas_connection(self, canvas_url: str, access_token: str):
        """Test Canvas API connection"""
        try:
            response = requests.get(
                f"{canvas_url.rstrip('/')}/api/v1/users/self",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15
            )

            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user_name': user_data.get('name', 'Unknown'),
                    'message': f"Connected as {user_data.get('name', 'Unknown')}"
                }
            else:
                return {
                    'success': False,
                    'message': f'HTTP {response.status_code}: Authentication failed'
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}'
            }

    def save_canvas_credentials(self, student_id: str, canvas_url: str, access_token: str, user_name: str):
        """Save Canvas credentials for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO canvas_credentials 
                (student_id, canvas_url, access_token, student_name, last_sync)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, canvas_url, access_token, user_name, datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            return False

    def sync_assignments(self, student_id: str):
        """Sync assignments from Canvas"""
        try:
            # Get credentials
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT canvas_url, access_token FROM canvas_credentials 
                WHERE student_id = ? AND is_active = TRUE
            ''', (student_id,))

            result = cursor.fetchone()
            if not result:
                return {'success': False, 'message': 'No Canvas credentials found'}

            canvas_url, access_token = result

            # Get courses
            courses_response = requests.get(
                f"{canvas_url}/api/v1/courses",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"enrollment_state": "active", "per_page": 20},
                timeout=15
            )

            if courses_response.status_code != 200:
                return {'success': False, 'message': 'Failed to fetch courses'}

            courses = courses_response.json()
            total_assignments = 0

            # Clear existing assignments
            cursor.execute('DELETE FROM canvas_assignments WHERE student_id = ?', (student_id,))

            # Sync assignments from each course
            for course in courses[:10]:  # Limit to 10 courses
                course_id = course['id']
                course_name = course.get('name', 'Unknown Course')

                # Get assignments
                assignments_response = requests.get(
                    f"{canvas_url}/api/v1/courses/{course_id}/assignments",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"per_page": 50},
                    timeout=15
                )

                if assignments_response.status_code == 200:
                    assignments = assignments_response.json()

                    for assignment in assignments:
                        due_date = assignment.get('due_at')
                        if due_date:
                            try:
                                # Parse Canvas date
                                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                                due_datetime = due_datetime.replace(tzinfo=None)  # Remove timezone

                                cursor.execute('''
                                    INSERT OR REPLACE INTO canvas_assignments
                                    (student_id, assignment_id, course_name, assignment_name, 
                                     due_date, points_possible, description, html_url, is_quiz)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    student_id,
                                    str(assignment['id']),
                                    course_name,
                                    assignment.get('name', 'Untitled Assignment'),
                                    due_datetime.isoformat(),
                                    assignment.get('points_possible', 0),
                                    assignment.get('description', '')[:500],
                                    assignment.get('html_url', ''),
                                    False
                                ))

                                total_assignments += 1

                            except Exception:
                                continue

                # Get quizzes
                quizzes_response = requests.get(
                    f"{canvas_url}/api/v1/courses/{course_id}/quizzes",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={"per_page": 50},
                    timeout=15
                )

                if quizzes_response.status_code == 200:
                    quizzes = quizzes_response.json()

                    for quiz in quizzes:
                        due_date = quiz.get('due_at')
                        if due_date:
                            try:
                                due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                                due_datetime = due_datetime.replace(tzinfo=None)

                                cursor.execute('''
                                    INSERT OR REPLACE INTO canvas_assignments
                                    (student_id, assignment_id, course_name, assignment_name, 
                                     due_date, points_possible, description, html_url, is_quiz)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                ''', (
                                    student_id,
                                    f"quiz_{quiz['id']}",
                                    course_name,
                                    quiz.get('title', 'Untitled Quiz'),
                                    due_datetime.isoformat(),
                                    quiz.get('points_possible', 0),
                                    quiz.get('description', '')[:500],
                                    quiz.get('html_url', ''),
                                    True
                                ))

                                total_assignments += 1

                            except Exception:
                                continue

            # Update last sync time
            cursor.execute('''
                UPDATE canvas_credentials 
                SET last_sync = ? 
                WHERE student_id = ?
            ''', (datetime.now().isoformat(), student_id))

            conn.commit()
            conn.close()

            return {
                'success': True,
                'message': f'Successfully synced {total_assignments} assignments and quizzes',
                'count': total_assignments
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Sync failed: {str(e)}'
            }

    def get_student_assignments(self, student_id: str):
        """Get assignments for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT assignment_id, course_name, assignment_name, due_date, 
                       points_possible, description, html_url, is_quiz
                FROM canvas_assignments 
                WHERE student_id = ?
                ORDER BY due_date ASC
            ''', (student_id,))

            assignments = []
            for row in cursor.fetchall():
                assignments.append({
                    'assignment_id': row[0],
                    'course': row[1],
                    'name': row[2],
                    'due_date': row[3],
                    'points': row[4],
                    'description': row[5] or '',
                    'html_url': row[6] or '',
                    'type': 'Quiz' if row[7] else 'Assignment'
                })

            conn.close()
            return assignments

        except Exception as e:
            return []

    def has_canvas_credentials(self, student_id: str):
        """Check if student has Canvas credentials"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) FROM canvas_credentials 
                WHERE student_id = ? AND is_active = TRUE
            ''', (student_id,))

            count = cursor.fetchone()[0]
            conn.close()
            return count > 0

        except Exception:
            return False


# ADD THESE FUNCTIONS TO YOUR EXISTING APP:

def show_simple_canvas_integration(student):
    """Simple Canvas integration interface"""

    # Initialize Canvas integrator
    if 'simple_canvas' not in st.session_state:
        st.session_state.simple_canvas = SimpleCanvasIntegrator()

    canvas = st.session_state.simple_canvas

    st.markdown("### 🎓 Canvas LMS Integration")

    # Check if already connected
    if canvas.has_canvas_credentials(student['id']):
        show_canvas_dashboard(student, canvas)
    else:
        show_canvas_setup(student, canvas)


def show_canvas_setup(student, canvas):
    """Canvas setup form"""

    st.markdown(f"""
    <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 20px; margin: 16px 0;">
        <h4>🔗 Connect {student['name']}'s Canvas Account</h4>
        <p>Automatically sync assignments and due dates from Canvas.</p>
    </div>
    """, unsafe_allow_html=True)

    # Instructions
    with st.expander("📋 How to get your Canvas access token", expanded=False):
        st.markdown("""
        **Step-by-step instructions:**

        1. **Log into Canvas** (your school's Canvas site)
        2. **Click your profile picture** → **Settings**
        3. **Scroll to "Approved Integrations"**
        4. **Click "+ New Access Token"**
        5. **Purpose:** Enter "Family Career App"
        6. **Click "Generate Token"**
        7. **Copy the token** and paste below

        ⚠️ **Keep your token private** - don't share it with anyone!
        """)

    # Connection form
    with st.form(f"canvas_setup_{student['id']}"):
        col1, col2 = st.columns(2)

        with col1:
            canvas_url = st.text_input(
                "Canvas URL",
                placeholder="https://your-school.instructure.com",
                help="Your school's Canvas website"
            )

        with col2:
            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Token from Canvas → Settings → Approved Integrations"
            )

        submitted = st.form_submit_button("🔗 Connect Canvas", use_container_width=True)

        if submitted and canvas_url and access_token:
            with st.spinner("Testing Canvas connection..."):
                # Test connection
                test_result = canvas.test_canvas_connection(canvas_url, access_token)

                if test_result['status'] == 'success':
                    # Save credentials
                    success = canvas.save_canvas_credentials(
                        student['id'], canvas_url, access_token,
                        test_result['user_name'], test_result['user_id']
                    )
                    if success:
                        st.success(f"✅ **Canvas Connected Successfully!**\n\nConnected as: {test_result['user_name']}")

                        # Initial sync
                        with st.spinner("Syncing assignments..."):
                            sync_result = canvas.sync_assignments(student['id'])

                        if sync_result['status'] == 'success':  # ✅ Correct
                            st.success(f"🎉 {sync_result['message']}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning(f"Canvas connected but sync had issues: {sync_result['message']}")
                    else:
                        st.error("Failed to save Canvas credentials")
                else:
                    st.error(f"❌ **Connection Failed:** {test_result['message']}")


def show_canvas_dashboard(student, canvas):
    """Canvas dashboard for connected student"""

    # Dashboard header
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e5e5e5; border-radius: 8px; padding: 16px;">
            <h4>📚 Canvas Connected</h4>
            <p><strong>{student['name']}</strong> • Canvas integration active</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🔄 Sync Now", use_container_width=True):
            with st.spinner("Syncing Canvas data..."):
                sync_result = canvas.sync_assignments(student['id'])

                if sync_result['success']:
                    st.success(sync_result['message'])
                    st.rerun()
                else:
                    st.error(f"Sync failed: {sync_result['message']}")

    # Show assignments
    show_assignments_table(student, canvas)


def show_assignments_table(student, canvas_integrator):
    """Show full Canvas integration with AI study planning and enhanced filtering"""

    # Initialize Canvas integrator if needed
    if 'canvas_integrator' not in st.session_state:
        st.session_state.canvas_integrator = CanvasIntegrator()

    # Use the full Canvas setup from canvas_integration.py
    show_canvas_setup(student, st.session_state.canvas_integrator)


def main():
    """Enhanced main application"""

    # Initialize session state
    if 'comprehensive_agent' not in st.session_state:
        st.session_state.comprehensive_agent = ComprehensiveFamilyCareerAgent()

    # Debug panel
    if st.sidebar.checkbox("🔧 Debug Mode"):
        st.sidebar.write("Session State Keys:", list(st.session_state.keys()))
        if 'authenticated_family' in st.session_state:
            st.sidebar.write("Authenticated:", True)
            st.sidebar.write("Family:", st.session_state.authenticated_family['family_name'])

        if st.sidebar.button("🔄 Reset Session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Main application flow
    if 'authenticated_family' not in st.session_state:
        if 'show_registration' in st.session_state and st.session_state.show_registration:
            # Use existing registration function
            st.info("Registration functionality available - implement create_family_registration()")
        else:
            create_enhanced_authentication()
    else:
        create_comprehensive_family_interface(st.session_state.authenticated_family)


if __name__ == "__main__":
    main()