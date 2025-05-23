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