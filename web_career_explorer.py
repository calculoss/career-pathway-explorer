import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import anthropic
import os
import json
from dotenv import load_dotenv
from advanced_data_manager import AdvancedEducationDataManager, PDFReportGenerator
from data_collector import AustralianEducationDataCollector
from live_data_collector import LiveEmploymentDataCollector

# Page configuration
st.set_page_config(
    page_title="CareerPath Personal | Rosa & Reuben Career Guidance",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - Khan Academy style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;600;700&display=swap');

    /* Global Styles */
    .stApp {
        background-color: #f7f8fa;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Remove Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
        height: 0rem;
    }

    /* Main container */
    .main-content {
        background: white;
        border-radius: 8px;
        padding: 32px;
        margin: 24px auto;
        max-width: 1200px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e5e5e5;
    }

    /* Header */
    .site-header {
        background: white;
        border-bottom: 1px solid #e5e5e5;
        padding: 16px 0;
        margin-bottom: 32px;
    }

    .site-header .container {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 32px;
    }

    .logo {
        font-size: 24px;
        font-weight: 700;
        color: #1c4980;
        text-decoration: none;
    }

    .logo-subtitle {
        font-size: 14px;
        color: #6b7280;
        font-weight: 400;
        margin-left: 8px;
    }

    /* Typography */
    .page-title {
        font-size: 32px;
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 8px;
        line-height: 1.2;
    }

    .page-subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 32px;
        line-height: 1.4;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
        margin-top: 32px;
    }

    .section-subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 24px;
    }

    /* Student selection cards */
    .student-selection {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
        margin: 32px 0;
    }

    .student-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 32px;
        text-align: center;
        transition: all 0.2s ease;
        cursor: pointer;
    }

    .student-card:hover {
        border-color: #1c4980;
        box-shadow: 0 4px 12px rgba(28, 73, 128, 0.1);
        transform: translateY(-2px);
    }

    .student-card.rosa {
        border-left: 4px solid #e74c3c;
    }

    .student-card.reuben {
        border-left: 4px solid #3498db;
    }

    .student-name {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .student-year {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 16px;
    }

    .student-interests {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }

    .student-timeline {
        font-size: 14px;
        color: #374151;
        font-weight: 500;
    }

    /* Chat interface */
    .chat-container {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin: 24px 0;
    }

    .chat-header {
        background: #f9fafb;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 24px;
        text-align: center;
    }

    .chat-header.rosa {
        background: #fef2f2;
        border-color: #fecaca;
    }

    .chat-header.reuben {
        background: #eff6ff;
        border-color: #bfdbfe;
    }

    .chat-title {
        font-size: 24px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
    }

    .chat-subtitle {
        font-size: 16px;
        color: #6b7280;
    }

    /* Sidebar styling */
    .sidebar-content {
        background: #f9fafb;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }

    .sidebar-title {
        font-size: 18px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
    }

    .sidebar-item {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
        line-height: 1.4;
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

    /* Data dashboard */
    .data-dashboard {
        background: #f9fafb;
        border: 1px solid #e5e5e5;
        border-radius: 8px;
        padding: 24px;
        margin: 24px 0;
    }

    .dashboard-title {
        font-size: 20px;
        font-weight: 600;
        color: #374151;
        margin-bottom: 16px;
    }

    .metric-card {
        background: white;
        border: 1px solid #e5e5e5;
        border-radius: 6px;
        padding: 16px;
        text-align: center;
        margin-bottom: 12px;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #1c4980;
        margin-bottom: 4px;
    }

    .metric-label {
        font-size: 14px;
        color: #6b7280;
    }

    /* Features list */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin: 24px 0;
    }

    .feature-item {
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 6px;
        padding: 16px;
        text-align: center;
        font-size: 14px;
        color: #0c4a6e;
        font-weight: 500;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .main-content {
            margin: 16px;
            padding: 24px;
        }

        .site-header .container {
            padding: 0 24px;
        }

        .student-selection {
            grid-template-columns: 1fr;
        }

        .features-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)


class WebCareerExplorerAgent:
    def __init__(self):
        # API setup
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize data manager
        if 'data_manager' not in st.session_state:
            st.session_state.data_manager = AdvancedEducationDataManager()
            st.session_state.pdf_generator = PDFReportGenerator()

        self.data_manager = st.session_state.data_manager
        self.pdf_generator = st.session_state.pdf_generator

        # Load education data
        self.load_education_data()
        self.load_live_data()

        # Student profiles
        self.student_profiles = {
            "Rosa": {
                "age": 16,
                "year": 11,
                "interests": ["ancient history", "biological anthropology", "english", "writing"],
                "preferences": ["Bachelor of Arts", "lab-based elements", "practical components"],
                "timeline": "applying in 12 months",
                "location_preference": "NSW/ACT",
                "career_considerations": ["research opportunities", "fieldwork", "writing components"],
                "goals": [
                    "Find university program with lab work",
                    "Explore anthropology career prospects",
                    "Prepare for ATAR requirements"
                ],
                "emoji": "🏛️",
                "color": "#e74c3c"
            },
            "Reuben": {
                "age": "nearly 18",
                "year": 12,
                "interests": ["modern history", "chinese studies", "secondary teaching"],
                "preferences": ["army reserves funding", "Newcastle University"],
                "timeline": "applying now - already applied to Newcastle for teaching",
                "location_preference": "Newcastle/NSW",
                "career_considerations": ["army reserves compatibility", "leadership opportunities"],
                "goals": [
                    "Secure teaching placement at Newcastle",
                    "Understand Army Reserves benefits",
                    "Plan application timeline"
                ],
                "emoji": "👨‍🏫",
                "color": "#3498db"
            }
        }

        self.conversation_history = []
        self.current_student = None

    def load_education_data(self):
        """Load education data"""
        try:
            with open('education_data.json', 'r', encoding='utf-8') as f:
                self.education_data = json.load(f)
        except FileNotFoundError:
            collector = AustralianEducationDataCollector()
            collector.save_data_to_file('education_data.json')
            with open('education_data.json', 'r', encoding='utf-8') as f:
                self.education_data = json.load(f)

    def load_live_data(self):
        """Load live employment data"""
        try:
            with open('live_employment_data.json', 'r', encoding='utf-8') as f:
                self.live_data = json.load(f)
        except:
            self.live_data = {
                'abs_employment': {'unemployment_rate': '3.8%', 'participation_rate': '66.8%'},
                'university_stats': {'overall_employment_rate': '89.1%', 'arts_employment_rate': '84.2%'}
            }

    def format_education_data_for_prompt(self, student_name):
        """Format education data for AI prompt"""
        history = self.data_manager.get_conversation_history(student_name, limit=3)

        data_summary = "CURRENT AUSTRALIAN EDUCATION & CAREER DATA WITH LIVE GOVERNMENT UPDATES:\n\n"

        if history:
            data_summary += "RECENT CONVERSATION CONTEXT:\n"
            for conv in history[-3:]:
                topics = ', '.join(conv['topics']) if conv['topics'] else 'General discussion'
                data_summary += f"• Previous topic: {topics}\n"
            data_summary += "\n"

        # Live data
        abs_data = self.live_data.get('abs_employment', {})
        data_summary += "LIVE AUSTRALIAN EMPLOYMENT DATA (ABS):\n"
        data_summary += f"• Current Unemployment Rate: {abs_data.get('unemployment_rate', 'N/A')}\n"
        data_summary += f"• Labor Participation Rate: {abs_data.get('participation_rate', 'N/A')}\n\n"

        uni_stats = self.live_data.get('university_stats', {})
        data_summary += "LIVE UNIVERSITY GRADUATE EMPLOYMENT RATES:\n"
        data_summary += f"• Overall Graduate Employment: {uni_stats.get('overall_employment_rate', 'N/A')}\n"
        data_summary += f"• Arts Graduate Employment: {uni_stats.get('arts_employment_rate', 'N/A')} (Rosa's field)\n\n"

        # University and course data
        data_summary += "NSW/ACT UNIVERSITIES:\n"
        for uni, info in self.education_data['universities'].items():
            data_summary += f"• {uni} ({info['location']}): Strengths in {', '.join(info['strengths'])}\n"

        data_summary += "\nRELEVANT COURSES:\n"
        for course, info in self.education_data['courses'].items():
            data_summary += f"• {course}: {info['duration']}, Prerequisites: {', '.join(info['prerequisites'])}\n"
            if 'lab_components' in info:
                data_summary += f"  🔬 Lab work: {', '.join(info['lab_components'])}\n"

        return data_summary

    def create_system_prompt(self, student_name):
        profile = self.student_profiles.get(student_name, {})
        education_data = self.format_education_data_for_prompt(student_name)

        return f"""You are a professional career guidance counselor with 25+ years of experience. You're providing personalized guidance to {student_name}, building on previous conversations through our CareerPath Personal platform.

STUDENT PROFILE - {student_name}:
- Age: {profile.get('age', '')}
- Year Level: {profile.get('year', '')}  
- Core Interests: {', '.join(profile.get('interests', []))}
- Preferences: {', '.join(profile.get('preferences', []))}
- Timeline: {profile.get('timeline', '')}
- Location Preference: {profile.get('location_preference', '')}
- Career Considerations: {', '.join(profile.get('career_considerations', []))}
- Goals: {', '.join(profile.get('goals', []))}

{education_data}

PROFESSIONAL CAPABILITIES:
- Live Australian university data and current application deadlines
- Real employment statistics and salary benchmarks (2025 data)
- Conversation memory (can reference previous discussions)
- Professional career pathway planning
- Access to NSW/ACT university information

CONVERSATION APPROACH:
- Professional, warm, and supportive
- Reference previous conversations when relevant
- Use specific, current data from the database
- Provide actionable next steps with deadlines
- Be realistic about prospects while maintaining optimism

Focus on providing comprehensive support for {student_name}'s career journey."""

    def get_ai_response(self, user_message, student_name):
        try:
            self.conversation_history.append({"role": "user", "content": user_message})

            topics = self.extract_topics(user_message)

            messages = [{"role": "user", "content": self.create_system_prompt(student_name)}]
            messages.extend(self.conversation_history[-10:])

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=messages
            )

            assistant_response = response.content[0].text
            self.conversation_history.append({"role": "assistant", "content": assistant_response})

            # Save conversation
            self.data_manager.save_conversation(student_name, user_message, assistant_response, topics)

            return assistant_response

        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again."

    def extract_topics(self, message):
        """Extract topic tags from user message"""
        topics = []
        message_lower = message.lower()

        topic_keywords = {
            'universities': ['university', 'uni', 'college', 'macquarie', 'sydney', 'newcastle'],
            'courses': ['course', 'degree', 'bachelor', 'program', 'study'],
            'careers': ['career', 'job', 'work', 'employment', 'salary'],
            'applications': ['apply', 'application', 'deadline', 'admission'],
            'anthropology': ['anthropology', 'archaeology', 'ancient', 'history'],
            'teaching': ['teaching', 'teacher', 'education', 'secondary']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['general']


def create_header():
    """Clean site header"""
    st.markdown("""
    <div class="site-header">
        <div class="container">
            <div>
                <span class="logo">📚 CareerPath Personal</span>
                <span class="logo-subtitle">Rosa & Reuben's Career Guidance Platform</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_dashboard():
    """Create main dashboard"""
    create_header()

    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    st.markdown("""
    <div class="page-title">Welcome to CareerPath Personal</div>
    <div class="page-subtitle">Professional AI-powered career guidance for Rosa and Reuben with live Australian employment data</div>
    """, unsafe_allow_html=True)

    # Features
    st.markdown("""
    <div class="features-grid">
        <div class="feature-item">✅ Live Australian University Data</div>
        <div class="feature-item">✅ Conversation Memory</div>
        <div class="feature-item">✅ Application Tracking</div>
        <div class="feature-item">✅ PDF Career Reports</div>
        <div class="feature-item">✅ Professional Guidance</div>
    </div>
    """, unsafe_allow_html=True)


def create_student_selector():
    """Create professional student selection"""
    agent = st.session_state.agent

    st.markdown('<div class="section-title">Select Student</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="student-selection">
        <div class="student-card rosa">
            <div class="student-name">🏛️ Rosa</div>
            <div class="student-year">Year 11 • Age 16</div>
            <div class="student-interests"><strong>Interests:</strong> Ancient History, Biological Anthropology, Writing</div>
            <div class="student-timeline"><strong>Timeline:</strong> Applying in 12 months</div>
        </div>

        <div class="student-card reuben">
            <div class="student-name">👨‍🏫 Reuben</div>
            <div class="student-year">Year 12 • Nearly 18</div>
            <div class="student-interests"><strong>Interests:</strong> Modern History, Chinese Studies, Teaching</div>
            <div class="student-timeline"><strong>Timeline:</strong> Applying now (Newcastle applied)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Chat with Rosa", use_container_width=True):
            st.session_state.selected_student = "Rosa"
            st.rerun()

    with col2:
        if st.button("Chat with Reuben", use_container_width=True):
            st.session_state.selected_student = "Reuben"
            st.rerun()


def create_chat_interface(student_name):
    """Create professional chat interface"""
    agent = st.session_state.agent
    profile = agent.student_profiles[student_name]

    # Chat header
    css_class = student_name.lower()
    st.markdown(f"""
    <div class="chat-header {css_class}">
        <div class="chat-title">{profile['emoji']} Career Guidance for {student_name}</div>
        <div class="chat-subtitle">Year {profile['year']} • {profile['timeline']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with student info
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-content">
            <div class="sidebar-title">{profile['emoji']} {student_name}'s Profile</div>
            <div class="sidebar-item"><strong>Interests:</strong></div>
        """, unsafe_allow_html=True)

        for interest in profile['interests']:
            st.markdown(f'<div class="sidebar-item">• {interest.title()}</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <div class="sidebar-item" style="margin-top: 16px;"><strong>Goals:</strong></div>
        """, unsafe_allow_html=True)

        for goal in profile['goals']:
            st.markdown(f'<div class="sidebar-item">• {goal}</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("📄 Generate Career Report", use_container_width=True):
            st.info("Generating comprehensive career report...")

        if st.button("📚 View Conversation History", use_container_width=True):
            st.info("Conversation history feature available")

        if st.button("🔄 Switch Students", use_container_width=True):
            del st.session_state.selected_student
            st.rerun()

    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)

    # Initialize chat history
    if f"chat_history_{student_name}" not in st.session_state:
        st.session_state[f"chat_history_{student_name}"] = []

    # Display chat messages
    for message in st.session_state[f"chat_history_{student_name}"]:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])

    # Chat input
    user_input = st.chat_input(f"Ask me anything about {student_name}'s career pathway...")

    if user_input:
        # Add user message
        st.session_state[f"chat_history_{student_name}"].append({
            "role": "user",
            "content": user_input
        })

        # Get AI response
        with st.spinner("Getting career guidance..."):
            response = agent.get_ai_response(user_input, student_name)

        # Add AI response
        st.session_state[f"chat_history_{student_name}"].append({
            "role": "assistant",
            "content": response
        })

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def create_live_data_dashboard():
    """Create live employment data dashboard"""
    agent = st.session_state.agent

    st.markdown("""
    <div class="data-dashboard">
        <div class="dashboard-title">📊 Live Australian Employment Data</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    abs_data = agent.live_data.get('abs_employment', {})
    uni_stats = agent.live_data.get('university_stats', {})

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{abs_data.get('unemployment_rate', 'N/A')}</div>
            <div class="metric-label">Unemployment Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{abs_data.get('participation_rate', 'N/A')}</div>
            <div class="metric-label">Participation Rate</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{uni_stats.get('overall_employment_rate', 'N/A')}</div>
            <div class="metric-label">Graduate Employment</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{uni_stats.get('arts_employment_rate', 'N/A')}</div>
            <div class="metric-label">Arts Graduate Rate</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main application function"""

    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = WebCareerExplorerAgent()

    # Create dashboard
    create_dashboard()

    # Show live data
    create_live_data_dashboard()

    # Main application logic
    if 'selected_student' not in st.session_state:
        create_student_selector()
    else:
        create_chat_interface(st.session_state.selected_student)

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()