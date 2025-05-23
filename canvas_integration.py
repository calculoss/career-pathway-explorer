import streamlit as st
import sqlite3
import requests
import json
import anthropic
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import traceback


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
    """Simple milestone generator for study planning with improved error handling"""

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

    def _create_ai_milestones_without_saving(self, student, assignment):
        """Create AI milestones but don't save them yet"""
        if not self.ai_client:
            return self._create_fallback_milestones_without_saving(assignment)

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

                return milestones

        except Exception as e:
            print(f"AI milestone generation failed: {e}")

        return self._create_fallback_milestones_without_saving(assignment)

    def _create_fallback_milestones_without_saving(self, assignment):
        """Create fallback milestones without saving"""
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

        return milestones

    def _safe_datetime_to_string(self, dt):
        """Safely convert datetime to ISO string"""
        if dt is None:
            return None

        if isinstance(dt, str):
            # Already a string, validate it's a valid datetime
            try:
                datetime.fromisoformat(dt)
                return dt
            except:
                return datetime.now().isoformat()

        if isinstance(dt, datetime):
            return dt.isoformat()

        # Fallback
        return datetime.now().isoformat()

    def _validate_inputs(self, student, assignment, milestones):
        """Validate inputs before saving to database"""
        errors = []

        # Validate student
        if not student or not isinstance(student, dict):
            errors.append("Invalid student data")
        elif 'id' not in student:
            errors.append("Student missing ID")

        # Validate assignment
        if not assignment or not isinstance(assignment, dict):
            errors.append("Invalid assignment data")
        elif 'assignment_name' not in assignment:
            errors.append("Assignment missing name")

        # Validate milestones
        if not milestones or not isinstance(milestones, list):
            errors.append("Invalid milestones data")
        elif len(milestones) == 0:
            errors.append("No milestones to save")

        # Validate each milestone
        for i, milestone in enumerate(milestones):
            if not isinstance(milestone, dict):
                errors.append(f"Milestone {i + 1} is not a dictionary")
                continue

            if 'title' not in milestone or not milestone['title']:
                errors.append(f"Milestone {i + 1} missing title")

            if 'description' not in milestone:
                errors.append(f"Milestone {i + 1} missing description")

            if 'target_date' not in milestone:
                errors.append(f"Milestone {i + 1} missing target_date")

        return errors

    def _save_milestones(self, student, assignment, milestones):
        """Save milestones to database with improved error handling"""
        try:
            # Validate inputs first
            validation_errors = self._validate_inputs(student, assignment, milestones)
            if validation_errors:
                error_msg = f"Validation failed: {'; '.join(validation_errors)}"
                st.error(error_msg)
                print(error_msg)
                return False

            assignment_id = assignment.get('assignment_id', str(hash(assignment['assignment_name'])))
            student_id = student.get('id', 'student')

            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()

            try:
                # Check if student exists in students table (if foreign key constraints are enabled)
                cursor.execute('SELECT COUNT(*) FROM students WHERE id = ?', (student_id,))
                student_exists = cursor.fetchone()[0] > 0

                if not student_exists:
                    # Create a placeholder student record if it doesn't exist
                    cursor.execute('''
                        INSERT OR IGNORE INTO students (id, family_id, name, age, year_level, interests)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (student_id, 'placeholder_family', student.get('name', 'Unknown'), 16, 11, '[]'))

                # Clear existing milestones for this assignment
                cursor.execute('DELETE FROM simple_milestones WHERE student_id = ? AND assignment_id = ?',
                               (student_id, assignment_id))

                # Save new milestones
                saved_count = 0
                for i, milestone in enumerate(milestones):
                    try:
                        # Safely convert target_date to string
                        target_date_str = self._safe_datetime_to_string(milestone['target_date'])

                        cursor.execute('''
                            INSERT INTO simple_milestones 
                            (student_id, assignment_id, assignment_name, title, description, target_date)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            student_id,
                            assignment_id,
                            assignment['assignment_name'][:200],  # Truncate long names
                            milestone['title'][:200],  # Truncate long titles
                            milestone['description'][:500],  # Truncate long descriptions
                            target_date_str
                        ))
                        saved_count += 1

                    except Exception as milestone_error:
                        error_msg = f"Error saving milestone {i + 1}: {str(milestone_error)}"
                        st.error(error_msg)
                        print(error_msg)

                conn.commit()
                return True

            except Exception as db_error:
                conn.rollback()
                error_msg = f"Database operation failed: {str(db_error)}"
                st.error(error_msg)
                print(error_msg)
                return False

            finally:
                conn.close()

        except Exception as e:
            error_msg = f"Error saving milestones: {str(e)}"
            st.error(error_msg)
            print(error_msg)
            return False

    def _save_single_milestone(self, student, assignment, milestone):
        """Save a single milestone to existing plan with improved error handling"""
        try:
            # Validate inputs
            validation_errors = self._validate_inputs(student, assignment, [milestone])
            if validation_errors:
                error_msg = f"Validation failed: {'; '.join(validation_errors)}"
                st.error(error_msg)
                return False

            assignment_id = assignment.get('assignment_id', str(hash(assignment['assignment_name'])))
            student_id = student.get('id', 'student')

            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()

            try:
                target_date_str = self._safe_datetime_to_string(milestone['target_date'])

                cursor.execute('''
                    INSERT INTO simple_milestones 
                    (student_id, assignment_id, assignment_name, title, description, target_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    student_id,
                    assignment_id,
                    assignment['assignment_name'][:200],
                    milestone['title'][:200],
                    milestone['description'][:500],
                    target_date_str
                ))

                conn.commit()
                return True

            except Exception as db_error:
                conn.rollback()
                error_msg = f"Database error saving single milestone: {str(db_error)}"
                st.error(error_msg)
                print(error_msg)
                return False

            finally:
                conn.close()

        except Exception as e:
            error_msg = f"Error saving single milestone: {str(e)}"
            st.error(error_msg)
            print(error_msg)
            return False

    def get_milestones_for_assignment(self, student_id, assignment_id):
        """Get milestones for an assignment with improved error handling"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
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
            st.error(f"Error getting milestones: {e}")
            return []

    def mark_milestone_completed(self, milestone_id):
        """Mark milestone as completed with improved error handling"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()

            cursor.execute('UPDATE simple_milestones SET completed = TRUE WHERE id = ?', (milestone_id,))

            if cursor.rowcount > 0:
                conn.commit()
                return True
            else:
                return False

        except Exception as e:
            st.error(f"Error marking milestone complete: {e}")
            return False

        finally:
            try:
                conn.close()
            except:
                pass

    def clear_milestones_for_assignment(self, student_id, assignment_id):
        """Clear existing milestones for an assignment with improved error handling"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM simple_milestones WHERE student_id = ? AND assignment_id = ?',
                           (student_id, assignment_id))

            conn.commit()
            return True

        except Exception as e:
            st.error(f"Error clearing milestones: {e}")
            return False

        finally:
            try:
                conn.close()
            except:
                pass


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
    """Interactive milestone selection system"""
    due_date = assignment['due_date']
    days_until = (due_date - datetime.now()).days if due_date else 0
    assignment_key = assignment.get('assignment_id', str(hash(assignment['assignment_name'])))

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

            # Check for existing milestones in tracker
            existing_milestones = milestone_gen.get_milestones_for_assignment(
                student['id'], assignment_key
            )

            if existing_milestones:
                show_existing_milestones_with_add_option(assignment, existing_milestones, milestone_gen, student)
            else:
                show_milestone_generation_and_selection(student, assignment, milestone_gen, assignment_key, days_until)

        with col2:
            if existing_milestones:
                # Show progress for existing milestones
                completed = len([m for m in existing_milestones if m.get('completed', False)])
                total = len(existing_milestones)
                st.metric("Progress", f"{completed}/{total}")

                if st.button("🔄 Start Over",
                             key=f"restart_{assignment_key}",
                             use_container_width=True):
                    # Clear existing milestones and start fresh
                    milestone_gen.clear_milestones_for_assignment(student['id'], assignment_key)
                    # Clear session state for this assignment
                    for key in list(st.session_state.keys()):
                        if assignment_key in key:
                            del st.session_state[key]
                    st.success("Cleared study plan. Generate a new one below!")
                    st.rerun()
            else:
                # Show generate button
                if st.button(f"🧠 Generate Study Plan Ideas",
                             key=f"gen_{assignment_key}",
                             use_container_width=True):
                    st.session_state[f"generate_for_{assignment_key}"] = True
                    st.rerun()


def show_milestone_generation_and_selection(student, assignment, milestone_gen, assignment_key, days_until):
    """Show AI generation and interactive selection interface"""

    # Check if we should generate milestones
    if st.session_state.get(f"generate_for_{assignment_key}", False):

        # Generate AI milestones (but don't save them yet)
        if f"ai_suggestions_{assignment_key}" not in st.session_state:
            with st.spinner("🧠 AI is creating study plan suggestions..."):
                try:
                    # Generate milestones but don't save them
                    ai_milestones = milestone_gen._create_ai_milestones_without_saving(student, assignment)
                    if not ai_milestones:
                        ai_milestones = milestone_gen._create_fallback_milestones_without_saving(assignment)

                    st.session_state[f"ai_suggestions_{assignment_key}"] = ai_milestones
                    st.success(f"✨ Generated {len(ai_milestones)} study plan suggestions!")

                except Exception as e:
                    st.error(f"Error generating suggestions: {str(e)}")
                    ai_milestones = milestone_gen._create_fallback_milestones_without_saving(assignment)
                    st.session_state[f"ai_suggestions_{assignment_key}"] = ai_milestones

        # Show the interactive selection interface
        ai_milestones = st.session_state[f"ai_suggestions_{assignment_key}"]
        show_milestone_selection_interface(student, assignment, milestone_gen, assignment_key, ai_milestones)

    else:
        # Show initial generation option
        st.markdown("**Get AI-powered study plan suggestions** that you can customise:")
        st.markdown("• Research and planning tasks")
        st.markdown("• Content development phases")
        st.markdown("• Review and finalisation steps")
        st.markdown("• **Choose which ones you want to keep!**")


def show_milestone_selection_interface(student, assignment, milestone_gen, assignment_key, ai_milestones):
    """Interactive interface for selecting and customising milestones"""

    st.markdown("### 🎯 Choose Your Study Plan")
    st.markdown("**Select which milestones you want to keep, edit them, and add your own:**")

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["🤖 AI Suggestions", "➕ Add Your Own"])

    with tab1:
        st.markdown("**AI-Generated Study Plan Suggestions:**")
        st.markdown("*Select the ones you want to keep and customise them:*")

        selected_milestones = []

        # Show each AI milestone with selection options
        for i, milestone in enumerate(ai_milestones):
            milestone_container = st.container()

            with milestone_container:
                # Checkbox to select this milestone
                selected = st.checkbox(
                    f"**{milestone['title']}**",
                    key=f"select_{assignment_key}_{i}",
                    value=True  # Default to selected
                )

                if selected:
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Editable description
                        custom_description = st.text_area(
                            "Description:",
                            value=milestone.get('description', ''),
                            key=f"desc_{assignment_key}_{i}",
                            height=70
                        )

                    with col2:
                        # Editable due date
                        target_date = milestone.get('target_date')
                        if isinstance(target_date, str):
                            target_date = datetime.fromisoformat(target_date)

                        custom_date = st.date_input(
                            "Target Date:",
                            value=target_date.date() if target_date else datetime.now().date(),
                            key=f"date_{assignment_key}_{i}"
                        )

                        # Convert back to datetime
                        custom_datetime = datetime.combine(custom_date, datetime.min.time())

                    # Add to selected milestones
                    selected_milestones.append({
                        'title': milestone['title'],
                        'description': custom_description,
                        'target_date': custom_datetime
                    })

                st.markdown("---")

        # Store selected milestones in session state
        st.session_state[f"selected_milestones_{assignment_key}"] = selected_milestones

    with tab2:
        st.markdown("**Add Your Own Custom Milestones:**")

        # Initialize custom milestones in session state
        if f"custom_milestones_{assignment_key}" not in st.session_state:
            st.session_state[f"custom_milestones_{assignment_key}"] = []

        custom_milestones = st.session_state[f"custom_milestones_{assignment_key}"]

        # Form to add new custom milestone
        with st.form(f"add_custom_{assignment_key}"):
            st.markdown("**Add a new milestone:**")

            col1, col2 = st.columns([2, 1])

            with col1:
                custom_title = st.text_input("Milestone Title:", placeholder="e.g., Meet with teacher for feedback")
                custom_desc = st.text_area("Description:",
                                           placeholder="e.g., Discuss essay structure and get clarification on requirements",
                                           height=70)

            with col2:
                custom_date = st.date_input("Target Date:", value=datetime.now().date())

            if st.form_submit_button("➕ Add Milestone"):
                if custom_title and custom_desc:
                    new_milestone = {
                        'title': custom_title,
                        'description': custom_desc,
                        'target_date': datetime.combine(custom_date, datetime.min.time())
                    }
                    st.session_state[f"custom_milestones_{assignment_key}"].append(new_milestone)
                    st.success(f"Added: {custom_title}")
                    st.rerun()

        # Show existing custom milestones
        if custom_milestones:
            st.markdown("**Your Custom Milestones:**")
            for i, milestone in enumerate(custom_milestones):
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{milestone['title']}**")
                    st.markdown(f"*{milestone['description']}*")
                    st.markdown(f"📅 {milestone['target_date'].strftime('%d %b %Y')}")

                with col2:
                    if st.button("🗑️", key=f"remove_custom_{assignment_key}_{i}", help="Remove this milestone"):
                        st.session_state[f"custom_milestones_{assignment_key}"].pop(i)
                        st.rerun()

    # Final save section
    st.markdown("---")
    st.markdown("### 💾 Save Your Study Plan")

    # Count total milestones
    selected_count = len(st.session_state.get(f"selected_milestones_{assignment_key}", []))
    custom_count = len(st.session_state.get(f"custom_milestones_{assignment_key}", []))
    total_count = selected_count + custom_count

    st.markdown(
        f"**Ready to save:** {selected_count} AI suggestions + {custom_count} custom milestones = **{total_count} total milestones**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("💾 Save My Study Plan", use_container_width=True, type="primary"):
            if total_count > 0:
                save_selected_milestones(student, assignment, milestone_gen, assignment_key)
            else:
                st.warning("Please select at least one milestone to save!")

    with col2:
        if st.button("🔄 Get New AI Suggestions", use_container_width=True):
            # Clear AI suggestions to regenerate
            if f"ai_suggestions_{assignment_key}" in st.session_state:
                del st.session_state[f"ai_suggestions_{assignment_key}"]
            st.rerun()


def save_selected_milestones(student, assignment, milestone_gen, assignment_key):
    """Save the selected and custom milestones to the tracker with improved error handling"""

    try:
        selected_milestones = st.session_state.get(f"selected_milestones_{assignment_key}", [])
        custom_milestones = st.session_state.get(f"custom_milestones_{assignment_key}", [])

        all_milestones = selected_milestones + custom_milestones

        if not all_milestones:
            st.error("No milestones to save!")
            return

        # Clear any existing milestones first
        clear_success = milestone_gen.clear_milestones_for_assignment(student['id'], assignment_key)
        if not clear_success:
            st.error("Failed to clear existing milestones")
            return

        # Save the selected milestones
        save_success = milestone_gen._save_milestones(student, assignment, all_milestones)

        if save_success:
            # Clear session state only if save was successful
            for key in list(st.session_state.keys()):
                if assignment_key in key:
                    del st.session_state[key]

            st.success(f"🎉 Successfully saved {len(all_milestones)} milestones to your study tracker!")
            st.balloons()

            # Small delay then refresh to show the saved milestones
            time.sleep(1)
            st.rerun()
        else:
            st.error("Failed to save milestones. Please check the error messages above and try again.")

    except Exception as e:
        error_msg = f"Error in save_selected_milestones: {str(e)}"
        st.error(error_msg)
        print(error_msg)


def show_existing_milestones_with_add_option(assignment, existing_milestones, milestone_gen, student):
    """Show existing milestones with option to add more"""

    assignment_key = assignment.get('assignment_id', str(hash(assignment['assignment_name'])))

    st.markdown(f"**✅ Active Study Plan** ({len(existing_milestones)} milestones):")

    # Show progress bar
    completed_count = len([m for m in existing_milestones if m.get('completed', False)])
    progress = completed_count / len(existing_milestones) if existing_milestones else 0
    st.progress(progress, text=f"Progress: {completed_count}/{len(existing_milestones)} completed ({progress:.0%})")

    # Show existing milestones
    for i, milestone in enumerate(existing_milestones):
        show_milestone_card(milestone, i, milestone_gen)

    # Option to add more milestones
    st.markdown("---")
    # Option to add more milestones
    st.markdown("---")

    # Use a button toggle instead of nested expander
    show_add_form_key = f"show_add_form_{assignment_key}"

    if st.button("➕ Add More Milestones", use_container_width=True):
        st.session_state[show_add_form_key] = not st.session_state.get(show_add_form_key, False)

    if st.session_state.get(show_add_form_key, False):
        st.markdown("**Add another milestone to this study plan:**")

        with st.form(f"add_more_{assignment_key}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                new_title = st.text_input("Milestone Title:", placeholder="e.g., Practice presentation")
                new_desc = st.text_area("Description:", placeholder="e.g., Rehearse presentation timing and slides",
                                        height=70)

            with col2:
                new_date = st.date_input("Target Date:", value=datetime.now().date())

            col1_form, col2_form = st.columns(2)
            with col1_form:
                submitted = st.form_submit_button("➕ Add to Study Plan", use_container_width=True)
            with col2_form:
                cancel = st.form_submit_button("Cancel", use_container_width=True)

            if cancel:
                st.session_state[show_add_form_key] = False
                st.rerun()

            if submitted:
                if new_title and new_desc:
                    try:
                        # Add single milestone to existing plan
                        new_milestone = {
                            'title': new_title,
                            'description': new_desc,
                            'target_date': datetime.combine(new_date, datetime.min.time())
                        }

                        milestone_gen._save_single_milestone(student, assignment, new_milestone)
                        st.success(f"Added: {new_title}")
                        st.session_state[show_add_form_key] = False  # Hide form after successful add
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error adding milestone: {str(e)}")
                else:
                    st.error("Please fill in both title and description.")

def show_milestone_card(milestone, index, milestone_gen):
    """Show a single milestone card with completion option"""

    target_date = milestone.get('target_date')
    if isinstance(target_date, str):
        try:
            target_date = datetime.fromisoformat(target_date)
        except:
            target_date = None

    days_until = (target_date - datetime.now()).days if target_date else 0
    completed = milestone.get('completed', False)

    if completed:
        status = "✅"
        status_color = "#10b981"
        status_text = "Completed"
    elif days_until < 0:
        status = "🔴"
        status_color = "#dc2626"
        status_text = f"{abs(days_until)} days overdue"
    elif days_until == 0:
        status = "🟡"
        status_color = "#f59e0b"
        status_text = "Due today"
    elif days_until <= 2:
        status = "🟡"
        status_color = "#f59e0b"
        status_text = f"Due in {days_until} days"
    else:
        status = "🟢"
        status_color = "#10b981"
        status_text = f"Due in {days_until} days"

    # Create milestone card
    col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"""
        <div style="border-left: 4px solid {status_color}; padding: 12px; margin: 8px 0; background: #f9fafb; border-radius: 4px;">
            <div style="font-weight: 600; font-size: 16px;">{status} {milestone['title']}</div>
            <div style="color: #6b7280; margin: 6px 0; line-height: 1.4;">{milestone.get('description', '')}</div>
            <div style="font-size: 13px; color: {status_color}; font-weight: 500;">
                📅 {target_date.strftime('%A, %d %b') if target_date else 'No date'} • {status_text}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if not completed:
            if st.button("✅ Done", key=f"complete_{milestone.get('id', index)}", use_container_width=True):
                success = milestone_gen.mark_milestone_completed(milestone.get('id', index))
                if success:
                    st.success("Completed! 🎉")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()


# Integration function for main app - THIS IS THE MISSING FUNCTION!
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