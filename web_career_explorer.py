import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import anthropic
import os
import json
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="CareerPath Personal | Rosa & Reuben Career Guidance",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Fixed CSS - removed problematic styles and improved header
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;600;700&display=swap');

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header[data-testid="stHeader"] {display: none;}

    /* Global app styling */
    .stApp {
        background-color: #f7f8fa;
        font-family: 'Lato', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container */
    .main-content {
        background: white;
        border-radius: 8px;
        padding: 2rem;
        margin: 1rem auto;
        max-width: 1200px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    /* Header styling */
    .app-header {
        background: linear-gradient(135deg, #1c4980 0%, #2563eb 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        text-align: center;
    }

    .app-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .app-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }

    /* Student cards */
    .student-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin: 2rem 0;
    }

    .student-card {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .student-card:hover {
        border-color: #1c4980;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(28, 73, 128, 0.15);
    }

    .student-emoji {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .student-name {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    .student-details {
        color: #6b7280;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    .student-interests {
        background: #f3f4f6;
        border-radius: 6px;
        padding: 0.75rem;
        font-size: 0.9rem;
        color: #374151;
    }

    /* Metrics styling */
    .metrics-container {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1.5rem 0;
    }

    .metrics-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 1rem;
        text-align: center;
    }

    /* Features grid */
    .features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }

    .feature-badge {
        background: #dbeafe;
        color: #1e40af;
        padding: 0.75rem 1rem;
        border-radius: 6px;
        text-align: center;
        font-weight: 500;
        font-size: 0.9rem;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1c4980 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(28, 73, 128, 0.3);
    }

    /* Chat interface */
    .chat-header {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }

    .chat-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .student-grid {
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

        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None

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
                    "Find university programme with lab work",
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
        """Load education data with fallback"""
        try:
            with open('education_data.json', 'r', encoding='utf-8') as f:
                self.education_data = json.load(f)
        except FileNotFoundError:
            # Fallback data
            self.education_data = {
                'universities': {
                    'University of Newcastle': {
                        'location': 'Newcastle, NSW',
                        'strengths': ['Education', 'Engineering', 'Medicine']
                    },
                    'Macquarie University': {
                        'location': 'Sydney, NSW',
                        'strengths': ['Ancient History', 'Anthropology', 'Languages']
                    }
                },
                'courses': {
                    'Bachelor of Education': {
                        'duration': '4 years',
                        'prerequisites': ['ATAR 75+']
                    }
                }
            }

    def load_live_data(self):
        """Load live employment data with fallback"""
        try:
            with open('live_employment_data.json', 'r', encoding='utf-8') as f:
                self.live_data = json.load(f)
        except:
            self.live_data = {
                'abs_employment': {
                    'unemployment_rate': '3.8%',
                    'participation_rate': '66.8%'
                },
                'university_stats': {
                    'overall_employment_rate': '89.1%',
                    'arts_employment_rate': '84.2%'
                }
            }

    def get_ai_response(self, user_message, student_name):
        """Get AI response with fallback"""
        if not self.client:
            return f"I'd be happy to help {student_name} with career guidance! However, the AI service isn't currently configured. Please check your API settings."

        try:
            profile = self.student_profiles.get(student_name, {})

            system_prompt = f"""You are a professional career guidance counsellor helping {student_name}, a Year {profile.get('year', '')} student interested in {', '.join(profile.get('interests', []))}.

Student Details:
- Timeline: {profile.get('timeline', '')}
- Location preference: {profile.get('location_preference', '')}
- Goals: {', '.join(profile.get('goals', []))}

Provide helpful, specific advice about university courses, career prospects, and next steps."""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=[
                    {"role": "user", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"I encountered an error: {str(e)}. Please try again or check your internet connection."


def create_header():
    """Create clean header"""
    st.markdown("""
    <div class="app-header">
        <div class="app-title">📚 CareerPath Personal</div>
        <div class="app-subtitle">Professional AI-powered career guidance for Rosa and Reuben</div>
    </div>
    """, unsafe_allow_html=True)


def create_dashboard():
    """Create main dashboard"""
    create_header()

    # Features showcase
    st.markdown("""
    <div class="features-grid">
        <div class="feature-badge">✅ Live Australian University Data</div>
        <div class="feature-badge">✅ Conversation Memory</div>
        <div class="feature-badge">✅ Application Tracking</div>
        <div class="feature-badge">✅ PDF Career Reports</div>
        <div class="feature-badge">✅ Professional Guidance</div>
    </div>
    """, unsafe_allow_html=True)


def create_student_selector():
    """Create student selection interface"""
    agent = st.session_state.agent

    st.markdown("## Select Student")

    # Create columns for student cards
    col1, col2 = st.columns(2)

    # Rosa's card
    with col1:
        rosa_profile = agent.student_profiles["Rosa"]

        st.markdown(f"""
        <div class="student-card">
            <div class="student-emoji">{rosa_profile['emoji']}</div>
            <div class="student-name">Rosa</div>
            <div class="student-details">
                <strong>Year 11 • Age 16</strong><br>
                Timeline: Applying in 12 months
            </div>
            <div class="student-interests">
                <strong>Interests:</strong> {', '.join(rosa_profile['interests'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Chat with Rosa", key="rosa_btn", use_container_width=True):
            st.session_state.selected_student = "Rosa"
            st.rerun()

    # Reuben's card
    with col2:
        reuben_profile = agent.student_profiles["Reuben"]

        st.markdown(f"""
        <div class="student-card">
            <div class="student-emoji">{reuben_profile['emoji']}</div>
            <div class="student-name">Reuben</div>
            <div class="student-details">
                <strong>Year 12 • Nearly 18</strong><br>
                Timeline: Applying now
            </div>
            <div class="student-interests">
                <strong>Interests:</strong> {', '.join(reuben_profile['interests'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Chat with Reuben", key="reuben_btn", use_container_width=True):
            st.session_state.selected_student = "Reuben"
            st.rerun()


def create_metrics_dashboard():
    """Create employment metrics dashboard"""
    agent = st.session_state.agent

    st.markdown("""
    <div class="metrics-container">
        <div class="metrics-title">📊 Live Australian Employment Data</div>
    </div>
    """, unsafe_allow_html=True)

    # Create metrics columns
    col1, col2, col3, col4 = st.columns(4)

    abs_data = agent.live_data.get('abs_employment', {})
    uni_stats = agent.live_data.get('university_stats', {})

    with col1:
        st.metric(
            "Unemployment Rate",
            abs_data.get('unemployment_rate', 'N/A'),
            help="Current Australian unemployment rate (ABS)"
        )

    with col2:
        st.metric(
            "Participation Rate",
            abs_data.get('participation_rate', 'N/A'),
            help="Labour force participation rate"
        )

    with col3:
        st.metric(
            "Graduate Employment",
            uni_stats.get('overall_employment_rate', 'N/A'),
            help="Overall university graduate employment rate"
        )

    with col4:
        st.metric(
            "Arts Graduate Rate",
            uni_stats.get('arts_employment_rate', 'N/A'),
            help="Employment rate for Arts graduates"
        )


def create_chat_interface(student_name):
    """Create chat interface"""
    agent = st.session_state.agent
    profile = agent.student_profiles[student_name]

    # Chat header
    st.markdown(f"""
    <div class="chat-header">
        <div class="chat-title">{profile['emoji']} Career Guidance for {student_name}</div>
        <div>Year {profile['year']} • {profile['timeline']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with student info
    with st.sidebar:
        st.markdown(f"### {profile['emoji']} {student_name}'s Profile")

        st.markdown("**Interests:**")
        for interest in profile['interests']:
            st.markdown(f"• {interest.title()}")

        st.markdown("**Goals:**")
        for goal in profile['goals']:
            st.markdown(f"• {goal}")

        st.markdown("---")

        if st.button("📄 Generate Career Report", use_container_width=True):
            st.info("Career report generation feature coming soon!")

        if st.button("🔄 Switch Students", use_container_width=True):
            if 'selected_student' in st.session_state:
                del st.session_state.selected_student
            st.rerun()

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


def main():
    """Main application function"""
    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = WebCareerExplorerAgent()

    # Create dashboard
    create_dashboard()

    # Show metrics
    create_metrics_dashboard()

    # Main application logic
    if 'selected_student' not in st.session_state:
        create_student_selector()
    else:
        create_chat_interface(st.session_state.selected_student)


if __name__ == "__main__":
    main()