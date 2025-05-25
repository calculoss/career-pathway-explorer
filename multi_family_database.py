import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class MultiFamilyDatabase:
    def __init__(self, db_path="community_career_explorer.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with multi-family support"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Families table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS families (
                id TEXT PRIMARY KEY,
                family_name TEXT NOT NULL,
                email TEXT,
                location TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                settings TEXT DEFAULT '{}'
            )
        ''')

        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                family_id TEXT,
                name TEXT NOT NULL,
                age INTEGER,
                year_level INTEGER,
                interests TEXT,
                preferences TEXT,
                timeline TEXT,
                location_preference TEXT,
                career_considerations TEXT,
                goals TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families (id)
            )
        ''')

        # Conversations table (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                student_id TEXT,
                student_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT,
                agent_response TEXT,
                topic_tags TEXT,
                session_id TEXT,
                FOREIGN KEY (family_id) REFERENCES families (id),
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        # Applications tracking (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id TEXT,
                student_id TEXT,
                student_name TEXT,
                university TEXT,
                course TEXT,
                deadline DATE,
                status TEXT DEFAULT 'planned',
                notes TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (family_id) REFERENCES families (id),
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        # Platform analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS platform_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE DEFAULT CURRENT_DATE,
                total_families INTEGER DEFAULT 0,
                total_students INTEGER DEFAULT 0,
                total_conversations INTEGER DEFAULT 0,
                total_reports_generated INTEGER DEFAULT 0,
                active_families_today INTEGER DEFAULT 0
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Multi-family database initialized")

    def create_family(self, family_name: str, email: str = "", location: str = "") -> str:
        """Create a new family"""
        family_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO families (id, family_name, email, location)
            VALUES (?, ?, ?, ?)
        ''', (family_id, family_name, email, location))

        conn.commit()
        conn.close()

        print(f"✅ Created family: {family_name} (ID: {family_id})")
        return family_id

    def add_student(self, family_id: str, student_data: Dict) -> str:
        """Add a student to a family"""
        student_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO students (
                id, family_id, name, age, year_level, interests, 
                preferences, timeline, location_preference, 
                career_considerations, goals
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            student_id, family_id, student_data['name'], student_data['age'],
            student_data['year_level'], json.dumps(student_data['interests']),
            json.dumps(student_data['preferences']), student_data['timeline'],
            student_data['location_preference'],
            json.dumps(student_data['career_considerations']),
            json.dumps(student_data['goals'])
        ))

        conn.commit()
        conn.close()

        print(f"✅ Added student: {student_data['name']} to family {family_id}")
        return student_id

    def get_all_families(self) -> List[Dict]:
        """Get all families"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT f.*, COUNT(s.id) as student_count
            FROM families f
            LEFT JOIN students s ON f.id = s.family_id
            GROUP BY f.id
            ORDER BY f.last_active DESC
        ''')

        families = []
        for row in cursor.fetchall():
            families.append({
                'id': row[0],
                'family_name': row[1],
                'email': row[2],
                'location': row[3],
                'created_date': row[4],
                'last_active': row[5],
                'student_count': row[7]
            })

        conn.close()
        return families

    def get_family_students(self, family_id: str) -> List[Dict]:
        """Get all students for a family"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM students WHERE family_id = ?
            ORDER BY year_level DESC, name
        ''', (family_id,))

        students = []
        for row in cursor.fetchall():
            students.append({
                'id': row[0],
                'family_id': row[1],
                'name': row[2],
                'age': row[3],
                'year_level': row[4],
                'interests': json.loads(row[5]) if row[5] else [],
                'preferences': json.loads(row[6]) if row[6] else [],
                'timeline': row[7],
                'location_preference': row[8],
                'career_considerations': json.loads(row[9]) if row[9] else [],
                'goals': json.loads(row[10]) if row[10] else []
            })

        conn.close()
        return students

    def save_conversation(self, family_id: str, student_id: str, student_name: str,
                          user_message: str, agent_response: str, topics: List[str] = None):
        """Save conversation with family context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        topic_tags = ','.join(topics) if topics else ''
        session_id = datetime.now().strftime('%Y%m%d_%H')  # Group by hour

        cursor.execute('''
            INSERT INTO conversations (
                family_id, student_id, student_name, user_message, 
                agent_response, topic_tags, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (family_id, student_id, student_name, user_message,
              agent_response, topic_tags, session_id))

        # Update family last_active
        cursor.execute('''
            UPDATE families SET last_active = CURRENT_TIMESTAMP WHERE id = ?
        ''', (family_id,))

        conn.commit()
        conn.close()

    def get_platform_analytics(self) -> Dict:
        """Get platform-wide analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total families
        cursor.execute('SELECT COUNT(*) FROM families')
        total_families = cursor.fetchone()[0]

        # Total students
        cursor.execute('SELECT COUNT(*) FROM students')
        total_students = cursor.fetchone()[0]

        # Total conversations
        cursor.execute('SELECT COUNT(*) FROM conversations')
        total_conversations = cursor.fetchone()[0]

        # Active families this week
        cursor.execute('''
            SELECT COUNT(DISTINCT family_id) FROM conversations 
            WHERE timestamp >= date('now', '-7 days')
        ''')
        active_families_week = cursor.fetchone()[0]

        # Most popular interests
        cursor.execute('''
            SELECT student_name, COUNT(*) as conversation_count
            FROM conversations 
            GROUP BY student_name 
            ORDER BY conversation_count DESC 
            LIMIT 5
        ''')
        top_students = cursor.fetchall()

        # Conversations by topic
        cursor.execute('''
            SELECT topic_tags, COUNT(*) as count
            FROM conversations 
            WHERE topic_tags != ''
            GROUP BY topic_tags 
            ORDER BY count DESC 
            LIMIT 10
        ''')
        top_topics = cursor.fetchall()

        conn.close()

        return {
            'total_families': total_families,
            'total_students': total_students,
            'total_conversations': total_conversations,
            'active_families_week': active_families_week,
            'top_students': top_students,
            'top_topics': top_topics,
            'last_updated': datetime.now().isoformat()
        }

    def create_family(self, family_name: str, email: str = "", location: str = "") -> tuple:
        """Create a new family and return family_id and access_code"""
        import random
        import string

        family_id = str(uuid.uuid4())

        # Generate unique access code (8 characters)
        access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Ensure access_code column exists
        try:
            cursor.execute('ALTER TABLE families ADD COLUMN access_code TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists

        # Check if access code already exists (very unlikely but be safe)
        max_attempts = 10
        attempts = 0

        while attempts < max_attempts:
            cursor.execute('SELECT id FROM families WHERE access_code = ?', (access_code,))
            if cursor.fetchone() is None:
                break  # Access code is unique

            # Generate new code
            access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            attempts += 1

        try:
            cursor.execute('''
                INSERT INTO families (id, family_name, email, location, access_code)
                VALUES (?, ?, ?, ?, ?)
            ''', (family_id, family_name, email, location, access_code))

            conn.commit()
            print(f"✅ Created family: {family_name} (Code: {access_code})")

        except sqlite3.Error as e:
            print(f"❌ Database error creating family: {e}")
            conn.rollback()
            raise e
        finally:
            conn.close()

        return family_id, access_code

    def verify_family_access(self, access_code: str) -> dict:
        """Verify access code and return family info - IMPROVED VERSION"""
        if not access_code or len(access_code.strip()) < 6:
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Clean the access code
            clean_code = access_code.strip().upper()

            cursor.execute('''
                SELECT id, family_name, email, location, access_code, created_date
                FROM families WHERE UPPER(access_code) = ?
            ''', (clean_code,))

            result = cursor.fetchone()

            if result:
                # Update last_active timestamp
                cursor.execute('''
                    UPDATE families SET last_active = CURRENT_TIMESTAMP WHERE id = ?
                ''', (result[0],))
                conn.commit()

                return {
                    'id': result[0],
                    'family_name': result[1],
                    'email': result[2] or '',
                    'location': result[3] or '',
                    'access_code': result[4],
                    'created_date': result[5]
                }
            else:
                print(f"❌ No family found with access code: {clean_code}")
                return None

        except sqlite3.Error as e:
            print(f"❌ Database error during verification: {e}")
            return None
        finally:
            conn.close()

    # Add this method to your MultiFamilyDatabase class in multi_family_database.py

    def init_canvas_tables(self):
        """Initialize Canvas integration tables"""
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
        print("✅ Canvas tables initialized")

    # Also update your init_database method to call this:
    def init_database(self):
        """Initialize database with multi-family support"""
        # ... your existing code ...

        # Add this line at the end of your existing init_database method:
        self.init_canvas_tables()

    def test_database_connection(self):
        """Test database connection and show sample data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Test connection
            cursor.execute('SELECT COUNT(*) FROM families')
            family_count = cursor.fetchone()[0]

            print(f"✅ Database connected successfully")
            print(f"📊 Total families: {family_count}")

            # Show sample families (for debugging)
            cursor.execute('SELECT family_name, access_code FROM families LIMIT 3')
            sample_families = cursor.fetchall()

            if sample_families:
                print("📋 Sample families:")
                for family_name, code in sample_families:
                    print(f"  - {family_name}: {code}")

            conn.close()
            return True

        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False

    def create_test_family(self):
        """Create a test family for debugging"""
        try:
            family_id, access_code = self.create_family(
                "Test Family",
                "test@example.com",
                "Sydney, NSW"
            )

            # Add a test student
            student_data = {
                'name': 'Test Student',
                'age': 16,
                'year_level': 11,
                'interests': ['science', 'technology'],
                'preferences': [],
                'timeline': 'applying in 12 months',
                'location_preference': 'NSW',
                'career_considerations': [],
                'goals': ['university entry']
            }

            self.add_student(family_id, student_data)

            print(f"🧪 Test family created successfully!")
            print(f"Family: Test Family")
            print(f"Access Code: {access_code}")

            return access_code

        except Exception as e:
            print(f"❌ Failed to create test family: {e}")
            return None

    # Usage example for testing:
    if __name__ == "__main__":
        db = MultiFamilyDatabase()

        # Test database connection
        if db.test_database_connection():
            print("Database is working correctly!")

            # Create test family if needed
            test_code = db.create_test_family()
            if test_code:
                print(f"\n🔑 You can test login with code: {test_code}")
        else:
            print("Database connection issues detected!")
# Initialize with sample families for testing
def setup_sample_families():
    """Set up sample families for demonstration"""
    db = MultiFamilyDatabase()

    # Create sample families
    smith_family = db.create_family("Smith Family", "smith@email.com", "Newcastle, NSW")
    jones_family = db.create_family("Jones Family", "jones@email.com", "Sydney, NSW")
    brown_family = db.create_family("Brown Family", "brown@email.com", "Canberra, ACT")

    # Add students to Smith family (Rosa & Reuben)
    db.add_student(smith_family, {
        'name': 'Rosa',
        'age': 16,
        'year_level': 11,
        'interests': ['ancient history', 'biological anthropology', 'writing'],
        'preferences': ['lab-based learning', 'research opportunities'],
        'timeline': 'applying in 12 months',
        'location_preference': 'NSW/ACT',
        'career_considerations': ['research opportunities', 'fieldwork'],
        'goals': ['Find university with lab work', 'Explore anthropology careers']
    })

    db.add_student(smith_family, {
        'name': 'Reuben',
        'age': 18,
        'year_level': 12,
        'interests': ['modern history', 'chinese studies', 'teaching'],
        'preferences': ['army reserves funding', 'Newcastle University'],
        'timeline': 'applying now',
        'location_preference': 'Newcastle/NSW',
        'career_considerations': ['army reserves compatibility', 'leadership'],
        'goals': ['Secure teaching placement', 'Understand Army Reserves benefits']
    })

    # Add students to other families
    db.add_student(jones_family, {
        'name': 'Emma',
        'age': 17,
        'year_level': 12,
        'interests': ['psychology', 'social work', 'counseling'],
        'preferences': ['helping others', 'graduate programs'],
        'timeline': 'applying now',
        'location_preference': 'Sydney/NSW',
        'career_considerations': ['mental health focus', 'community impact'],
        'goals': ['University psychology program', 'Career in mental health']
    })

    db.add_student(brown_family, {
        'name': 'Alex',
        'age': 16,
        'year_level': 11,
        'interests': ['computer science', 'engineering', 'technology'],
        'preferences': ['hands-on projects', 'innovation'],
        'timeline': 'applying in 12 months',
        'location_preference': 'ACT/NSW',
        'career_considerations': ['tech industry', 'startup opportunities'],
        'goals': ['Top CS program', 'Internship opportunities']
    })

    print("✅ Sample families and students created")
    return db




if __name__ == "__main__":
    # Test the multi-family database
    db = setup_sample_families()

    # Show analytics
    analytics = db.get_platform_analytics()
    print(f"\n📊 Platform Analytics:")
    print(f"Total Families: {analytics['total_families']}")
    print(f"Total Students: {analytics['total_students']}")

    # Show all families
    families = db.get_all_families()
    print(f"\n👨‍👩‍👧‍👦 Families on Platform:")
    for family in families:
        print(f"• {family['family_name']} - {family['student_count']} students")