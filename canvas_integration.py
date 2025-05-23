import streamlit as st
import sqlite3
import requests
import json
import anthropic
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class CanvasIntegrator:
    """Simplified Canvas integration for the family app"""

    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_canvas_tables()

    def init_canvas_tables(self):
        """Initialize Canvas tables in existing database"""
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
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_sync DATETIME,
                FOREIGN KEY (student_id) REFERENCES students (id),
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
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id),
                UNIQUE(student_id, assignment_id)
            )
        ''')

        # Simple milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS simple_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                assignment_name TEXT,
                title TEXT,
                description TEXT,
                target_date TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        conn.commit()
        conn.close()

    def test_canvas_connection(self, canvas_url: str, access_token: str) -> Dict:
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
                    'status': 'success',
                    'user_name': user_data.get('name', 'Unknown'),
                    'user_id': str(user_data.get('id', '')),
                    'login_id': user_data.get('login_id', '')
                }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}: Authentication failed'
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            }

    def save_canvas_credentials(self, student_id: str, canvas_url: str,
                                access_token: str, user_name: str, canvas_user_id: str) -> bool:
        """Save Canvas credentials for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO canvas_credentials 
                (student_id, canvas_url, access_token, student_name, canvas_user_id, last_sync)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, canvas_url, access_token, user_name, canvas_user_id,
                  datetime.now().isoformat()))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            st.error(f"Error saving credentials: {e}")
            return False

    def get_canvas_credentials(self, student_id: str) -> Optional[Dict]:
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

        except Exception as e:
            st.error(f"Error retrieving credentials: {e}")
            return None

    def sync_assignments(self, student_id: str) -> Dict:
        """Sync assignments AND quizzes/exams from Canvas"""
        credentials = self.get_canvas_credentials(student_id)
        if not credentials:
            return {'status': 'error', 'message': 'No Canvas credentials found'}

        try:
            canvas_url = credentials['canvas_url']
            access_token = credentials['access_token']

            # Get courses
            courses_response = requests.get(
                f"{canvas_url}/api/v1/courses",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"enrollment_state": "active", "per_page": 50},
                timeout=15
            )

            if courses_response.status_code != 200:
                return {'status': 'error', 'message': 'Failed to fetch courses'}

            courses = courses_response.json()
            total_assignments = 0
            total_exams = 0

            # Get assignments and quizzes from each course
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing assignments for this student
            cursor.execute('DELETE FROM canvas_assignments WHERE student_id = ?', (student_id,))

            for course in courses:
                course_id = course['id']
                course_name = course.get('name', 'Unknown Course')

                # Sync regular assignments
                assignment_count = self._sync_course_assignments(
                    cursor, student_id, course_id, course_name, canvas_url, access_token
                )
                total_assignments += assignment_count

                # Sync quizzes/exams
                quiz_count = self._sync_course_quizzes(
                    cursor, student_id, course_id, course_name, canvas_url, access_token
                )
                total_exams += quiz_count

            # Update last sync time
            cursor.execute('''
                UPDATE canvas_credentials 
                SET last_sync = ? 
                WHERE student_id = ?
            ''', (datetime.now().isoformat(), student_id))

            conn.commit()
            conn.close()

            total_items = total_assignments + total_exams

            return {
                'status': 'success',
                'message': f'Synced {total_assignments} assignments and {total_exams} exams from {len(courses)} courses',
                'assignments_count': total_assignments,
                'exams_count': total_exams,
                'total_count': total_items,
                'courses_count': len(courses)
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Sync failed: {str(e)}'
            }

    def _sync_course_assignments(self, cursor, student_id: str, course_id: int,
                                 course_name: str, canvas_url: str, access_token: str) -> int:
        """Sync assignments for a specific course"""
        try:
            assignments_response = requests.get(
                f"{canvas_url}/api/v1/courses/{course_id}/assignments",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"per_page": 50, "order_by": "due_at"},
                timeout=15
            )

            if assignments_response.status_code != 200:
                return 0

            assignments = assignments_response.json()
            count = 0

            for assignment in assignments:
                try:
                    due_date = self._parse_due_date(assignment.get('due_at'))
                    points_possible = self._safe_float(assignment.get('points_possible'), 0)

                    assignment_name = assignment.get('name') or 'Unnamed Assignment'
                    description = assignment.get('description') or ''
                    html_url = assignment.get('html_url') or ''
                    is_quiz_assignment = assignment.get('is_quiz_assignment', False)
                    assignment_id = str(assignment.get('id', f'unknown_{count}'))

                    cursor.execute('''
                        INSERT OR REPLACE INTO canvas_assignments
                        (student_id, assignment_id, course_name, assignment_name, 
                         due_date, points_possible, description, html_url, is_quiz)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        student_id, assignment_id, course_name, assignment_name,
                        due_date.isoformat() if due_date else None,
                        points_possible, description[:500], html_url, bool(is_quiz_assignment)
                    ))

                    count += 1

                except Exception as e:
                    print(f"Error processing assignment in {course_name}: {e}")
                    continue

            return count

        except Exception as e:
            print(f"Error syncing assignments for {course_name}: {e}")
            return 0

    def _sync_course_quizzes(self, cursor, student_id: str, course_id: int,
                             course_name: str, canvas_url: str, access_token: str) -> int:
        """Sync quizzes/exams for a specific course"""
        try:
            quizzes_response = requests.get(
                f"{canvas_url}/api/v1/courses/{course_id}/quizzes",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"per_page": 50},
                timeout=15
            )

            if quizzes_response.status_code != 200:
                return 0

            quizzes = quizzes_response.json()
            count = 0

            for quiz in quizzes:
                try:
                    if not quiz or not isinstance(quiz, dict):
                        continue

                    quiz_id = quiz.get('id')
                    if not quiz_id:
                        continue

                    # Check if already exists as assignment
                    cursor.execute('''
                        SELECT COUNT(*) FROM canvas_assignments 
                        WHERE student_id = ? AND assignment_id = ?
                    ''', (student_id, str(quiz_id)))

                    if cursor.fetchone()[0] > 0:
                        continue  # Already exists as assignment

                    due_date = self._parse_due_date(quiz.get('due_at'))
                    points_possible = self._safe_float(quiz.get('points_possible'), 0)

                    quiz_title = quiz.get('title') or 'Unnamed Quiz/Exam'
                    description = quiz.get('description') or ''
                    html_url = quiz.get('html_url') or ''

                    cursor.execute('''
                        INSERT OR REPLACE INTO canvas_assignments
                        (student_id, assignment_id, course_name, assignment_name, 
                         due_date, points_possible, description, html_url, is_quiz)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        student_id, f"quiz_{quiz_id}", course_name, quiz_title,
                        due_date.isoformat() if due_date else None,
                        points_possible, description[:500], html_url, True
                    ))

                    count += 1

                except Exception as e:
                    print(f"Error processing quiz in {course_name}: {e}")
                    continue

            return count

        except Exception as e:
            print(f"Error syncing quizzes for {course_name}: {e}")
            return 0

    def _parse_due_date(self, due_at_str: str) -> Optional[datetime]:
        """Safely parse due date string"""
        if not due_at_str:
            return None

        try:
            due_date = datetime.fromisoformat(due_at_str.replace('Z', '+00:00'))
            # Convert to timezone-naive for consistent storage
            if due_date.tzinfo is not None:
                due_date = due_date.replace(tzinfo=None)
            return due_date
        except:
            return None

    def _safe_float(self, value, default=0.0) -> float:
        """Safely convert value to float"""
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_upcoming_assignments(self, student_id: str, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming assignments for a student"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            today = datetime.now()
            future_date = today + timedelta(days=days_ahead)

            cursor.execute('''
                SELECT course_name, assignment_name, due_date, points_possible, 
                       html_url, description, is_quiz, assignment_id
                FROM canvas_assignments
                WHERE student_id = ? 
                AND due_date IS NOT NULL
                AND due_date >= ?
                AND due_date <= ?
                ORDER BY due_date ASC
            ''', (student_id, today.isoformat(), future_date.isoformat()))

            assignments = []
            for row in cursor.fetchall():
                due_date = self._parse_due_date(row[2]) if row[2] else None

                assignments.append({
                    'course_name': row[0],
                    'assignment_name': row[1],
                    'due_date': due_date,
                    'points_possible': row[3],
                    'html_url': row[4],
                    'description': row[5],
                    'is_quiz': bool(row[6]),
                    'assignment_id': row[7]
                })

            conn.close()
            return assignments

        except Exception as e:
            st.error(f"Error retrieving assignments: {e}")
            return []


class SimpleMilestoneGenerator:
    """Simple milestone generator for study planning"""

    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path

        # Try to initialize AI client
        try:
            api_key = st.secrets.get("ANTHROPIC_API_KEY")
            if not api_key:
                try:
                    import os
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.getenv("ANTHROPIC_API_KEY")
                except:
                    pass

            self.ai_client = anthropic.Anthropic(api_key=api_key) if api_key else None
        except:
            self.ai_client = None

    def create_milestones_for_assignment(self, student, assignment):
        """Create milestones using AI or fallback method"""
        if self.ai_client:
            return self._create_ai_milestones(student, assignment)
        else:
            return self._create_fallback_milestones(assignment)

    def _create_ai_milestones(self, student, assignment):
        """Create milestones using AI"""
        try:
            due_date = assignment['due_date']
            days_available = (due_date - datetime.now()).days if due_date else 14

            prompt = f"""Create a study plan for this Australian high school assignment:

Assignment: {assignment['assignment_name']}
Course: {assignment['course_name']} 
Due: {due_date.strftime('%d %B %Y') if due_date else 'Soon'}
Points: {assignment['points_possible']}
Days available: {days_available}

Create 4 specific study milestones as JSON:
[
  {{"title": "Research & Planning", "description": "Specific research tasks for this assignment", "days_before_due": 7}},
  {{"title": "First Draft", "description": "Writing/creation tasks", "days_before_due": 4}},
  {{"title": "Review & Edit", "description": "Improvement tasks", "days_before_due": 2}},
  {{"title": "Final Polish", "description": "Final preparation", "days_before_due": 1}}
]"""

            response = self.ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            ai_text = response.content[0].text
            start_idx = ai_text.find('[')
            end_idx = ai_text.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                milestones_data = json.loads(ai_text[start_idx:end_idx])

                milestones = []
                for milestone_data in milestones_data:
                    target_date = due_date - timedelta(days=milestone_data.get('days_before_due', 1))

                    if target_date <= datetime.now():
                        target_date = datetime.now() + timedelta(days=1)

                    milestones.append({
                        'title': milestone_data.get('title', 'Study Task'),
                        'description': milestone_data.get('description', 'Work on assignment'),
                        'target_date': target_date
                    })

                self._save_milestones(student, assignment, milestones)
                return milestones

        except Exception as e:
            print(f"AI milestone generation failed: {e}")

        return self._create_fallback_milestones(assignment)

    def _create_fallback_milestones(self, assignment):
        """Create basic milestones without AI"""
        due_date = assignment['due_date']
        days_available = max((due_date - datetime.now()).days, 1) if due_date else 14

        milestones = [
            {
                'title': 'Research & Planning',
                'description': f'Research topic and create outline for {assignment["assignment_name"]}',
                'target_date': due_date - timedelta(days=min(7, days_available - 1))
            },
            {
                'title': 'First Draft',
                'description': 'Write first draft focusing on main content',
                'target_date': due_date - timedelta(days=min(4, days_available - 1))
            },
            {
                'title': 'Review & Edit',
                'description': 'Review content, improve structure and arguments',
                'target_date': due_date - timedelta(days=min(2, days_available - 1))
            },
            {
                'title': 'Final Polish',
                'description': 'Proofread, format, and prepare final submission',
                'target_date': due_date - timedelta(days=1)
            }
        ]

        # Adjust dates that are in the past
        for milestone in milestones:
            if milestone['target_date'] <= datetime.now():
                milestone['target_date'] = datetime.now() + timedelta(hours=12)

        self._save_milestones({'id': 'student'}, assignment, milestones)
        return milestones

    def _save_milestones(self, student, assignment, milestones):
        """Save milestones to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            assignment_id = assignment.get('assignment_id', str(hash(assignment['assignment_name'])))
            student_id = student.get('id', 'student')

            # Clear existing milestones
            cursor.execute('DELETE FROM simple_milestones WHERE student_id = ? AND assignment_id = ?',
                           (student_id, assignment_id))

            # Save new milestones
            for milestone in milestones:
                cursor.execute('''
                    INSERT INTO simple_milestones 
                    (student_id, assignment_id, assignment_name, title, description, target_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    student_id,
                    assignment_id,
                    assignment['assignment_name'],
                    milestone['title'],
                    milestone['description'],
                    milestone['target_date'].isoformat()
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving milestones: {e}")

    def get_milestones_for_assignment(self, student_id, assignment_id):
        """Get milestones for an assignment"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, title, description, target_date, completed
                FROM simple_milestones
                WHERE student_id = ? AND assignment_id = ?
                ORDER BY target_date
            ''', (student_id, assignment_id))

            milestones = []
            for row in cursor.fetchall():
                milestones.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'target_date': row[3],
                    'completed': bool(row[4])
                })

            conn.close()
            return milestones

        except Exception as e:
            print(f"Error getting milestones: {e}")
            return []

    def mark_milestone_completed(self, milestone_id):
        """Mark milestone as completed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('UPDATE simple_milestones SET completed = TRUE WHERE id = ?', (milestone_id,))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error marking milestone complete: {e}")
            return False


# UI Functions
def show_canvas_setup(student, canvas_integrator):
    """Show Canvas setup interface for a student"""
    # Check if already connected
    credentials = canvas_integrator.get_canvas_credentials(student['id'])

    if credentials:
        show_canvas_dashboard(student, canvas_integrator, credentials)
    else:
        show_canvas_connection_form(student, canvas_integrator)


def show_canvas_connection_form(student, canvas_integrator):
    """Show Canvas connection form"""
    st.markdown(f"""
    <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 20px; margin: 16px 0;">
        <h4>🔗 Connect Canvas Account</h4>
        <p>Connect {student['name']}'s Canvas account to automatically sync assignments and due dates.</p>
    </div>
    """, unsafe_allow_html=True)

    # Instructions
    with st.expander("📋 How to get your Canvas access token", expanded=False):
        st.markdown("""
        **Step-by-step instructions:**

        1. **Log into Canvas** (e.g., `lambtonhs.instructure.com`)
        2. **Click your profile picture** → **Settings**
        3. **Scroll to "Approved Integrations"**
        4. **Click "+ New Access Token"**
        5. **Purpose:** Enter "CareerPath Family App"
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
                value="https://lambtonhs.instructure.com/",
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
                test_result = canvas_integrator.test_canvas_connection(canvas_url, access_token)

                if test_result['status'] == 'success':
                    # Save credentials
                    success = canvas_integrator.save_canvas_credentials(
                        student['id'], canvas_url, access_token,
                        test_result['user_name'], test_result['user_id']
                    )

                    if success:
                        st.success(f"""
                        ✅ **Canvas Connected Successfully!**

                        Connected as: **{test_result['user_name']}**

                        Now syncing assignments...
                        """)

                        # Initial sync
                        sync_result = canvas_integrator.sync_assignments(student['id'])
                        if sync_result['status'] == 'success':
                            st.success(f"🎉 {sync_result['message']}")
                            st.balloons()
                            st.rerun()
                        else:
                            st.warning(f"Canvas connected but sync had issues: {sync_result['message']}")
                    else:
                        st.error("Failed to save Canvas credentials")
                else:
                    st.error(f"❌ **Connection Failed:** {test_result['message']}")


def show_canvas_dashboard(student, canvas_integrator, credentials):
    """Show Canvas dashboard for connected student"""

    # Dashboard header
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        last_sync = credentials.get('last_sync')
        if last_sync:
            sync_time = datetime.fromisoformat(last_sync)
            hours_ago = (datetime.now() - sync_time).total_seconds() / 3600

            if hours_ago < 1:
                sync_status = "🟢 Recently synced"
            elif hours_ago < 24:
                sync_status = f"🟡 Synced {int(hours_ago)} hours ago"
            else:
                sync_status = f"🔴 Synced {int(hours_ago / 24)} days ago"
        else:
            sync_status = "🔴 Never synced"

        st.markdown(f"""
        <div style="background: white; border: 1px solid #e5e5e5; border-radius: 8px; padding: 16px;">
            <h4>📚 Canvas Connected</h4>
            <p><strong>{credentials['student_name']}</strong> • {sync_status}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("🔄 Sync Now", use_container_width=True):
            with st.spinner("Syncing Canvas data..."):
                sync_result = canvas_integrator.sync_assignments(student['id'])

                if sync_result['status'] == 'success':
                    st.success(sync_result['message'])
                    st.rerun()
                else:
                    st.error(f"Sync failed: {sync_result['message']}")

    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state[f'canvas_settings_{student["id"]}'] = True

    # Show settings if requested
    if st.session_state.get(f'canvas_settings_{student["id"]}', False):
        st.markdown("---")
        show_canvas_settings(student, canvas_integrator)
        return

    # Show assignments and milestones
    show_enhanced_assignments_table(student, canvas_integrator)
    show_milestone_section(student, canvas_integrator)


def show_canvas_settings(student, canvas_integrator):
    """Show Canvas settings"""
    st.markdown(f"#### ⚙️ Canvas Settings - {student['name']}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔍 Test Connection", use_container_width=True):
            credentials = canvas_integrator.get_canvas_credentials(student['id'])
            if credentials:
                test_result = canvas_integrator.test_canvas_connection(
                    credentials['canvas_url'], credentials['access_token']
                )

                if test_result['status'] == 'success':
                    st.success(f"✅ Connection working! Logged in as: {test_result['user_name']}")
                else:
                    st.error(f"❌ Connection failed: {test_result['message']}")

    with col2:
        if st.button("🗑️ Remove Canvas", use_container_width=True, type="secondary"):
            # Remove Canvas integration
            conn = sqlite3.connect(canvas_integrator.db_path)
            cursor = conn.cursor()

            cursor.execute('UPDATE canvas_credentials SET is_active = FALSE WHERE student_id = ?', (student['id'],))
            cursor.execute('DELETE FROM canvas_assignments WHERE student_id = ?', (student['id'],))
            cursor.execute('DELETE FROM simple_milestones WHERE student_id = ?', (student['id'],))

            conn.commit()
            conn.close()

            st.success("Canvas integration removed")
            del st.session_state[f'canvas_settings_{student["id"]}']
            st.rerun()

    if st.button("← Back to Dashboard"):
        del st.session_state[f'canvas_settings_{student["id"]}']
        st.rerun()


def show_enhanced_assignments_table(student, canvas_integrator):
    """Show assignments in a clean table"""
    st.markdown("#### 📝 Upcoming Assignments")

    # Get assignments
    assignments = canvas_integrator.get_upcoming_assignments(student['id'], days_ahead=60)

    if not assignments:
        st.info("No upcoming assignments found. Try syncing again or check if assignments have due dates set.")

        if st.button("🔄 Try Syncing Again"):
            with st.spinner("Syncing..."):
                sync_result = canvas_integrator.sync_assignments(student['id'])
                st.success(sync_result['message'])
                st.rerun()
        return

    # Filter controls
    col1, col2 = st.columns(2)

    with col1:
        days_filter = st.selectbox("Show assignments due in:", [7, 14, 30, 60], index=2)

    with col2:
        course_names = sorted(list(set([a['course_name'] for a in assignments])))
        course_filter = st.selectbox("Filter by course:", ['All Courses'] + course_names)

    # Filter assignments
    filtered_assignments = []
    cutoff_date = datetime.now() + timedelta(days=days_filter)

    for assignment in assignments:
        if assignment['due_date'] and assignment['due_date'] > cutoff_date:
            continue

        if course_filter != 'All Courses' and assignment['course_name'] != course_filter:
            continue

        filtered_assignments.append(assignment)

    if not filtered_assignments:
        st.info("No assignments match your filters.")
        return

    # Create assignments table
    table_data = []
    for assignment in filtered_assignments:
        due_date = assignment['due_date']

        if due_date:
            try:
                days_until = (due_date - datetime.now()).days

                if days_until < 0:
                    urgency = "🔴 Overdue"
                    due_text = f"Overdue ({abs(days_until)} days)"
                elif days_until <= 2:
                    urgency = "🔴 Urgent"
                    due_text = f"{days_until} days"
                elif days_until <= 7:
                    urgency = "🟡 Soon"
                    due_text = f"{days_until} days"
                else:
                    urgency = "🟢 Future"
                    due_text = f"{days_until} days"

                date_str = due_date.strftime('%d %b %Y')

            except Exception:
                urgency = "⚪ Date error"
                due_text = "Date error"
                date_str = "Date error"
        else:
            urgency = "⚪ No date"
            due_text = "No date"
            date_str = "No date"

        assignment_type = "🧪 Quiz/Exam" if assignment['is_quiz'] else "📝 Assignment"

        table_data.append({
            'Type': assignment_type,
            'Assignment': assignment['assignment_name'],
            'Course': assignment['course_name'],
            'Due Date': date_str,
            'Days Left': due_text,
            'Points': int(assignment['points_possible']),
            'Status': urgency
        })

    # Display as DataFrame
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Assignment": st.column_config.TextColumn("Assignment", width="large"),
                "Course": st.column_config.TextColumn("Course", width="medium"),
                "Due Date": st.column_config.TextColumn("Due Date", width="small"),
                "Days Left": st.column_config.TextColumn("Days Left", width="small"),
                "Points": st.column_config.NumberColumn("Points", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )

        st.markdown(f"**Total:** {len(filtered_assignments)} assignments")


def show_milestone_section(student, canvas_integrator):
    """Show AI milestone generation section"""
    st.markdown("---")
    st.markdown("### 🧠 AI Study Planning")

    # Initialize milestone generator
    if 'simple_milestone_generator' not in st.session_state:
        st.session_state.simple_milestone_generator = SimpleMilestoneGenerator()

    milestone_gen = st.session_state.simple_milestone_generator

    # Get assignments for milestone generation
    assignments = canvas_integrator.get_upcoming_assignments(student['id'], days_ahead=60)

    if not assignments:
        st.info("No assignments available for study planning.")
        return

    # Filter assignments suitable for milestone generation
    suitable_assignments = []
    for assignment in assignments:
        if assignment['due_date']:
            try:
                due_date = assignment['due_date']
                days_until = (due_date - datetime.now()).days
                if days_until > 2 and not assignment['is_quiz']:  # Only assignments, not quizzes
                    suitable_assignments.append(assignment)
            except:
                continue

    if not suitable_assignments:
        st.info("⏰ Current assignments are due very soon. Focus on final preparation!")
        return

    st.markdown("**Create AI study plans for your upcoming assignments:**")

    for assignment in suitable_assignments[:5]:  # Show first 5 suitable assignments
        show_milestone_option_for_assignment(student, assignment, milestone_gen)


def show_milestone_option_for_assignment(student, assignment, milestone_gen):
    """Show milestone generation option for a single assignment"""
    due_date = assignment['due_date']
    days_until = (due_date - datetime.now()).days if due_date else 0

    # Assignment info card
    with st.expander(f"📚 {assignment['assignment_name']} ({assignment['course_name']})", expanded=False):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"""
            **Course:** {assignment['course_name']}  
            **Due:** {due_date.strftime('%d %B %Y') if due_date else 'No date'}  
            **Points:** {assignment['points_possible']}  
            **Time available:** {days_until} days
            """)

            # Check if milestones already exist
            existing_milestones = milestone_gen.get_milestones_for_assignment(
                student['id'],
                assignment.get('assignment_id', str(hash(assignment['assignment_name'])))
            )

            if existing_milestones:
                show_existing_milestones(assignment, existing_milestones, milestone_gen)
            else:
                st.markdown("**Generate a smart study plan** that breaks this assignment into daily tasks:")
                st.markdown("• Research and planning phase")
                st.markdown("• Content development phase")
                st.markdown("• Writing/creation phase")
                st.markdown("• Review and finalisation phase")

        with col2:
            if not existing_milestones:
                if st.button(f"🧠 Generate Study Plan",
                             key=f"gen_{assignment.get('assignment_id', hash(assignment['assignment_name']))}",
                             use_container_width=True):
                    generate_milestones_for_assignment(student, assignment, milestone_gen)
            else:
                completed = len([m for m in existing_milestones if m.get('completed', False)])
                total = len(existing_milestones)
                st.metric("Progress", f"{completed}/{total}")

                if st.button("🔄 Regenerate",
                             key=f"regen_{assignment.get('assignment_id', hash(assignment['assignment_name']))}",
                             use_container_width=True):
                    generate_milestones_for_assignment(student, assignment, milestone_gen)


def show_existing_milestones(assignment, milestones, milestone_gen):
    """Show existing milestones"""
    st.markdown(f"**Study plan active** ({len(milestones)} milestones):")

    for i, milestone in enumerate(milestones, 1):
        target_date = milestone.get('target_date')
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date)

        days_until = (target_date - datetime.now()).days if target_date else 0
        completed = milestone.get('completed', False)

        if completed:
            status = "✅"
        elif days_until < 0:
            status = "🔴"
        elif days_until <= 1:
            status = "🟡"
        else:
            status = "🟢"

        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"{status} **{milestone['title']}** - {target_date.strftime('%d %b') if target_date else 'No date'}")
            st.markdown(f"   {milestone.get('description', '')[:100]}...")

        with col2:
            if not completed and st.button("✅", key=f"complete_{milestone.get('id', i)}", help="Mark complete"):
                milestone_gen.mark_milestone_completed(milestone.get('id', i))
                st.success("Completed!")
                st.rerun()


