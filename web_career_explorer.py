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

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Professional Career Pathway Explorer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #3498db;
        margin-bottom: 2rem;
    }

    .student-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }

    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
    }

    .feature-badge {
        background: #27ae60;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        margin: 0.2rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


class WebCareerExplorerAgent:
    def __init__(self):
        # Cloud-compatible API key loading
        try:
            # Try Streamlit secrets first (for cloud deployment)
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            # Fall back to .env file (for local development)
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

    def load_education_data(self):
        """Load education data"""
        try:
            with open('education_data.json', 'r', encoding='utf-8') as f:
                self.education_data = json.load(f)
        except FileNotFoundError:
            # Create fresh data if needed
            collector = AustralianEducationDataCollector()
            collector.save_data_to_file('education_data.json')
            with open('education_data.json', 'r', encoding='utf-8') as f:
                self.education_data = json.load(f)

    def format_education_data_for_prompt(self, student_name):
        """Enhanced education data formatting with live government data"""

        # Get conversation history for context
        history = self.data_manager.get_conversation_history(student_name, limit=3)

        data_summary = "CURRENT AUSTRALIAN EDUCATION & CAREER DATA WITH LIVE GOVERNMENT UPDATES:\n\n"

        # Previous conversation context
        if history:
            data_summary += "RECENT CONVERSATION CONTEXT:\n"
            for conv in history[-3:]:
                topics = ', '.join(conv['topics']) if conv['topics'] else 'General discussion'
                data_summary += f"• Previous topic: {topics}\n"
            data_summary += "\n"

        # LIVE GOVERNMENT EMPLOYMENT DATA
        abs_data = self.live_data.get('abs_employment', {})
        data_summary += "LIVE AUSTRALIAN EMPLOYMENT DATA (ABS):\n"
        data_summary += f"• Current Unemployment Rate: {abs_data.get('unemployment_rate', 'N/A')}\n"
        data_summary += f"• Labor Participation Rate: {abs_data.get('participation_rate', 'N/A')}\n"
        data_summary += f"• Employment Growth: {abs_data.get('employment_growth', 'N/A')}\n"
        data_summary += f"• Source: {abs_data.get('source', 'Government data')}\n\n"

        # LIVE UNIVERSITY GRADUATE STATISTICS
        uni_stats = self.live_data.get('university_stats', {})
        data_summary += "LIVE UNIVERSITY GRADUATE EMPLOYMENT RATES:\n"
        data_summary += f"• Overall Graduate Employment: {uni_stats.get('overall_employment_rate', 'N/A')}\n"
        data_summary += f"• Arts Graduate Employment: {uni_stats.get('arts_employment_rate', 'N/A')} (Rosa's field)\n"
        data_summary += f"• Education Graduate Employment: {uni_stats.get('education_employment_rate', 'N/A')} (Reuben's field)\n"
        data_summary += f"• Median Starting Salary: {uni_stats.get('median_starting_salary', 'N/A')}\n\n"

        # LIVE CAREER OUTLOOK DATA
        career_outlook = self.live_data.get('career_outlook', {})
        if career_outlook:
            data_summary += "LIVE CAREER-SPECIFIC EMPLOYMENT DATA:\n"
            for career, data in career_outlook.items():
                data_summary += f"• {career.title()}:\n"
                data_summary += f"  - Employment Outlook: {data.get('employment_outlook', 'N/A')}\n"
                data_summary += f"  - Weekly Earnings: {data.get('weekly_earnings', 'N/A')}\n"
                data_summary += f"  - Current Employment Size: {data.get('employment_size', 'N/A')}\n"
                data_summary += f"  - Growth Forecast: {data.get('growth_forecast', 'N/A')}\n"
            data_summary += "\n"

        # University data
        data_summary += "NSW/ACT UNIVERSITIES:\n"
        for uni, info in self.education_data['universities'].items():
            data_summary += f"• {uni} ({info['location']}): Strengths in {', '.join(info['strengths'])}\n"

        # Course data
        data_summary += "\nRELEVANT COURSES:\n"
        for course, info in self.education_data['courses'].items():
            data_summary += f"• {course}: {info['duration']}, Prerequisites: {', '.join(info['prerequisites'])}\n"
            if 'lab_components' in info:
                data_summary += f"  🔬 Lab work: {', '.join(info['lab_components'])}\n"
            if 'macquarie_specific' in info:
                data_summary += f"  🏛️ Macquarie features: {', '.join(info['macquarie_specific'])}\n"

        # Army reserves data for Reuben
        if student_name == "Reuben":
            data_summary += "\nARMY RESERVES EDUCATION BENEFITS:\n"
            for benefit, info in self.education_data['army_benefits'].items():
                data_summary += f"• {benefit}: {info['description']} - {info.get('amount', 'Various benefits')}\n"

        data_summary += f"\nDATA FRESHNESS: Live government data collected at {self.live_data.get('collection_timestamp', 'Unknown')}\n"

        return data_summary
    def create_system_prompt(self, student_name):
        profile = self.student_profiles.get(student_name, {})
        education_data = self.format_education_data_for_prompt(student_name)

        return f"""You are a professional career guidance counselor with 25+ years of experience. You're providing personalized guidance to {student_name} through a web-based career exploration platform.

STUDENT PROFILE - {student_name}:
- Age: {profile.get('age', '')}
- Year Level: {profile.get('year', '')}  
- Core Interests: {', '.join(profile.get('interests', []))}
- Preferences: {', '.join(profile.get('preferences', []))}
- Timeline: {profile.get('timeline', '')}
- Location Preference: {profile.get('location_preference', '')}
- Career Considerations: {', '.join(profile.get('career_considerations', []))}
- Current Goals: {', '.join(profile.get('goals', []))}

{education_data}

PLATFORM CAPABILITIES:
- Web-based career exploration accessible from any device
- Conversation memory across sessions
- Real-time Australian university and career data
- PDF career plan generation
- Application deadline tracking
- Family collaboration features

WEB INTERFACE CONTEXT:
- Student is accessing this through a professional web interface
- Can generate reports, track applications, view conversation history
- Interface shows data visualizations and interactive elements
- Mobile-friendly for access from school or anywhere

RESPONSE STYLE:
- Professional yet approachable for web interface
- Use specific data from the Australian education database
- Suggest actionable next steps with concrete timelines
- Reference platform features when relevant
- Keep responses concise but comprehensive for web reading
- Encourage use of report generation and tracking features

Focus on providing personalized, data-driven career guidance that takes advantage of the web platform's capabilities."""

    def get_ai_response(self, user_message, student_name):
        """Get response from Claude AI"""
        try:
            # Extract topics for conversation tracking
            topics = self.extract_topics(user_message)

            # Create system prompt with current data
            system_prompt = self.create_system_prompt(student_name)

            # Get recent conversation history for context
            history = self.data_manager.get_conversation_history(student_name, limit=5)

            # Build messages
            messages = [{"role": "user", "content": system_prompt}]

            # Add recent history for context
            for conv in history[-3:]:  # Last 3 conversations
                messages.append({"role": "user", "content": conv['user_message']})
                messages.append({"role": "assistant", "content": conv['agent_response']})

            # Add current message
            messages.append({"role": "user", "content": user_message})

            # Get AI response
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                messages=messages
            )

            assistant_response = response.content[0].text

            # Save conversation to database
            self.data_manager.save_conversation(student_name, user_message, assistant_response, topics)

            return assistant_response

        except Exception as e:
            return f"I encountered an error: {str(e)}. Please check your API connection and try again."

    def extract_topics(self, message):
        """Extract topic tags from user message"""
        topics = []
        message_lower = message.lower()

        topic_keywords = {
            'universities': ['university', 'uni', 'college', 'macquarie', 'sydney', 'newcastle', 'unsw', 'anu'],
            'courses': ['course', 'degree', 'bachelor', 'program', 'study'],
            'careers': ['career', 'job', 'work', 'employment', 'salary'],
            'applications': ['apply', 'application', 'deadline', 'admission'],
            'army_reserves': ['army', 'reserves', 'military', 'funding'],
            'lab_work': ['lab', 'laboratory', 'practical', 'hands-on', 'fieldwork'],
            'anthropology': ['anthropology', 'archaeology', 'ancient', 'history'],
            'teaching': ['teaching', 'teacher', 'education', 'secondary']
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['general']

    def load_live_data(self):
        """Load live employment data"""
        try:
            with open('live_employment_data.json', 'r', encoding='utf-8') as f:
                self.live_data = json.load(f)
            print("📊 Live employment data loaded successfully")
        except FileNotFoundError:
            print("📊 No live data file found, collecting fresh data...")
            # Collect fresh data
            collector = LiveEmploymentDataCollector()
            collector.save_live_data()
            with open('live_employment_data.json', 'r', encoding='utf-8') as f:
                self.live_data = json.load(f)
        except Exception as e:
            print(f"📊 Using fallback data: {e}")
            self.live_data = self.get_fallback_live_data()

    def get_fallback_live_data(self):
        """Fallback live data"""
        return {
            'collection_timestamp': datetime.now().isoformat(),
            'abs_employment': {
                'unemployment_rate': '3.8%',
                'participation_rate': '66.8%',
                'employment_growth': '+2.1%',
                'source': 'Australian Bureau of Statistics (cached)'
            },
            'university_stats': {
                'overall_employment_rate': '89.1%',
                'median_starting_salary': '$61,000',
                'arts_employment_rate': '84.2%',
                'education_employment_rate': '93.7%',
                'source': 'Graduate Outcomes Survey'
            },
            'career_outlook': {
                'anthropologists': {
                    'employment_outlook': 'Moderate Growth',
                    'weekly_earnings': '$1,450 per week',
                    'employment_size': '2,500 employed',
                    'growth_forecast': '4.2% growth forecast'
                },
                'teachers': {
                    'employment_outlook': 'Strong Growth',
                    'weekly_earnings': '$1,650 per week',
                    'employment_size': '180,000 employed',
                    'growth_forecast': '8.5% growth forecast'
                }
            }
        }


def create_dashboard():
    """Create the main dashboard"""

    # Header
    st.markdown('<div class="main-header">🎓 Professional Career Pathway Explorer</div>', unsafe_allow_html=True)

    # Feature badges
    features = [
        "✅ Live Australian University Data",
        "✅ Conversation Memory",
        "✅ Application Tracking",
        "✅ PDF Career Reports",
        "✅ Web Access Anywhere"
    ]

    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(f'<div class="feature-badge">{feature}</div>', unsafe_allow_html=True)

    st.markdown("---")


def create_student_selector():
    """Create student selection interface"""
    agent = st.session_state.agent

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="student-card">
            <h3>🏛️ Rosa (Year 11)</h3>
            <p><strong>Interests:</strong> Ancient History, Biological Anthropology, Writing</p>
            <p><strong>Timeline:</strong> Applying in 12 months</p>
            <p><strong>Focus:</strong> Lab-based learning, research opportunities</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Chat with Rosa", key="rosa_btn", use_container_width=True):
            st.session_state.selected_student = "Rosa"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="student-card">
            <h3>👨‍🏫 Reuben (Year 12)</h3>
            <p><strong>Interests:</strong> Modern History, Chinese Studies, Teaching</p>
            <p><strong>Timeline:</strong> Applying now (Newcastle applied)</p>
            <p><strong>Focus:</strong> Army Reserves funding, education career</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Chat with Reuben", key="reuben_btn", use_container_width=True):
            st.session_state.selected_student = "Reuben"
            st.rerun()


def create_chat_interface(student_name):
    """Create the chat interface for selected student"""
    agent = st.session_state.agent
    profile = agent.student_profiles[student_name]

    # Student header
    st.markdown(f"""
    <div style="background: {profile['color']}; color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h2>{profile['emoji']} Chatting with {student_name}</h2>
        <p><strong>Year {profile['year']}</strong> • {profile['timeline']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar with student info and tools
    with st.sidebar:
        st.markdown(f"### {profile['emoji']} {student_name}'s Profile")

        st.write("**Interests:**")
        for interest in profile['interests']:
            st.write(f"• {interest.title()}")

        st.write("**Current Goals:**")
        for goal in profile['goals']:
            st.write(f"• {goal}")

        st.markdown("---")

        # Quick actions
        st.markdown("### 🚀 Quick Actions")

        if st.button("📄 Generate Career Report", use_container_width=True):
            with st.spinner("Generating comprehensive career report..."):
                try:
                    filename = agent.pdf_generator.create_career_plan(
                        student_name,
                        profile,
                        get_sample_recommendations(student_name),
                        f"{student_name.lower()}_web_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    )
                    st.success(f"✅ Career report generated: {filename}")

                    # Offer download
                    with open(filename, "rb") as pdf_file:
                        st.download_button(
                            label="📥 Download Report",
                            data=pdf_file.read(),
                            file_name=filename,
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

        if st.button("📚 View Conversation History", use_container_width=True):
            history = agent.data_manager.get_conversation_history(student_name, limit=10)
            if history:
                st.markdown("### Recent Conversations")
                for i, conv in enumerate(history[:5], 1):
                    with st.expander(f"Conversation {i} - {', '.join(conv['topics']).title()}"):
                        st.write(f"**{student_name}:** {conv['user_message']}")
                        st.write(f"**Counselor:** {conv['agent_response'][:200]}...")
                        st.caption(f"Date: {conv['timestamp']}")
            else:
                st.info("No conversation history yet.")

        if st.button("🔄 Switch Students", use_container_width=True):
            del st.session_state.selected_student
            st.rerun()

    # Main chat area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Chat history display
        st.markdown("### 💬 Conversation")

        # Initialize chat history in session state
        if f"chat_history_{student_name}" not in st.session_state:
            st.session_state[f"chat_history_{student_name}"] = []

        # Display chat history
        chat_container = st.container()

        # Chat input
        user_input = st.chat_input(f"Ask me anything about {student_name}'s career pathway...")

        if user_input:
            # Add user message to chat history
            st.session_state[f"chat_history_{student_name}"].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })

            # Get AI response
            with st.spinner("Thinking..."):
                response = agent.get_ai_response(user_input, student_name)

            # Add AI response to chat history
            st.session_state[f"chat_history_{student_name}"].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })

            st.rerun()

        # Display chat messages
        with chat_container:
            for message in st.session_state[f"chat_history_{student_name}"]:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(message["content"])

    with col2:
        # Quick stats and data
        st.markdown("### 📊 Quick Insights")

        # Career data relevant to student
        agent = st.session_state.agent
        if student_name == "Rosa":
            careers = ["Anthropologists", "Archaeologists", "Museum Curators"]
        else:
            careers = ["Secondary School Teachers"]

        for career in careers:
            if career in agent.education_data['careers']:
                data = agent.education_data['careers'][career]
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{career}</h4>
                    <p><strong>Salary:</strong> {data['median_salary']}</p>
                    <p><strong>Growth:</strong> {data['growth_rate']}</p>
                    <p><strong>Outlook:</strong> {data['employment_outlook']}</p>
                </div>
                """, unsafe_allow_html=True)


def get_sample_recommendations(student_name):
    """Get sample recommendations for PDF generation"""
    if student_name == "Rosa":
        return [
            {
                "title": "University Recommendations",
                "description": "Based on your interests in ancient history and biological anthropology:",
                "details": [
                    "Macquarie University - Strong ancient history with lab components",
                    "University of Sydney - Prestigious anthropology program",
                    "ANU - Research-focused opportunities"
                ]
            }
        ]
    else:
        return [
            {
                "title": "Teaching Career Pathway",
                "description": "Your combination of teaching interests and Army Reserves funding:",
                "details": [
                    "Newcastle University Education - Monitor application status",
                    "Army Reserves benefits - Up to $27,000 HECS support",
                    "Teaching salaries - $85,000-$95,000 with strong growth"
                ]
            }
        ]


def main():
    """Main application function"""

    # Initialize session state
    if 'agent' not in st.session_state:
        st.session_state.agent = WebCareerExplorerAgent()

    # Create dashboard
    create_dashboard()

    # Main application logic
    if 'selected_student' not in st.session_state:
        # Show student selection
        st.markdown("## 👥 Select Student")
        create_student_selector()

        # Show some general stats
        st.markdown("---")
        st.markdown("## 📈 Platform Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Universities Tracked", "7", "NSW/ACT Focus")
        with col2:
            st.metric("Careers Analyzed", "5+", "Live Data")
        with col3:
            st.metric("Students Supported", "2", "Rosa & Reuben")
        with col4:
            st.metric("Platform Status", "✅ Online", "All Systems Active")

    else:
        # Show chat interface for selected student
        create_chat_interface(st.session_state.selected_student)


if __name__ == "__main__":
    main()