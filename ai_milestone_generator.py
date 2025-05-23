import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import anthropic
import streamlit as st


class AIStudyMilestoneGenerator:
    """Generate intelligent study milestones for Canvas assignments"""

    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_milestone_tables()

        # Initialize AI client
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            try:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv("ANTHROPIC_API_KEY")
            except:
                api_key = None

        self.ai_client = anthropic.Anthropic(api_key=api_key) if api_key else None

    def init_milestone_tables(self):
        """Initialize milestone tracking tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Study milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                assignment_name TEXT,
                course_name TEXT,
                milestone_title TEXT,
                milestone_description TEXT,
                milestone_type TEXT,
                target_date DATETIME,
                completed BOOLEAN DEFAULT FALSE,
                completed_date DATETIME,
                ai_generated BOOLEAN DEFAULT TRUE,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        # Milestone generation log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestone_generation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                assignment_id TEXT,
                generation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                error_message TEXT,
                milestones_generated INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()

    def generate_milestones_for_assignment(self, student_id: str, assignment: Dict, student_profile: Dict = None) -> \
    List[Dict]:
        """Generate AI-powered study milestones for a specific assignment"""

        if not self.ai_client:
            return self._generate_fallback_milestones(assignment)

        # Get student context
        student_context = self._get_student_context(student_id, student_profile)

        # Get other assignments for workload context
        other_assignments = self._get_concurrent_assignments(student_id, assignment)

        # Create AI prompt for milestone generation
        prompt = self._create_milestone_prompt(assignment, student_context, other_assignments)

        try:
            response = self.ai_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )

            milestones = self._parse_ai_response(response.content[0].text, assignment)

            # Save milestones to database
            self._save_milestones(student_id, assignment, milestones)

            # Log successful generation
            self._log_generation(student_id, assignment['assignment_id'], True, len(milestones))

            return milestones

        except Exception as e:
            print(f"AI milestone generation failed: {e}")

            # Log failed generation
            self._log_generation(student_id, assignment['assignment_id'], False, 0, str(e))

            # Fallback to rule-based milestones
            return self._generate_fallback_milestones(assignment)

    def _get_student_context(self, student_id: str, student_profile: Dict = None) -> Dict:
        """Get student context for AI prompt"""

        # Default context
        context = {
            'learning_style': 'balanced',
            'study_preferences': 'mixed',
            'typical_work_pace': 'steady',
            'strengths': [],
            'goals': []
        }

        # Get from student profile if available
        if student_profile:
            context.update({
                'learning_style': student_profile.get('learning_style', 'balanced'),
                'interests': student_profile.get('interests', []),
                'goals': student_profile.get('goals', []),
                'year_level': student_profile.get('year_level', 11)
            })

        # Get from database
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT name, interests, goals FROM students WHERE id = ?
            ''', (student_id,))

            result = cursor.fetchone()
            if result:
                context['student_name'] = result[0]
                if result[1]:
                    context['interests'] = json.loads(result[1])
                if result[2]:
                    context['goals'] = json.loads(result[2])

            conn.close()

        except Exception as e:
            print(f"Error getting student context: {e}")

        return context

    def _get_concurrent_assignments(self, student_id: str, current_assignment: Dict) -> List[Dict]:
        """Get other assignments due around the same time for workload context"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get assignments due within 2 weeks of current assignment
            current_due = datetime.fromisoformat(current_assignment['due_date']) if current_assignment[
                'due_date'] else datetime.now()
            start_date = current_due - timedelta(days=7)
            end_date = current_due + timedelta(days=7)

            cursor.execute('''
                SELECT assignment_name, course_name, due_date, points_possible
                FROM canvas_assignments
                WHERE student_id = ? 
                AND assignment_id != ?
                AND due_date >= ? 
                AND due_date <= ?
                ORDER BY due_date
            ''', (student_id, current_assignment['assignment_id'],
                  start_date.isoformat(), end_date.isoformat()))

            assignments = []
            for row in cursor.fetchall():
                assignments.append({
                    'name': row[0],
                    'course': row[1],
                    'due_date': row[2],
                    'points': row[3]
                })

            conn.close()
            return assignments

        except Exception as e:
            print(f"Error getting concurrent assignments: {e}")
            return []

    def _create_milestone_prompt(self, assignment: Dict, student_context: Dict, other_assignments: List[Dict]) -> str:
        """Create AI prompt for milestone generation"""

        due_date = datetime.fromisoformat(assignment['due_date']) if assignment['due_date'] else None
        days_available = (due_date - datetime.now()).days if due_date else 14

        # Build context about other assignments
        workload_context = ""
        if other_assignments:
            workload_context = "\n**Other assignments around this time:**\n"
            for other in other_assignments[:3]:
                workload_context += f"- {other['name']} ({other['course']}) - {other['points']} points\n"

        prompt = f"""You are an expert study planner for Australian high school students. Create a detailed study plan for this HSC assessment.

**ASSIGNMENT DETAILS:**
- Name: {assignment['assignment_name']}
- Course: {assignment['course_name']}
- Due Date: {due_date.strftime('%A, %d %B %Y') if due_date else 'No due date'}
- Points: {assignment['points_possible']} points
- Days Available: {days_available} days
- Description: {assignment.get('description', 'No description available')[:300]}

**STUDENT CONTEXT:**
- Student: {student_context.get('student_name', 'Student')}
- Year Level: {student_context.get('year_level', 11)}
- Interests: {', '.join(student_context.get('interests', []))}
- Goals: {', '.join(student_context.get('goals', []))}
{workload_context}

**TASK:**
Create 4-6 specific, actionable study milestones that break this assignment into manageable phases. Consider:

1. **Research & Planning Phase** - Gather sources, understand requirements
2. **Development Phase** - Create content, conduct analysis
3. **Writing/Creation Phase** - Produce the main work
4. **Review & Polish Phase** - Edit, proofread, finalise

**REQUIREMENTS:**
- Each milestone should be 1-3 days long
- Include specific actions (not just "work on assignment")
- Consider the assignment type and subject area
- Account for weekends and the student's other commitments
- Be realistic about what can be achieved each day
- Include submission preparation

**FORMAT YOUR RESPONSE AS JSON:**
```json
[
  {{
    "title": "Research & Source Gathering",
    "description": "Find 5-7 reliable sources on [specific topic]. Create bibliography and take initial notes on key themes.",
    "type": "research", 
    "days_before_due": 12,
    "estimated_hours": 3
  }},
  {{
    "title": "Create Assignment Outline",
    "description": "Develop detailed outline with main arguments, structure essay/report sections, plan evidence integration.",
    "type": "planning",
    "days_before_due": 10,
    "estimated_hours": 2
  }}
]
```

Make the milestones specific to this {assignment['course_name']} assignment and helpful for a Year {student_context.get('year_level', 11)} student."""

        return prompt

    def _parse_ai_response(self, ai_response: str, assignment: Dict) -> List[Dict]:
        """Parse AI response into milestone objects"""

        try:
            # Extract JSON from AI response
            start_idx = ai_response.find('[')
            end_idx = ai_response.rfind(']') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                milestones_data = json.loads(json_str)

                # Convert to milestone objects with actual dates
                milestones = []
                due_date = datetime.fromisoformat(assignment['due_date']) if assignment[
                    'due_date'] else datetime.now() + timedelta(days=14)

                for milestone_data in milestones_data:
                    target_date = due_date - timedelta(days=milestone_data.get('days_before_due', 1))

                    # Don't schedule milestones in the past
                    if target_date <= datetime.now():
                        target_date = datetime.now() + timedelta(days=1)

                    milestone = {
                        'title': milestone_data.get('title', 'Study Milestone'),
                        'description': milestone_data.get('description', 'Work on assignment'),
                        'type': milestone_data.get('type', 'general'),
                        'target_date': target_date,
                        'estimated_hours': milestone_data.get('estimated_hours', 2)
                    }
                    milestones.append(milestone)

                return milestones

            else:
                # Fallback parsing if JSON extraction fails
                return self._extract_milestones_from_text(ai_response, assignment)

        except json.JSONDecodeError:
            return self._extract_milestones_from_text(ai_response, assignment)

    def _extract_milestones_from_text(self, text: str, assignment: Dict) -> List[Dict]:
        """Fallback method to extract milestones from plain text"""

        milestones = []
        lines = text.split('\n')
        current_milestone = {}

        due_date = datetime.fromisoformat(assignment['due_date']) if assignment[
            'due_date'] else datetime.now() + timedelta(days=14)

        # Simple pattern matching for milestone extraction
        for line in lines:
            line = line.strip()

            if any(word in line.lower() for word in ['phase', 'step', 'milestone', 'stage']):
                if current_milestone:
                    milestones.append(current_milestone)

                current_milestone = {
                    'title': line.replace('-', '').replace('*', '').strip(),
                    'description': 'Work on this phase of the assignment',
                    'type': 'general',
                    'target_date': due_date - timedelta(days=len(milestones) * 2 + 2),
                    'estimated_hours': 2
                }

            elif line and current_milestone and 'description' in current_milestone:
                current_milestone['description'] = line[:200]

        if current_milestone:
            milestones.append(current_milestone)

        return milestones if milestones else self._generate_fallback_milestones(assignment)

    def _generate_fallback_milestones(self, assignment: Dict) -> List[Dict]:
        """Generate basic rule-based milestones when AI fails"""

        due_date = datetime.fromisoformat(assignment['due_date']) if assignment[
            'due_date'] else datetime.now() + timedelta(days=14)
        days_available = max((due_date - datetime.now()).days, 1)

        # Basic milestone structure based on assignment type
        if 'exam' in assignment['assignment_name'].lower() or 'test' in assignment['assignment_name'].lower():
            # Exam preparation milestones
            milestones = [
                {
                    'title': 'Review Course Materials',
                    'description': f'Go through all {assignment["course_name"]} notes and textbook chapters covered in this exam.',
                    'type': 'review',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 5)),
                    'estimated_hours': 3
                },
                {
                    'title': 'Create Study Summary',
                    'description': 'Make condensed notes and key concept summaries for quick review.',
                    'type': 'summary',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 3)),
                    'estimated_hours': 2
                },
                {
                    'title': 'Practice Questions',
                    'description': 'Complete practice exercises and past exam questions.',
                    'type': 'practice',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 2)),
                    'estimated_hours': 2
                },
                {
                    'title': 'Final Review',
                    'description': 'Quick review of key concepts and areas of difficulty.',
                    'type': 'review',
                    'target_date': due_date - timedelta(days=1),
                    'estimated_hours': 1
                }
            ]
        else:
            # Assignment milestones
            milestones = [
                {
                    'title': 'Research and Planning',
                    'description': f'Research topic, gather sources, and create an outline for your {assignment["assignment_name"]}.',
                    'type': 'research',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 7)),
                    'estimated_hours': 3
                },
                {
                    'title': 'First Draft',
                    'description': 'Write the first draft, focusing on getting ideas down rather than perfection.',
                    'type': 'draft',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 4)),
                    'estimated_hours': 4
                },
                {
                    'title': 'Review and Revise',
                    'description': 'Review content, improve arguments, check structure and flow.',
                    'type': 'revision',
                    'target_date': due_date - timedelta(days=min(days_available - 1, 2)),
                    'estimated_hours': 2
                },
                {
                    'title': 'Final Polish',
                    'description': 'Proofread, format correctly, check references, and prepare for submission.',
                    'type': 'finalise',
                    'target_date': due_date - timedelta(days=1),
                    'estimated_hours': 1
                }
            ]

        # Adjust dates to not be in the past
        for milestone in milestones:
            if milestone['target_date'] <= datetime.now():
                milestone['target_date'] = datetime.now() + timedelta(hours=12)

        return milestones

    def _save_milestones(self, student_id: str, assignment: Dict, milestones: List[Dict]):
        """Save generated milestones to database"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear existing milestones for this assignment
            cursor.execute('''
                DELETE FROM study_milestones 
                WHERE student_id = ? AND assignment_id = ?
            ''', (student_id, assignment['assignment_id']))

            # Save new milestones
            for milestone in milestones:
                cursor.execute('''
                    INSERT INTO study_milestones
                    (student_id, assignment_id, assignment_name, course_name,
                     milestone_title, milestone_description, milestone_type, target_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student_id,
                    assignment['assignment_id'],
                    assignment['assignment_name'],
                    assignment['course_name'],
                    milestone['title'],
                    milestone['description'],
                    milestone['type'],
                    milestone['target_date'].isoformat()
                ))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error saving milestones: {e}")

    def _log_generation(self, student_id: str, assignment_id: str, success: bool,
                        milestones_generated: int, error_message: str = None):
        """Log milestone generation attempt"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO milestone_generation_log
                (student_id, assignment_id, success, milestones_generated, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, assignment_id, success, milestones_generated, error_message))

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Error logging milestone generation: {e}")

    def get_student_milestones(self, student_id: str, days_ahead: int = 14) -> List[Dict]:
        """Get upcoming milestones for a student"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            end_date = datetime.now() + timedelta(days=days_ahead)

            cursor.execute('''
                SELECT id, assignment_name, course_name, milestone_title, 
                       milestone_description, milestone_type, target_date, completed
                FROM study_milestones
                WHERE student_id = ? 
                AND target_date >= ?
                AND target_date <= ?
                ORDER BY target_date ASC
            ''', (student_id, datetime.now().isoformat(), end_date.isoformat()))

            milestones = []
            for row in cursor.fetchall():
                milestones.append({
                    'id': row[0],
                    'assignment_name': row[1],
                    'course_name': row[2],
                    'title': row[3],
                    'description': row[4],
                    'type': row[5],
                    'target_date': datetime.fromisoformat(row[6]),
                    'completed': bool(row[7])
                })

            conn.close()
            return milestones

        except Exception as e:
            print(f"Error getting milestones: {e}")
            return []

    def mark_milestone_complete(self, milestone_id: int) -> bool:
        """Mark a milestone as completed"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE study_milestones 
                SET completed = TRUE, completed_date = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), milestone_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error marking milestone complete: {e}")
            return False

    def get_assignment_milestones(self, student_id: str, assignment_id: str) -> List[Dict]:
        """Get all milestones for a specific assignment"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, milestone_title, milestone_description, milestone_type, 
                       target_date, completed, completed_date
                FROM study_milestones
                WHERE student_id = ? AND assignment_id = ?
                ORDER BY target_date ASC
            ''', (student_id, assignment_id))

            milestones = []
            for row in cursor.fetchall():
                milestones.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'type': row[3],
                    'target_date': datetime.fromisoformat(row[4]),
                    'completed': bool(row[5]),
                    'completed_date': datetime.fromisoformat(row[6]) if row[6] else None
                })

            conn.close()
            return milestones

        except Exception as e:
            print(f"Error getting assignment milestones: {e}")
            return []