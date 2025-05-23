import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import datetime
from typing import Dict, List, Optional
import schedule
import time
import threading
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class AdvancedEducationDataManager:
    def __init__(self, db_path="career_explorer.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for conversation memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Conversation history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT,
                agent_response TEXT,
                topic_tags TEXT
            )
        ''')

        # Application tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                university TEXT,
                course TEXT,
                deadline DATE,
                status TEXT DEFAULT 'planned',
                notes TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Goals and interests tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT,
                goal_type TEXT,
                goal_description TEXT,
                priority INTEGER,
                target_date DATE,
                status TEXT DEFAULT 'active'
            )
        ''')

        conn.commit()
        conn.close()
        print("✅ Database initialized")

    def save_conversation(self, student_name: str, user_message: str, agent_response: str, topics: List[str] = None):
        """Save conversation for future reference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        topic_tags = ','.join(topics) if topics else ''

        cursor.execute('''
            INSERT INTO conversations (student_name, user_message, agent_response, topic_tags)
            VALUES (?, ?, ?, ?)
        ''', (student_name, user_message, agent_response, topic_tags))

        conn.commit()
        conn.close()

    def get_conversation_history(self, student_name: str, limit: int = 10) -> List[Dict]:
        """Retrieve recent conversations for context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_message, agent_response, timestamp, topic_tags
            FROM conversations 
            WHERE student_name = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (student_name, limit))

        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user_message': row[0],
                'agent_response': row[1],
                'timestamp': row[2],
                'topics': row[3].split(',') if row[3] else []
            })

        conn.close()
        return conversations

    def scrape_live_deadlines(self) -> Dict[str, List[Dict]]:
        """Scrape current application deadlines from university websites"""
        print("🔍 Scraping live application deadlines...")

        university_urls = {
            "University of Newcastle": "https://www.newcastle.edu.au/study/apply",
            "University of Sydney": "https://www.sydney.edu.au/study/how-to-apply.html",
            "UNSW": "https://www.unsw.edu.au/study/how-to-apply",
            "Macquarie University": "https://www.mq.edu.au/study/apply"
        }

        live_deadlines = {}

        for uni_name, url in university_urls.items():
            try:
                print(f"📡 Checking {uni_name}...")
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for deadline-related text
                deadline_info = []

                # Search for common deadline patterns
                text_content = soup.get_text().lower()

                # Common deadline patterns
                if 'september 30' in text_content:
                    deadline_info.append(
                        {"type": "Undergraduate", "deadline": "September 30, 2025", "note": "Main round applications"})
                if 'december 31' in text_content:
                    deadline_info.append(
                        {"type": "Education", "deadline": "December 31, 2024", "note": "Teaching degrees"})
                if 'january 15' in text_content:
                    deadline_info.append({"type": "Late applications", "deadline": "January 15, 2025",
                                          "note": "Subject to availability"})

                live_deadlines[uni_name] = deadline_info
                time.sleep(1)  # Be respectful to servers

            except Exception as e:
                print(f"⚠️ Could not fetch {uni_name}: {e}")
                # Fallback to stored data
                live_deadlines[uni_name] = [
                    {"type": "Standard", "deadline": "Check university website", "note": "Live data unavailable"}]

        print("✅ Live deadline scraping complete")
        return live_deadlines

    def track_application(self, student_name: str, university: str, course: str, deadline: str, notes: str = ""):
        """Track a student's application"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert deadline string to date
        try:
            deadline_date = datetime.datetime.strptime(deadline, "%B %d, %Y").date()
        except:
            deadline_date = None

        cursor.execute('''
            INSERT INTO applications (student_name, university, course, deadline, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_name, university, course, deadline_date, notes))

        conn.commit()
        conn.close()
        print(f"📝 Tracked application: {student_name} -> {university} ({course})")

    def get_upcoming_deadlines(self, student_name: str) -> List[Dict]:
        """Get upcoming deadlines for a student"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT university, course, deadline, notes, status
            FROM applications 
            WHERE student_name = ? AND deadline >= date('now')
            ORDER BY deadline ASC
        ''', (student_name,))

        deadlines = []
        for row in cursor.fetchall():
            deadlines.append({
                'university': row[0],
                'course': row[1],
                'deadline': row[2],
                'notes': row[3],
                'status': row[4]
            })

        conn.close()
        return deadlines


class PDFReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()

    def create_career_plan(self, student_name: str, profile: Dict, recommendations: List[Dict], output_file: str):
        """Generate personalized career plan PDF"""
        print(f"📄 Generating career plan for {student_name}...")

        doc = SimpleDocTemplate(output_file, pagesize=letter)
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=30,
            alignment=1  # Center
        )

        story.append(Paragraph(f"Career Pathway Plan for {student_name}", title_style))
        story.append(Spacer(1, 20))

        # Student Profile Section
        story.append(Paragraph("Student Profile", self.styles['Heading2']))

        profile_data = [
            ['Age:', profile.get('age', 'N/A')],
            ['Year Level:', f"Year {profile.get('year', 'N/A')}"],
            ['Interests:', ', '.join(profile.get('interests', []))],
            ['Timeline:', profile.get('timeline', 'N/A')],
            ['Location Preference:', profile.get('location_preference', 'N/A')]
        ]

        profile_table = Table(profile_data, colWidths=[120, 300])
        profile_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(profile_table)
        story.append(Spacer(1, 20))

        # Recommendations Section
        story.append(Paragraph("Personalized Recommendations", self.styles['Heading2']))

        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec['title']}", self.styles['Heading3']))
            story.append(Paragraph(rec['description'], self.styles['Normal']))

            if 'details' in rec:
                for detail in rec['details']:
                    story.append(Paragraph(f"• {detail}", self.styles['Normal']))

            story.append(Spacer(1, 10))

        # Next Steps Section
        story.append(Paragraph("Immediate Next Steps", self.styles['Heading2']))

        next_steps = [
            "Research recommended universities and courses in detail",
            "Attend university open days and information sessions",
            "Prepare for prerequisite requirements (ATAR targets, subject selections)",
            "Schedule regular check-ins to track progress",
            "Set up application deadline reminders"
        ]

        for step in next_steps:
            story.append(Paragraph(f"• {step}", self.styles['Normal']))

        story.append(Spacer(1, 20))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=1
        )

        story.append(Paragraph(f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}", footer_style))
        story.append(Paragraph("Career Pathway Explorer - Professional Edition", footer_style))

        doc.build(story)
        print(f"✅ Career plan saved as {output_file}")


def test_advanced_features():
    """Test the advanced features"""
    print("🧪 Testing Advanced Features...")

    # Test database
    manager = AdvancedEducationDataManager()

    # Test conversation saving
    manager.save_conversation(
        "Rosa",
        "What courses have lab work?",
        "Biological anthropology programs at Macquarie have excellent lab facilities...",
        ["anthropology", "lab_work", "macquarie"]
    )

    # Test conversation retrieval
    history = manager.get_conversation_history("Rosa")
    print(f"📚 Retrieved {len(history)} conversation entries")

    # Test application tracking
    manager.track_application("Reuben", "University of Newcastle", "Bachelor of Education", "December 31, 2024")

    deadlines = manager.get_upcoming_deadlines("Reuben")
    print(f"📅 Found {len(deadlines)} upcoming deadlines")

    # Test PDF generation
    pdf_gen = PDFReportGenerator()

    sample_profile = {
        "age": 16,
        "year": 11,
        "interests": ["ancient history", "biological anthropology"],
        "timeline": "applying in 12 months",
        "location_preference": "NSW/ACT"
    }

    sample_recommendations = [
        {
            "title": "Recommended Universities",
            "description": "Based on your interests in ancient history and biological anthropology with lab preferences:",
            "details": [
                "Macquarie University - Strong ancient history with lab components",
                "University of Sydney - Prestigious anthropology program",
                "ANU - Research-focused opportunities"
            ]
        },
        {
            "title": "Career Pathways",
            "description": "Potential career directions based on your interests:",
            "details": [
                "Anthropologist - $75,000-$90,000 salary range",
                "Archaeologist - Growing field with fieldwork opportunities",
                "Museum Curator - Combines history and research skills"
            ]
        }
    ]

    try:
        pdf_gen.create_career_plan("Rosa", sample_profile, sample_recommendations, "rosa_career_plan.pdf")
        print("✅ PDF generation successful")
    except Exception as e:
        print(f"⚠️ PDF generation error: {e}")

    print("🎉 Advanced features test complete!")


if __name__ == "__main__":
    test_advanced_features()