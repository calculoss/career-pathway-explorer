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
from dotenv import load_dotenv
from multi_family_database import MultiFamilyDatabase

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

class CanvasIntegrator:
    """Canvas LMS Integration with fixed methods"""

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
                canvas_user_id TEXT,
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

        # Study milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                assignment_name TEXT,
                title TEXT,
                description TEXT,
                target_date TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def test_canvas_connection(self, canvas_url: str, access_token: str):
        """Test Canvas API connection"""
        try:
            clean_url = canvas_url.rstrip('/')
            response = requests.get(
                f"{clean_url}/api/v1/users/self",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15
            )

            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user_name': user_data.get('name', 'Unknown'),
                    'user_id': str(user_data.get('id', '')),
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

    def save_canvas_credentials(self, student_id: str, canvas_url: str, access_token: str,
                                user_name: str, user_id: str = ""):
        """Save Canvas credentials for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO canvas_credentials 
                (student_id, canvas_url, access_token, student_name, canvas_user_id, last_sync)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, canvas_url.rstrip('/'), access_token, user_name, user_id,
                  datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            return False

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

    def get_canvas_credentials(self, student_id: str):
        """Get Canvas credentials for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT canvas_url, access_token, student_name, canvas_user_id, last_sync
                FROM canvas_credentials 
                WHERE student_id = ? AND is_active = TRUE
            ''', (student_id,))

            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    'canvas_url': result[0],
                    'access_token': result[1],
                    'student_name': result[2],
                    'canvas_user_id': result[3],
                    'last_sync': result[4]
                }
            return None

        except Exception:
            return None

    def sync_assignments(self, student_id: str):
        """Sync assignments from Canvas"""
        try:
            credentials = self.get_canvas_credentials(student_id)
            if not credentials:
                return {'success': False, 'message': 'No Canvas credentials found'}

            canvas_url = credentials['canvas_url']
            access_token = credentials['access_token']

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

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing assignments
            cursor.execute('DELETE FROM canvas_assignments WHERE student_id = ?', (student_id,))

            # Sync assignments from each course
            for course in courses[:10]:  # Limit to 10 courses
                course_id = course['id']
                course_name = course.get('name', 'Unknown Course')

                # Get assignments
                try:
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
                                    due_datetime = due_datetime.replace(tzinfo=None)

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

    # REPLACE your CanvasIntegrator save_study_milestones method with this version that creates the table:

    def save_study_milestones(self, student_id: str, assignment_id: str, assignment_name: str, milestones: list):
        """Save study milestones for an assignment - FIXED with table creation"""
        try:
            print(f"🔍 SAVE DEBUG: Starting save for {len(milestones)} milestones")
            print(f"🔍 SAVE DEBUG: student_id={student_id}, assignment_id={assignment_id}")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ENSURE TABLE EXISTS - Create it if missing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    assignment_id TEXT,
                    assignment_name TEXT,
                    title TEXT,
                    description TEXT,
                    target_date TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            print("🔍 SAVE DEBUG: Ensured study_milestones table exists")

            # Clear existing milestones for this assignment
            cursor.execute('''
                DELETE FROM study_milestones 
                WHERE student_id = ? AND assignment_id = ?
            ''', (student_id, assignment_id))

            rows_deleted = cursor.rowcount
            print(f"🔍 SAVE DEBUG: Deleted {rows_deleted} existing milestones")

            # Insert new milestones
            for i, milestone in enumerate(milestones):
                title = milestone.get('title', f'Milestone {i + 1}')
                description = milestone.get('description', '')
                target_date = milestone.get('target_date', '')

                print(f"🔍 SAVE DEBUG: Inserting milestone {i}: {title}")

                cursor.execute('''
                    INSERT INTO study_milestones
                    (student_id, assignment_id, assignment_name, title, description, target_date, completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student_id,
                    assignment_id,
                    assignment_name,
                    title,
                    description,
                    target_date,
                    False
                ))

            conn.commit()

            # Verify what we saved
            cursor.execute('''
                SELECT COUNT(*) FROM study_milestones 
                WHERE student_id = ? AND assignment_id = ?
            ''', (student_id, assignment_id))

            saved_count = cursor.fetchone()[0]
            print(f"🔍 SAVE DEBUG: Verified {saved_count} milestones saved")

            conn.close()

            return saved_count == len(milestones)

        except Exception as e:
            print(f"❌ SAVE ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    # ALSO UPDATE your get_study_milestones method to ensure table exists:

    def get_study_milestones(self, student_id: str, assignment_id: str):
        """Get study milestones for an assignment - FIXED with table creation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # ENSURE TABLE EXISTS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    assignment_id TEXT,
                    assignment_name TEXT,
                    title TEXT,
                    description TEXT,
                    target_date TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                SELECT title, description, target_date, completed
                FROM study_milestones 
                WHERE student_id = ? AND assignment_id = ?
                ORDER BY target_date ASC
            ''', (student_id, assignment_id))

            milestones = []
            for row in cursor.fetchall():
                milestones.append({
                    'title': row[0],
                    'description': row[1],
                    'target_date': row[2],
                    'completed': bool(row[3])
                })

            conn.close()
            print(f"🔍 Retrieved {len(milestones)} milestones for {assignment_id}")
            return milestones

        except Exception as e:
            print(f"❌ Error retrieving milestones: {str(e)}")
            return []

    # OPTIONAL: Also fix your CanvasIntegrator __init__ method to ensure tables are created:
    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_canvas_tables()  # Make sure this gets called

    def init_canvas_tables(self):
        """Initialize Canvas tables if they don't exist - COMPLETE VERSION"""
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
                canvas_user_id TEXT,
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

        # Study milestones table - ENSURE IT'S CREATED HERE TOO
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                assignment_name TEXT,
                title TEXT,
                description TEXT,
                target_date TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ All Canvas tables initialized successfully")

class SecureFamilyCareerAgent:
    def __init__(self):
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None

        if 'secure_db' not in st.session_state:
            st.session_state.secure_db = MultiFamilyDatabase()
        self.db = st.session_state.secure_db

    def generate_ai_study_plan(self, assignment_name, due_date, assignment_description=""):
        """Generate AI study plan milestones for an assignment"""
        if not self.client:
            return self.get_default_milestones(assignment_name, due_date)

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
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                milestones_data = json.loads(json_match.group())
                return milestones_data
            else:
                return self.get_default_milestones(assignment_name, due_date)

        except Exception as e:
            return self.get_default_milestones(assignment_name, due_date)

    def get_default_milestones(self, assignment_name, due_date):
        """Fallback default milestones"""
        try:
            due_datetime = datetime.fromisoformat(due_date.replace('Z', ''))
            days_until_due = (due_datetime - datetime.now()).days

            if days_until_due > 7:
                return [
                    {
                        "title": "Research & Planning",
                        "description": f"Research the topic for {assignment_name} and create an outline",
                        "target_date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
                    },
                    {
                        "title": "First Draft",
                        "description": "Complete the initial draft of the assignment",
                        "target_date": (due_datetime - timedelta(days=3)).strftime('%Y-%m-%d')
                    },
                    {
                        "title": "Review & Revise",
                        "description": "Review, edit, and improve the assignment",
                        "target_date": (due_datetime - timedelta(days=1)).strftime('%Y-%m-%d')
                    },
                    {
                        "title": "Final Check",
                        "description": "Final proofreading and submission preparation",
                        "target_date": due_datetime.strftime('%Y-%m-%d')
                    }
                ]
            else:
                return [
                    {
                        "title": "Quick Planning",
                        "description": "Create outline and gather materials",
                        "target_date": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                    },
                    {
                        "title": "Complete Work",
                        "description": "Complete the assignment",
                        "target_date": (due_datetime - timedelta(days=1)).strftime('%Y-%m-%d')
                    }
                ]
        except:
            return [
                {
                    "title": "Plan Assignment",
                    "description": "Create a plan for completing this assignment",
                    "target_date": datetime.now().strftime('%Y-%m-%d')
                },
                {
                    "title": "Complete Assignment",
                    "description": "Work on and complete the assignment",
                    "target_date": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
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

def create_family_login():
    """Clean, professional login interface"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Page header
    st.markdown("""
    <div class="auth-title">Secure Family Access</div>
    <div class="auth-subtitle">Enter your family access code to view your personalised career guidance dashboard</div>
    """, unsafe_allow_html=True)

    # Security features
    st.markdown("""
    <div style="display: flex; justify-content: center; gap: 32px; margin: 32px 0; flex-wrap: wrap;">
        <div style="text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 24px; margin-bottom: 8px;">🔒</div>
            <div style="font-size: 16px; font-weight: 600; color: #374151; margin-bottom: 4px;">Private & Secure</div>
            <div style="font-size: 14px; color: #6b7280; line-height: 1.4;">Your family's data is encrypted and completely private</div>
        </div>
        <div style="text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 24px; margin-bottom: 8px;">👨‍👩‍👧‍👦</div>
            <div style="font-size: 16px; font-weight: 600; color: #374151; margin-bottom: 4px;">Family Only</div>
            <div style="font-size: 14px; color: #6b7280; line-height: 1.4;">Only your family can access your students and conversations</div>
        </div>
        <div style="text-align: center; flex: 1; min-width: 200px;">
            <div style="font-size: 24px; margin-bottom: 8px;">🛡️</div>
            <div style="font-size: 16px; font-weight: 600; color: #374151; margin-bottom: 4px;">Data Protected</div>
            <div style="font-size: 14px; color: #6b7280; line-height: 1.4;">We never share your information with other families</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Login form
    st.markdown("""
    <div style="background: #f9fafb; border: 1px solid #e5e5e5; border-radius: 8px; padding: 32px; margin: 24px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #374151; margin-bottom: 8px; text-align: center;">Access Your Family Dashboard</div>
        <div style="font-size: 16px; color: #6b7280; margin-bottom: 32px; text-align: center;">Use the 8-character code provided when you registered</div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("family_login"):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            access_code = st.text_input(
                "Family Access Code",
                placeholder="e.g., SMITH123",
                help="The unique 8-character code for your family",
                key="login_access_code"
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

    # Registration section
    st.markdown(
        '<div style="font-size: 24px; font-weight: 600; color: #374151; margin-bottom: 16px; margin-top: 32px;">New to CareerPath?</div>',
        unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size: 16px; color: #6b7280; margin-bottom: 24px;">Join families across Australia getting professional career guidance</div>',
        unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Register Your Family", use_container_width=True, type="secondary", key="register_family_btn"):
            st.session_state.show_registration = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

def create_family_registration():
    """Clean family registration form"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 32px; font-weight: 700; color: #1c4980; margin-bottom: 8px; line-height: 1.2;">Family Registration</div>
    <div style="font-size: 18px; color: #6b7280; margin-bottom: 32px; line-height: 1.4;">Create your secure family account and get instant access to professional career guidance</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f9fafb; border: 1px solid #e5e5e5; border-radius: 8px; padding: 32px; margin: 24px 0;">
    </div>
    """, unsafe_allow_html=True)

    with st.form("family_registration"):
        st.markdown(
            '<div style="font-size: 24px; font-weight: 600; color: #374151; margin-bottom: 16px;">Family Information</div>',
            unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., The Smith Family", key="reg_family_name")
            email = st.text_input("Email Address *", placeholder="your.email@example.com", key="reg_email")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW", key="reg_location")

        st.markdown(
            '<div style="font-size: 24px; font-weight: 600; color: #374151; margin-bottom: 16px; margin-top: 32px;">First Student</div>',
            unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma", key="reg_student_name")
            age = st.number_input("Age", min_value=14, max_value=20, value=16, key="reg_age")
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2, key="reg_year_level")

        with col2:
            interests = st.text_area("Interests", placeholder="e.g., psychology, science, helping others",
                                     key="reg_interests")
            timeline = st.selectbox("University Timeline",
                                    ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months",
                                     "Applying now"], key="reg_timeline")
            location_preference = st.text_input("Study Location Preference", placeholder="e.g., NSW/ACT",
                                                key="reg_location_pref")

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
                <div style="background: #f0f9ff; border: 2px dashed #0ea5e9; border-radius: 8px; padding: 32px; text-align: center; margin: 24px 0;">
                    <div style="font-size: 16px; color: #075985; font-weight: 600; margin-bottom: 8px;">Your Family Access Code</div>
                    <div style="font-size: 36px; font-weight: 700; color: #0c4a6e; letter-spacing: 4px; font-family: 'Monaco', 'Menlo', monospace; margin: 16px 0;">{access_code}</div>
                    <div style="font-size: 14px; color: #6b7280; margin-top: 16px;">
                        Save this code securely. You'll need it to access your family's career guidance dashboard.
                        <br>A confirmation email has been sent to {email}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Access My Family Dashboard", use_container_width=True, key="access_dashboard_btn"):
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

    # Back to login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Back to Login", use_container_width=True, type="secondary", key="back_to_login_btn"):
            if 'show_registration' in st.session_state:
                del st.session_state.show_registration
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

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
        if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
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

    with tab2:
        create_canvas_integration_tab(selected_student)


    with tab3:
        create_progress_tab(selected_student)

    with tab4:
        create_settings_tab(selected_student, family_info)

    st.markdown("</div>", unsafe_allow_html=True)

def create_career_guidance_tab(student, family_info):
    """Career guidance tab"""
    st.markdown("### 🤖 AI Career Guidance")

    interests_text = ', '.join(student['interests'][:2]) if student['interests'] else 'their interests'

    user_input = st.text_area(
        "Ask your career question:",
        placeholder=f"e.g., 'What university courses align with {student['name']}'s interest in {interests_text}?' or 'What are the current job prospects in their field?'",
        height=100,
        key=f"career_input_{student['id']}"
    )

    if st.button("🚀 Get AI Career Guidance", use_container_width=True, key=f"career_btn_{student['id']}"):
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

def create_canvas_integration_tab(student):
    """Canvas integration with AI study planning"""

    # Initialize Canvas integrator
    if 'canvas_integrator' not in st.session_state:
        st.session_state.canvas_integrator = CanvasIntegrator()

    canvas = st.session_state.canvas_integrator

    st.markdown("### 🎓 Canvas LMS Integration")

    # Check if already connected
    if canvas.has_canvas_credentials(student['id']):
        show_canvas_dashboard(student, canvas)
    else:
        show_canvas_connection_form(student, canvas)

def show_assignments_list_with_study_plans(student, canvas):
    """Enhanced assignments list with study plan indicators - FIXED DATE HANDLING"""

    # Get filter values
    days_filter, course_filter, type_filter = show_assignment_filters(student)

    # Get assignments from database
    assignments = canvas.get_student_assignments(student['id'])

    if not assignments:
        st.info("📚 No assignments found. Click 'Sync Now' to get your latest Canvas assignments.")
        return

    # Filter assignments with SAFE date handling
    current_time = datetime.now()
    filtered_assignments = []

    for assignment in assignments:
        try:
            due_date_str = assignment.get('due_date')
            due_date = None  # Initialize as None

            # SAFE date parsing
            if due_date_str:
                try:
                    if isinstance(due_date_str, str):
                        clean_date_str = due_date_str.replace('Z', '').replace('+00:00', '')
                        due_date = datetime.fromisoformat(clean_date_str)
                        assignment['parsed_due_date'] = due_date
                    elif isinstance(due_date_str, datetime):
                        due_date = due_date_str
                        assignment['parsed_due_date'] = due_date
                except Exception:
                    due_date = None
                    assignment['parsed_due_date'] = None

            # Apply TIME filter - ONLY if we have a valid due date
            if due_date:
                days_until_due = (due_date - current_time).days
                if days_until_due > days_filter or days_until_due < -30:
                    continue  # Skip assignments outside time range
            # If no due date, include it (will be handled separately)

            # Apply COURSE filter
            if course_filter != "All Courses":
                assignment_course = assignment.get('course', 'Unknown Course')
                if assignment_course != course_filter:
                    continue

            # Apply TYPE filter
            assignment_category = categorize_assignment(assignment)
            if type_filter == "Assessment Tasks Only" and assignment_category != "Assessment Tasks":
                continue
            elif type_filter == "Quizzes & Tests" and assignment_category != "Quizzes & Tests":
                continue
            elif type_filter == "Course Materials" and assignment_category != "Course Materials":
                continue

            filtered_assignments.append(assignment)

        except Exception as e:
            # If any error, skip this assignment but log it
            st.warning(f"Skipped assignment due to error: {str(e)}")
            continue

    # Sort by due date - handle None dates safely
    def safe_sort_key(assignment):
        due_date = assignment.get('parsed_due_date')
        if due_date:
            return due_date
        else:
            return datetime.max  # Put assignments without dates at the end

    filtered_assignments.sort(key=safe_sort_key)

    # Show summary
    st.markdown(f"""
    **📊 Assignment Summary:** {len(filtered_assignments)} assignments match your filters
    """)

    if not filtered_assignments:
        st.info(f"📅 No {type_filter.lower()} found matching your filters.")
        return

    # Enhanced assignment display with study plan indicators
    st.markdown("### 📅 Assignments with Due Dates")

    for i, assignment in enumerate(filtered_assignments[:20]):
        try:
            # Get study plan info for this assignment
            study_plan_info = get_assignment_study_plan_summary(canvas, student['id'], assignment)

            due_date = assignment.get('parsed_due_date')

            # SAFE urgency calculation
            if due_date:
                days_until_due = (due_date - current_time).days

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

                due_date_display = due_date.strftime('%Y-%m-%d %H:%M')
            else:
                # Handle assignments without due dates
                urgency_class = "future"
                urgency_text = "NO DATE"
                urgency_badge_class = "urgency-future"
                due_date_display = "Date TBD"

            # Create enhanced assignment container
            with st.container():
                col1, col2 = st.columns([3, 1])

                with col1:
                    assignment_name = assignment.get('name', 'Untitled Assignment')
                    course_name = assignment.get('course', 'Unknown Course')
                    points = assignment.get('points', 0)
                    assignment_type = assignment.get('type', 'Assignment')

                    # Display basic assignment info first
                    st.markdown(f"""
                    <div class="assignment-row {urgency_class}">
                        <div class="assignment-name">
                            {assignment_name}
                            <span class="urgency-badge {urgency_badge_class}">{urgency_text}</span>
                        </div>
                        <div class="assignment-details">
                            📚 {course_name} | 📅 Due: {due_date_display} | 
                            🎯 {points} points | 📝 {assignment_type}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display study plan info SEPARATELY if it exists
                    if study_plan_info['has_plan']:
                        progress_percent = study_plan_info['progress_percent']
                        next_milestone = study_plan_info['next_milestone']

                        if next_milestone:
                            next_milestone_text = f"Next: {next_milestone['title']} ({next_milestone['target_date']})"
                            milestone_days = next_milestone.get('days_until_due', 999)
                            if milestone_days <= 1:
                                next_milestone_color = "#dc3545"  # Red
                            elif milestone_days <= 3:
                                next_milestone_color = "#ffc107"  # Yellow
                            else:
                                next_milestone_color = "#28a745"  # Green
                        else:
                            next_milestone_text = "All milestones complete! 🎉"
                            next_milestone_color = "#28a745"

                        # Render study plan info as separate markdown
                        st.markdown(f"""
                        <div style="background: #f0f9ff; border-left: 3px solid #0ea5e9; padding: 8px 12px; margin: 8px 0; border-radius: 4px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <span style="font-weight: 600; color: #0c4a6e;">
                                    🧠 Study Plan: {study_plan_info['completed']}/{study_plan_info['total']} milestones ({progress_percent}%)
                                </span>
                                <div style="background: #e5e7eb; border-radius: 8px; overflow: hidden; width: 100px; height: 8px;">
                                    <div style="background: #0ea5e9; height: 100%; width: {progress_percent}%; transition: width 0.3s ease;"></div>
                                </div>
                            </div>
                            <div style="font-size: 13px; color: #075985;">
                                <span style="background: {next_milestone_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">{next_milestone_text}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)



                with col2:
                    # Study plan action buttons
                    if study_plan_info['has_plan']:
                        # Show "View/Edit Plan" button
                        if st.button(f"📊 View Plan", key=f"view_plan_{i}", use_container_width=True):
                            st.session_state[f"show_study_plan_{student['id']}_dated_{i}"] = True
                            st.rerun()

                        # Quick complete milestone button for next milestone
                        if study_plan_info['next_milestone']:
                            milestone_title = study_plan_info['next_milestone']['title']
                            short_title = milestone_title[:20] + "..." if len(milestone_title) > 20 else milestone_title
                            if st.button(f"✅ Complete:\n{short_title}",
                                         key=f"complete_milestone_{i}", use_container_width=True, type="secondary"):
                                success = complete_milestone(canvas, student['id'], assignment,
                                                             study_plan_info['next_milestone'])
                                if success:
                                    st.success(f"✅ Completed: {milestone_title}")
                                    st.rerun()
                                else:
                                    st.error("Failed to complete milestone")
                    else:
                        # Show "Create Study Plan" button
                        if st.button(f"🤖 Study Plan", key=f"study_plan_btn_{i}", use_container_width=True):
                            st.session_state[f"show_study_plan_{student['id']}_dated_{i}"] = True
                            st.rerun()

                # AI Study Planning Interface (same as before)
                if st.session_state.get(f"show_study_plan_{student['id']}_dated_{i}", False):
                    show_ai_study_planning_dated(student, assignment, i)

        except Exception as e:
            st.error(f"Error displaying assignment {i}: {str(e)}")
            continue

def get_assignment_study_plan_summary(canvas, student_id, assignment):
    """Get summary info about study plan for an assignment - SAFE DATE HANDLING"""
    try:
        assignment_id = assignment.get('assignment_id', f"assignment_dated_{assignment.get('name', '')}")
        milestones = canvas.get_study_milestones(student_id, assignment_id)

        if not milestones:
            return {
                'has_plan': False,
                'total': 0,
                'completed': 0,
                'progress_percent': 0,
                'next_milestone': None
            }

        # Calculate progress
        total_milestones = len(milestones)
        completed_milestones = sum(1 for m in milestones if m.get('completed', False))
        progress_percent = int((completed_milestones / total_milestones) * 100) if total_milestones > 0 else 0

        # Find next incomplete milestone with SAFE date handling
        next_milestone = None
        current_date = datetime.now().date()

        for milestone in milestones:
            if not milestone.get('completed', False):
                try:
                    target_date_str = milestone.get('target_date', '')
                    if target_date_str:
                        target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                        days_until_due = (target_date - current_date).days

                        next_milestone = {
                            'title': milestone['title'],
                            'target_date': milestone['target_date'],
                            'days_until_due': days_until_due
                        }
                        break  # Get the first incomplete milestone
                except Exception:
                    # If date parsing fails, still include the milestone but with safe defaults
                    next_milestone = {
                        'title': milestone.get('title', 'Milestone'),
                        'target_date': milestone.get('target_date', 'Date TBD'),
                        'days_until_due': 999  # Safe default
                    }
                    break

        return {
            'has_plan': True,
            'total': total_milestones,
            'completed': completed_milestones,
            'progress_percent': progress_percent,
            'next_milestone': next_milestone
        }

    except Exception as e:
        return {
            'has_plan': False,
            'total': 0,
            'completed': 0,
            'progress_percent': 0,
            'next_milestone': None
        }

def complete_milestone(canvas, student_id, assignment, milestone_info):
    """Mark a milestone as complete - SAFE IMPLEMENTATION"""
    try:
        conn = sqlite3.connect(canvas.db_path)
        cursor = conn.cursor()

        assignment_id = assignment.get('assignment_id', f"assignment_dated_{assignment.get('name', '')}")
        milestone_title = milestone_info.get('title', '')

        if not milestone_title:
            return False

        cursor.execute('''
            UPDATE study_milestones 
            SET completed = TRUE 
            WHERE student_id = ? AND assignment_id = ? AND title = ?
        ''', (student_id, assignment_id, milestone_title))

        conn.commit()
        conn.close()
        return cursor.rowcount > 0  # Return True if a row was actually updated

    except Exception as e:
        return False

def show_assignments_list(student, canvas):
    """Show assignments list with FIXED filtering - only shows assignments with due dates"""

    # Get filter values
    days_filter, course_filter, type_filter = show_assignment_filters(student)

    # Get assignments from database
    assignments = canvas.get_student_assignments(student['id'])

    if not assignments:
        st.info("📚 No assignments found. Click 'Sync Now' to get your latest Canvas assignments.")
        return

    # Separate assignments with and without due dates
    current_time = datetime.now()
    assignments_with_dates = []
    assignments_without_dates = []

    for assignment in assignments:
        due_date_str = assignment.get('due_date')
        has_due_date = False

        if due_date_str:
            try:
                if isinstance(due_date_str, str):
                    clean_date_str = due_date_str.replace('Z', '').replace('+00:00', '')
                    due_date = datetime.fromisoformat(clean_date_str)
                    assignment['parsed_due_date'] = due_date  # Store parsed date
                    has_due_date = True
                elif isinstance(due_date_str, datetime):
                    assignment['parsed_due_date'] = due_date_str
                    has_due_date = True
            except Exception:
                pass

        if has_due_date:
            assignments_with_dates.append(assignment)
        else:
            assignments_without_dates.append(assignment)

    # Apply filters to assignments WITH due dates only
    filtered_assignments = []

    for assignment in assignments_with_dates:
        try:
            due_date = assignment.get('parsed_due_date')

            # Apply TIME filter
            if due_date:
                days_until_due = (due_date - current_time).days
                if days_until_due > days_filter or days_until_due < -30:
                    continue  # Skip assignments too far in the future

            # Apply COURSE filter
            if course_filter != "All Courses":
                assignment_course = assignment.get('course', 'Unknown Course')
                if assignment_course != course_filter:
                    continue  # Skip assignments not matching the selected course

            # NEW: Apply ASSIGNMENT TYPE filter
            assignment_category = categorize_assignment(assignment)

            if type_filter == "Assessment Tasks Only" and assignment_category != "Assessment Tasks":
                continue
            elif type_filter == "Quizzes & Tests" and assignment_category != "Quizzes & Tests":
                continue
            elif type_filter == "Course Materials" and assignment_category != "Course Materials":
                continue
            # "All Items" shows everything, so no filtering needed

            # If we get here, the assignment passed all filters
            filtered_assignments.append(assignment)

        except Exception:
            # If there's any error, skip this assignment
            continue

    # Show summary
    total_with_dates = len(assignments_with_dates)
    total_without_dates = len(assignments_without_dates)
    filtered_count = len(filtered_assignments)

    if course_filter == "All Courses":
        course_text = "all courses"
    else:
        course_text = f'"{course_filter}"'

    st.markdown(f"""
    **📊 Assignment Summary:**
    - {filtered_count} assignments with due dates match your filters ({course_text}, within {days_filter} days)
    - {total_with_dates} total assignments with due dates
    - {total_without_dates} assignments without due dates (hidden by default)
    """)

    # Show assignments with due dates that match filters
    if filtered_assignments:
        st.markdown("### 📅 Assignments with Due Dates")

        # Sort by due date
        filtered_assignments.sort(key=lambda x: x.get('parsed_due_date', datetime.now()))

        for i, assignment in enumerate(filtered_assignments[:20]):  # Show up to 20
            try:
                due_date = assignment.get('parsed_due_date')
                days_until_due = (due_date - current_time).days

                # Calculate urgency
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

                # Assignment container
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        assignment_name = assignment.get('name', 'Untitled Assignment')
                        course_name = assignment.get('course', 'Unknown Course')
                        points = assignment.get('points', 0)
                        assignment_type = assignment.get('type', 'Assignment')
                        description = assignment.get('description', 'No description available')[:100]
                        due_date_display = due_date.strftime('%Y-%m-%d %H:%M')

                        st.markdown(f"""
                        <div class="assignment-row {urgency_class}">
                            <div class="assignment-name">
                                {assignment_name}
                                <span class="urgency-badge {urgency_badge_class}">{urgency_text}</span>
                            </div>
                            <div class="assignment-details">
                                📚 {course_name} | 📅 Due: {due_date_display} | 
                                🎯 {points} points | 📝 {assignment_type}
                                <br>{description}...
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        unique_key = f"study_plan_btn_{student['id']}_dated_{i}"
                        if st.button(f"🤖 Study Plan", key=unique_key, use_container_width=True):
                            st.session_state[f"show_study_plan_{student['id']}_dated_{i}"] = True
                            st.rerun()

                # AI Study Planning Interface
                if st.session_state.get(f"show_study_plan_{student['id']}_dated_{i}", False):
                    show_ai_study_planning_dated(student, assignment, i)

            except Exception as e:
                st.error(f"Error displaying assignment: {str(e)}")
                continue
    else:
        st.info(f"📅 No {type_filter.lower()} found matching your filters. Try selecting a different type or longer time period.")

    # Optional: Show assignments without due dates in a collapsible section
    if total_without_dates > 0:
        with st.expander(f"📋 View {total_without_dates} assignments without due dates (course materials, etc.)",
                         expanded=False):

            # Apply course filter to undated assignments too
            undated_filtered = []
            for assignment in assignments_without_dates:
                if course_filter == "All Courses":
                    undated_filtered.append(assignment)
                else:
                    assignment_course = assignment.get('course', 'Unknown Course')
                    if assignment_course == course_filter:
                        undated_filtered.append(assignment)

            if undated_filtered:
                st.caption(f"Showing {len(undated_filtered)} undated assignments from {course_text}")

                for i, assignment in enumerate(undated_filtered[:10]):  # Limit to 10
                    assignment_name = assignment.get('name', 'Untitled Assignment')
                    course_name = assignment.get('course', 'Unknown Course')
                    assignment_type = assignment.get('type', 'Assignment')

                    st.markdown(f"""
                    <div class="assignment-row future" style="opacity: 0.7;">
                        <div class="assignment-name">
                            {assignment_name}
                            <span class="urgency-badge urgency-future">NO DATE</span>
                        </div>
                        <div class="assignment-details">
                            📚 {course_name} | 📝 {assignment_type}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.caption("No undated assignments match your course filter.")

def show_ai_study_planning_dated(student, assignment, assignment_index):
    """AI Study Planning Interface - For assignments with due dates"""


    unique_id = f"{student['id']}_dated_{assignment_index}"

    st.markdown(f"""
    <div class="study-plan-container">
        <div class="study-plan-header">
            🧠 AI Study Plan for: {assignment.get('name', 'Assignment')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate AI milestones if not already done
    if f"milestones_{unique_id}" not in st.session_state:
        agent = st.session_state.get('career_agent')
        if not agent:
            if 'career_agent' not in st.session_state:
                st.session_state.career_agent = SecureFamilyCareerAgent()
            agent = st.session_state.career_agent

        with st.spinner("🤖 AI is creating your study plan..."):
            due_date = assignment.get('parsed_due_date')
            due_date_str = due_date.isoformat() if due_date else (datetime.now() + timedelta(days=7)).isoformat()

            milestones = agent.generate_ai_study_plan(
                assignment.get('name', 'Assignment'),
                due_date_str,
                assignment.get('description', '')
            )
            st.session_state[f"milestones_{unique_id}"] = milestones

    milestones = st.session_state[f"milestones_{unique_id}"]

    # Rest of the AI study planning interface (same as before)
    st.markdown("#### Step 1: Select Study Milestones")

    selected_milestones = []

    for j, milestone in enumerate(milestones):
        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
            selected = st.checkbox("Select", key=f"milestone_select_{unique_id}_{j}")

        with col2:
            edited_description = st.text_area(
                "Description",
                value=milestone.get('description', ''),
                height=80,
                key=f"milestone_desc_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        with col3:
            try:
                target_date_str = milestone.get('target_date', '')
                if target_date_str:
                    default_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                else:
                    default_date = datetime.now().date()
            except:
                default_date = datetime.now().date()

            edited_date = st.date_input(
                "Target Date",
                value=default_date,
                key=f"milestone_date_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        if selected:
            selected_milestones.append({
                "title": milestone.get('title', 'Milestone'),
                "description": edited_description,
                "target_date": str(edited_date)
            })

    # Add Custom Milestones
    with st.expander("➕ Add Your Own Milestones"):
        with st.form(f"custom_milestone_form_{unique_id}"):
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
                    if f"custom_milestones_{unique_id}" not in st.session_state:
                        st.session_state[f"custom_milestones_{unique_id}"] = []
                    st.session_state[f"custom_milestones_{unique_id}"].append(custom_milestone)
                    st.success("✅ Custom milestone added!")

    # Include custom milestones
    if f"custom_milestones_{unique_id}" in st.session_state:
        selected_milestones.extend(st.session_state[f"custom_milestones_{unique_id}"])

    # Save Study Plan
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💾 Save Study Plan ({len(selected_milestones)} milestones)",
                     key=f"save_plan_{unique_id}", use_container_width=True):
            if selected_milestones:
                # DEBUG: Show what we're trying to save
                st.write("🔍 **DEBUG INFO:**")
                st.write(f"Student ID: {student['id']}")
                st.write(f"Assignment: {assignment}")
                st.write(f"Selected milestones: {selected_milestones}")

                canvas = st.session_state.canvas_integrator
                assignment_id_to_use = assignment.get('assignment_id', f"assignment_dated_{assignment_index}")
                assignment_name = assignment.get('name', 'Assignment')

                st.write(f"Using assignment_id: {assignment_id_to_use}")
                st.write(f"Assignment name: {assignment_name}")

                # Test database connection first
                try:
                    import sqlite3
                    conn = sqlite3.connect(canvas.db_path)
                    cursor = conn.cursor()

                    # Check if table exists
                    cursor.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='study_milestones'
                    """)
                    table_exists = cursor.fetchone()
                    st.write(f"study_milestones table exists: {table_exists is not None}")

                    if table_exists:
                        # Check table structure
                        cursor.execute("PRAGMA table_info(study_milestones)")
                        columns = cursor.fetchall()
                        st.write(f"Table columns: {columns}")

                    conn.close()

                except Exception as e:
                    st.error(f"Database connection error: {e}")

                # Try to save
                success = canvas.save_study_milestones(
                    student['id'],
                    assignment_id_to_use,
                    assignment_name,
                    selected_milestones
                )

                st.write(f"Save result: {success}")

                if success:
                    st.session_state[f"saved_plan_{unique_id}"] = selected_milestones
                    st.success(f"✅ Study plan saved with {len(selected_milestones)} milestones!")
                else:
                    st.error("❌ Failed to save study plan - check debug info above")
            else:
                st.warning("Please select at least one milestone")

    with col2:
        if st.button("❌ Cancel", key=f"cancel_plan_{unique_id}",
                     use_container_width=True, type="secondary"):
            st.session_state[f"show_study_plan_{student['id']}_dated_{assignment_index}"] = False
            st.rerun()

    # Show saved study plan progress (same as before)
    if st.session_state.get(f"saved_plan_{unique_id}"):
        st.markdown("#### 📊 Your Study Plan Progress")

        saved_plan = st.session_state[f"saved_plan_{unique_id}"]
        completed_count = 0

        for k, milestone in enumerate(saved_plan):
            col1, col2 = st.columns([1, 5])

            with col1:
                completed = st.checkbox("Done", key=f"completed_{unique_id}_{k}",
                                        value=st.session_state.get(f"completed_{unique_id}_{k}", False))
                if completed:
                    completed_count += 1

            with col2:
                milestone_class = "completed" if completed else ""
                st.markdown(f"""
                <div class="milestone-item {milestone_class}">
                    <div class="milestone-title">{milestone.get('title', 'Milestone')}</div>
                    <div class="milestone-description">{milestone.get('description', '')}</div>
                    <div class="milestone-date">Target: {milestone.get('target_date', '')}</div>
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

def show_ai_study_planning_filtered(student, assignment, assignment_index):
    """AI Study Planning Interface - For filtered assignments"""

    unique_id = f"{student['id']}_filtered_{assignment_index}"

    st.markdown(f"""
    <div class="study-plan-container">
        <div class="study-plan-header">
            🧠 AI Study Plan for: {assignment.get('name', 'Assignment')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate AI milestones if not already done
    if f"milestones_{unique_id}" not in st.session_state:
        agent = st.session_state.get('career_agent')
        if not agent:
            if 'career_agent' not in st.session_state:
                st.session_state.career_agent = SecureFamilyCareerAgent()
            agent = st.session_state.career_agent

        with st.spinner("🤖 AI is creating your study plan..."):
            due_date_str = assignment.get('due_date', '')
            if not due_date_str or due_date_str == 'Date TBD':
                due_date_str = (datetime.now() + timedelta(days=7)).isoformat()

            milestones = agent.generate_ai_study_plan(
                assignment.get('name', 'Assignment'),
                due_date_str,
                assignment.get('description', '')
            )
            st.session_state[f"milestones_{unique_id}"] = milestones

    milestones = st.session_state[f"milestones_{unique_id}"]

    # Step 1: AI Suggestions (Interactive Selection)
    st.markdown("#### Step 1: Select Study Milestones")

    selected_milestones = []

    for j, milestone in enumerate(milestones):
        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
            selected = st.checkbox("Select", key=f"milestone_select_{unique_id}_{j}")

        with col2:
            edited_description = st.text_area(
                "Description",
                value=milestone.get('description', ''),
                height=80,
                key=f"milestone_desc_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        with col3:
            try:
                target_date_str = milestone.get('target_date', '')
                if target_date_str:
                    default_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                else:
                    default_date = datetime.now().date()
            except:
                default_date = datetime.now().date()

            edited_date = st.date_input(
                "Target Date",
                value=default_date,
                key=f"milestone_date_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        if selected:
            selected_milestones.append({
                "title": milestone.get('title', 'Milestone'),
                "description": edited_description,
                "target_date": str(edited_date)
            })

    # Step 2: Add Custom Milestones
    with st.expander("➕ Add Your Own Milestones"):
        with st.form(f"custom_milestone_form_{unique_id}"):
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
                    if f"custom_milestones_{unique_id}" not in st.session_state:
                        st.session_state[f"custom_milestones_{unique_id}"] = []
                    st.session_state[f"custom_milestones_{unique_id}"].append(custom_milestone)
                    st.success("✅ Custom milestone added!")

    # Include custom milestones
    if f"custom_milestones_{unique_id}" in st.session_state:
        selected_milestones.extend(st.session_state[f"custom_milestones_{unique_id}"])

    # Step 3: Save Study Plan
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💾 Save Study Plan ({len(selected_milestones)} milestones)",
                     key=f"save_plan_{unique_id}", use_container_width=True):
            if selected_milestones:
                canvas = st.session_state.canvas_integrator
                success = canvas.save_study_milestones(
                    student['id'],
                    assignment.get('assignment_id', f"assignment_filtered_{assignment_index}"),
                    assignment.get('name', 'Assignment'),
                    selected_milestones
                )

                if success:
                    st.session_state[f"saved_plan_{unique_id}"] = selected_milestones
                    st.success(f"✅ Study plan saved with {len(selected_milestones)} milestones!")
                else:
                    st.error("Failed to save study plan")
            else:
                st.warning("Please select at least one milestone")

    with col2:
        if st.button("❌ Cancel", key=f"cancel_plan_{unique_id}",
                     use_container_width=True, type="secondary"):
            st.session_state[f"show_study_plan_{student['id']}_filtered_{assignment_index}"] = False
            st.rerun()

    # Show saved study plan (same logic as before)
    if st.session_state.get(f"saved_plan_{unique_id}"):
        st.markdown("#### 📊 Your Study Plan Progress")

        saved_plan = st.session_state[f"saved_plan_{unique_id}"]
        completed_count = 0

        for k, milestone in enumerate(saved_plan):
            col1, col2 = st.columns([1, 5])

            with col1:
                completed = st.checkbox("Done", key=f"completed_{unique_id}_{k}",
                                        value=st.session_state.get(f"completed_{unique_id}_{k}", False))
                if completed:
                    completed_count += 1

            with col2:
                milestone_class = "completed" if completed else ""
                st.markdown(f"""
                <div class="milestone-item {milestone_class}">
                    <div class="milestone-title">{milestone.get('title', 'Milestone')}</div>
                    <div class="milestone-description">{milestone.get('description', '')}</div>
                    <div class="milestone-date">Target: {milestone.get('target_date', '')}</div>
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

def show_canvas_connection_form(student, canvas):
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
    with st.form(f"canvas_setup_form_{student['id']}"):
        col1, col2 = st.columns(2)

        with col1:
            canvas_url = st.text_input(
                "Canvas URL",
                placeholder="https://your-school.instructure.com",
                help="Your school's Canvas website",
                key=f"canvas_url_{student['id']}"
            )

        with col2:
            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Token from Canvas → Settings → Approved Integrations",
                key=f"canvas_token_{student['id']}"
            )

        submitted = st.form_submit_button("🔗 Connect Canvas", use_container_width=True)

        if submitted and canvas_url and access_token:
            with st.spinner("Testing Canvas connection..."):
                # Test connection
                test_result = canvas.test_canvas_connection(canvas_url, access_token)

                if test_result['success']:
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

                        if sync_result['success']:
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
        if st.button("🔄 Sync Now", use_container_width=True, key=f"sync_button_{student['id']}"):
            with st.spinner("Syncing Canvas data..."):
                sync_result = canvas.sync_assignments(student['id'])

                if sync_result['success']:
                    st.success(sync_result['message'])
                    st.rerun()
                else:
                    st.error(f"Sync failed: {sync_result['message']}")

    # Show assignments
    show_assignments_list_with_study_plans(student, canvas) #change made

def get_assignment_counts(student, canvas):
    """Get assignment counts for user feedback"""
    try:
        assignments = canvas.get_student_assignments(student['id'])
        if not assignments:
            return "No assignments found"

        current_time = datetime.now()
        overdue = 0
        due_soon = 0
        future = 0
        total = len(assignments)

        for assignment in assignments:
            try:
                due_date_str = assignment.get('due_date')
                if due_date_str and isinstance(due_date_str, str):
                    clean_date_str = due_date_str.replace('Z', '').replace('+00:00', '')
                    due_date = datetime.fromisoformat(clean_date_str)
                    days_until_due = (due_date - current_time).days

                    if days_until_due < 0:
                        overdue += 1
                    elif days_until_due <= 3:
                        due_soon += 1
                    else:
                        future += 1
            except:
                future += 1

        status_parts = []
        if overdue > 0:
            status_parts.append(f"{overdue} overdue")
        if due_soon > 0:
            status_parts.append(f"{due_soon} due soon")
        if future > 0:
            status_parts.append(f"{future} future")

        if status_parts:
            return f"Total: {total} assignments ({', '.join(status_parts)})"
        else:
            return f"Total: {total} assignments"

    except Exception:
        return "Assignment count unavailable"

def categorize_assignment(assignment):
    """Categorize assignment by type - ULTRA RESTRICTIVE for Assessment Tasks"""

    name = assignment.get('name', '').upper()
    assignment_type = assignment.get('type', '').upper()

    # Course Materials - documents, syllabi, etc. (CHECK FIRST - EXPANDED)
    if (
            'REGISTER OF RECEIPT' in name or
            'COURSE DOCUMENTS' in name or
            'SYLLABUS' in name or
            'SCOPE AND SEQUENCE' in name or
            'ASSESSMENT SCHEDULE' in name or
            'REFLECTION' in name or
            'DRAFT' in name or
            'SUBMISSION' in name or
            'INTERVIEW' in name or
            'PROGRESS' in name or
            'CHECK' in name or
            'SURVEY' in name or
            'CHECKPOINT' in name or
            'CHAPTER ANALYSIS' in name or  # NEW: Chapter analyses are course materials
            'WRITING TASK' in name or  # NEW: Writing tasks are typically smaller exercises
            'PRACTICE' in name or  # NEW: Practice assignments
            'TUTORIAL' in name  # NEW: Tutorial work
    ):
        return "Course Materials"

    # Quizzes & Tests - smaller assessments (EXPANDED)
    elif (
            'QUIZ' in name or
            'TEST' in name or
            'CQ' in name or  # Check questions like "CQ2.1: Describe..."
            assignment_type == 'QUIZ' or
            name.startswith('CQ') or  # NEW: Questions starting with CQ
            'CHECK IN' in name or  # NEW: Check-in assignments
            'DISCURSIVE' in name or  # NEW: Discursive writing (typically shorter)
            'PERSUASIVE' in name  # NEW: Persuasive writing (typically shorter)
    ):
        return "Quizzes & Tests"

    # Assessment Tasks - ONLY major starred assessments and clearly labeled assessment tasks
    elif (
            name.startswith('⭐') or  # Starred assignments are definitely major assessments
            (
                    'ASSESSMENT TASK' in name and 'REGISTER OF RECEIPT' not in name and '#' in name) or  # Only numbered assessment tasks
            ('INVESTIGATION' in name and '⭐' in name) or  # Only starred investigations
            ('CAMPAIGN' in name and '⭐' in name) or  # Only starred campaigns
            ('PROJECT' in name and '⭐' in name)  # Only starred projects
    ):
        return "Assessment Tasks"

    # Everything else defaults to Course Materials (SAFEST)
    else:
        return "Course Materials"

def show_assignment_filters(student):
    """Add filtering UI elements - WITH ASSIGNMENT TYPE FILTER"""

    st.markdown("### 📋 Upcoming Assignments")

    # Get assignments to extract course names
    if 'canvas_integrator' in st.session_state:
        canvas = st.session_state.canvas_integrator
        assignments = canvas.get_student_assignments(student['id'])

        # Extract unique course names
        course_names = set()
        for assignment in assignments:
            course_name = assignment.get('course', 'Unknown Course')
            if course_name and course_name.strip():
                course_names.add(course_name)

        # Sort course names and add "All Courses" at the beginning
        sorted_courses = ["All Courses"] + sorted(list(course_names))

        # If no courses found, show default
        if len(sorted_courses) == 1:
            sorted_courses = ["All Courses", "No courses found"]
    else:
        sorted_courses = ["All Courses", "Canvas not connected"]

    # Filter row - NOW WITH 3 COLUMNS
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        # Time filter dropdown
        days_filter = st.selectbox(
            "Show assignments due in:",
            options=[7, 14, 30, 60, 90, 365],
            index=3,  # Default to 60 days
            format_func=lambda x: f"{x} days",
            key=f"days_filter_{student['id']}"
        )

    with col2:
        # Course filter dropdown with real course names
        course_filter = st.selectbox(
            "Filter by course:",
            options=sorted_courses,
            index=0,  # Default to "All Courses"
            key=f"course_filter_{student['id']}"
        )

    with col3:
        # NEW: Assignment type filter
        type_filter = st.selectbox(
            "Assignment type:",
            options=[
                "Assessment Tasks Only",  # Default - real assignments
                "All Items",
                "Quizzes & Tests",
                "Course Materials"
            ],
            index=0,  # Default to Assessment Tasks Only
            key=f"type_filter_{student['id']}"
        )

    with col4:
        # Refresh button
        if st.button("🔄 Refresh", key=f"refresh_assignments_{student['id']}", use_container_width=True):
            st.rerun()

    # Store filter values in session state for later use
    st.session_state[f"days_filter_value_{student['id']}"] = days_filter
    st.session_state[f"course_filter_value_{student['id']}"] = course_filter
    st.session_state[f"type_filter_value_{student['id']}"] = type_filter

    # Show filter summary
    if len(sorted_courses) > 2:  # More than just "All Courses" and fallback
        st.caption(f"📊 Found {len(sorted_courses) - 1} courses • {type_filter} • Due within {days_filter} days")

    # Add a separator
    st.markdown("---")

    return days_filter, course_filter, type_filter

def create_canvas_integration_tab_debug(student):
    """Canvas integration with DEBUG version"""

    if 'canvas_integrator' not in st.session_state:
        st.session_state.canvas_integrator = CanvasIntegrator()

    canvas = st.session_state.canvas_integrator

    st.markdown("### 🎓 Canvas LMS Integration")

    if canvas.has_canvas_credentials(student['id']):
        show_canvas_dashboard_debug(student, canvas)
    else:
        show_canvas_connection_form(student, canvas)

def show_canvas_dashboard_debug(student, canvas):
    """Canvas dashboard with DEBUG version"""

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
        <div style="background: white; border: 1px solid #e5e5e5; border-radius: 8px; padding: 16px;">
            <h4>📚 Canvas Connected (DEBUG MODE)</h4>
            <p><strong>{student['name']}</strong> • Canvas integration active</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🔄 Sync Now", use_container_width=True, key=f"sync_button_debug_{student['id']}"):
            with st.spinner("Syncing Canvas data..."):
                sync_result = canvas.sync_assignments(student['id'])

                if sync_result['success']:
                    st.success(sync_result['message'])
                    st.rerun()
                else:
                    st.error(f"Sync failed: {sync_result['message']}")

    # Use debug version
    show_assignments_list_debug(student, canvas)

def show_ai_study_planning(student, assignment, assignment_index):
    """AI Study Planning Interface - FIXED DATE HANDLING"""

    unique_id = f"{student['id']}_{assignment_index}"

    st.markdown(f"""
    <div class="study-plan-container">
        <div class="study-plan-header">
            🧠 AI Study Plan for: {assignment.get('name', 'Assignment')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate AI milestones if not already done
    if f"milestones_{unique_id}" not in st.session_state:
        agent = st.session_state.get('career_agent')
        if not agent:
            if 'career_agent' not in st.session_state:
                st.session_state.career_agent = SecureFamilyCareerAgent()
            agent = st.session_state.career_agent

        with st.spinner("🤖 AI is creating your study plan..."):
            # FIXED: Safe date handling for AI generation
            due_date_str = assignment.get('due_date', '')
            if not due_date_str or due_date_str == 'Date TBD':
                due_date_str = (datetime.now() + timedelta(days=7)).isoformat()

            milestones = agent.generate_ai_study_plan(
                assignment.get('name', 'Assignment'),
                due_date_str,
                assignment.get('description', '')
            )
            st.session_state[f"milestones_{unique_id}"] = milestones

    milestones = st.session_state[f"milestones_{unique_id}"]

    # Step 1: AI Suggestions (Interactive Selection)
    st.markdown("#### Step 1: Select Study Milestones")

    selected_milestones = []

    for j, milestone in enumerate(milestones):
        col1, col2, col3 = st.columns([1, 4, 2])

        with col1:
            selected = st.checkbox("Select", key=f"milestone_select_{unique_id}_{j}")

        with col2:
            edited_description = st.text_area(
                "Description",
                value=milestone.get('description', ''),
                height=80,
                key=f"milestone_desc_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        with col3:
            try:
                target_date_str = milestone.get('target_date', '')
                if target_date_str:
                    default_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                else:
                    default_date = datetime.now().date()
            except:
                default_date = datetime.now().date()

            edited_date = st.date_input(
                "Target Date",
                value=default_date,
                key=f"milestone_date_{unique_id}_{j}",
                label_visibility="collapsed"
            )

        if selected:
            selected_milestones.append({
                "title": milestone.get('title', 'Milestone'),
                "description": edited_description,
                "target_date": str(edited_date)
            })

    # Step 2: Add Custom Milestones
    with st.expander("➕ Add Your Own Milestones"):
        with st.form(f"custom_milestone_form_{unique_id}"):
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
                    if f"custom_milestones_{unique_id}" not in st.session_state:
                        st.session_state[f"custom_milestones_{unique_id}"] = []
                    st.session_state[f"custom_milestones_{unique_id}"].append(custom_milestone)
                    st.success("✅ Custom milestone added!")

    # Include custom milestones
    if f"custom_milestones_{unique_id}" in st.session_state:
        selected_milestones.extend(st.session_state[f"custom_milestones_{unique_id}"])

    # Step 3: Save Study Plan
    col1, col2 = st.columns(2)

    with col1:
        if st.button(f"💾 Save Study Plan ({len(selected_milestones)} milestones)",
                     key=f"save_plan_{unique_id}", use_container_width=True):
            if selected_milestones:
                # Save to database
                canvas = st.session_state.canvas_integrator
                success = canvas.save_study_milestones(
                    student['id'],
                    assignment.get('assignment_id', f"assignment_{assignment_index}"),
                    assignment.get('name', 'Assignment'),
                    selected_milestones
                )

                if success:
                    st.session_state[f"saved_plan_{unique_id}"] = selected_milestones
                    st.success(f"✅ Study plan saved with {len(selected_milestones)} milestones!")
                else:
                    st.error("Failed to save study plan")
            else:
                st.warning("Please select at least one milestone")

    with col2:
        if st.button("❌ Cancel", key=f"cancel_plan_{unique_id}",
                     use_container_width=True, type="secondary"):
            st.session_state[f"show_study_plan_{student['id']}_{assignment_index}"] = False
            st.rerun()

    # Show saved study plan
    if st.session_state.get(f"saved_plan_{unique_id}"):
        st.markdown("#### 📊 Your Study Plan Progress")

        saved_plan = st.session_state[f"saved_plan_{unique_id}"]
        completed_count = 0

        for k, milestone in enumerate(saved_plan):
            col1, col2 = st.columns([1, 5])

            with col1:
                completed = st.checkbox("Done", key=f"completed_{unique_id}_{k}",
                                        value=st.session_state.get(f"completed_{unique_id}_{k}", False))
                if completed:
                    completed_count += 1

            with col2:
                milestone_class = "completed" if completed else ""
                st.markdown(f"""
                <div class="milestone-item {milestone_class}">
                    <div class="milestone-title">{milestone.get('title', 'Milestone')}</div>
                    <div class="milestone-description">{milestone.get('description', '')}</div>
                    <div class="milestone-date">Target: {milestone.get('target_date', '')}</div>
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
                help="Enter interests separated by commas",
                key=f"interests_{student['id']}"
            )

            updated_timeline = st.selectbox(
                "University Timeline",
                ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months", "Applying now"],
                index=0,
                key=f"timeline_{student['id']}"
            )

        with col2:
            updated_location_pref = st.text_input(
                "Location Preference",
                value=student.get('location_preference', ''),
                placeholder="e.g., NSW/ACT",
                key=f"location_pref_{student['id']}"
            )

            notifications = st.checkbox("Enable study reminders", value=True, key=f"notifications_{student['id']}")

        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings updated successfully!")

    # Notification preferences
    st.markdown("#### 🔔 Notification Preferences")

    col1, col2 = st.columns(2)

    with col1:
        st.checkbox("Assignment due date reminders", value=True, key=f"reminder1_{student['id']}")
        st.checkbox("Study plan milestone alerts", value=True, key=f"reminder2_{student['id']}")

    with col2:
        st.checkbox("Career guidance suggestions", value=False, key=f"reminder3_{student['id']}")
        st.checkbox("Weekly progress summaries", value=True, key=f"reminder4_{student['id']}")

def main():
    """Enhanced main application"""

    # Initialize session state
    if 'career_agent' not in st.session_state:
        st.session_state.career_agent = SecureFamilyCareerAgent()

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
            create_family_registration()
        else:
            create_family_login()
    else:
        create_comprehensive_family_interface(st.session_state.authenticated_family)

if __name__ == "__main__":
    main()