def generate_milestones_for_assignment(student, assignment, milestone_gen):
    """Generate milestones for assignment"""
    with st.spinner("🧠 Creating your personalised study plan..."):
        milestones = milestone_gen.create_milestones_for_assignment(student, assignment)

        if milestones:
            st.success(f"✨ Created {len(milestones)} study milestones!")
            st.balloons()

            # Show generated milestones
            st.markdown("**Your new study plan:**")
            for i, milestone in enumerate(milestones, 1):
                target_date = milestone.get('target_date')
                if isinstance(target_date, str):
                    target_date = datetime.fromisoformat(target_date)

                days_until = (target_date - datetime.now()).days if target_date else 0
                st.markdown(
                    f"**{i}. {milestone['title']}** - {target_date.strftime('%d %b') if target_date else 'Soon'} ({days_until} days)")
                st.markdown(f"   {milestone.get('description', '')}")

            st.rerun()
        else:
            st.error("Failed to generate study plan. Please try again.")


# Integration function for main app
def add_canvas_to_family_interface():
    """Add Canvas integration to the family interface"""
    if 'authenticated_family' not in st.session_state:
        return

    family_info = st.session_state.authenticated_family

    # Initialize Canvas integrator
    if 'canvas_integrator' not in st.session_state:
        st.session_state.canvas_integrator = CanvasIntegrator()

    canvas_integrator = st.session_state.canvas_integrator

    # Get students
    db = st.session_state.secure_db
    students = db.get_family_students(family_info['id'])

    if not students:
        return

    st.markdown("---")
    st.markdown("## 📚 Canvas LMS Integration")

    # Show Canvas status for each student
    for student in students:
        st.markdown(f"### 📚 Canvas - {student['name']}")
        show_canvas_setup(student, canvas_integrator)
        st.markdown("---")