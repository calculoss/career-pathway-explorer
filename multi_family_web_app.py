import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import anthropic
import os
import json
from dotenv import load_dotenv
from multi_family_database import MultiFamilyDatabase

# Page configuration
st.set_page_config(
    page_title="Community Career Pathway Explorer",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .family-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }

    .analytics-card {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }

    .community-header {
        font-size: 2.8rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)



class CommunityCareerExplorerAgent:
    def __init__(self):
        # API setup
        try:
            api_key = st.secrets["ANTHROPIC_API_KEY"]
        except:
            load_dotenv()
            api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = anthropic.Anthropic(api_key=api_key)

        # Initialize database
        if 'community_db' not in st.session_state:
            st.session_state.community_db = MultiFamilyDatabase()

            # Auto-create sample families if none exist
            self.setup_sample_families_if_needed()

        self.db = st.session_state.community_db

    def setup_sample_families_if_needed(self):
        """Create sample families if database is empty"""
        try:
            families = st.session_state.community_db.get_all_families()

            if len(families) == 0:
                # Create sample families for demo
                db = st.session_state.community_db

                # Smith Family (Rosa & Reuben)
                smith_family = db.create_family("Smith Family", "smith@example.com", "Newcastle, NSW")

                db.add_student(smith_family, {
                    'name': 'Rosa',
                    'age': 16,
                    'year_level': 11,
                    'interests': ['ancient history', 'biological anthropology', 'writing'],
                    'preferences': ['lab-based learning'],
                    'timeline': 'applying in 12 months',
                    'location_preference': 'NSW/ACT',
                    'career_considerations': ['research opportunities'],
                    'goals': ['Find university with lab work']
                })

                db.add_student(smith_family, {
                    'name': 'Reuben',
                    'age': 18,
                    'year_level': 12,
                    'interests': ['modern history', 'chinese studies', 'teaching'],
                    'preferences': ['army reserves funding'],
                    'timeline': 'applying now',
                    'location_preference': 'Newcastle/NSW',
                    'career_considerations': ['army reserves compatibility'],
                    'goals': ['Secure teaching placement']
                })

                # Jones Family (Emma)
                jones_family = db.create_family("Jones Family", "jones@example.com", "Sydney, NSW")

                db.add_student(jones_family, {
                    'name': 'Emma',
                    'age': 17,
                    'year_level': 12,
                    'interests': ['psychology', 'social work', 'counseling'],
                    'preferences': ['helping others'],
                    'timeline': 'applying now',
                    'location_preference': 'Sydney/NSW',
                    'career_considerations': ['mental health focus'],
                    'goals': ['University psychology program']
                })

                # Brown Family (Alex)
                brown_family = db.create_family("Brown Family", "brown@example.com", "Canberra, ACT")

                db.add_student(brown_family, {
                    'name': 'Alex',
                    'age': 16,
                    'year_level': 11,
                    'interests': ['computer science', 'engineering', 'technology'],
                    'preferences': ['hands-on projects'],
                    'timeline': 'applying in 12 months',
                    'location_preference': 'ACT/NSW',
                    'career_considerations': ['tech industry'],
                    'goals': ['Top CS program']
                })

                print("✅ Sample families created for cloud deployment")

        except Exception as e:
            print(f"⚠️ Error setting up sample families: {e}")

def create_community_dashboard():
    """Create community platform dashboard"""
    st.markdown('<div class="community-header">🏘️ Community Career Pathway Explorer</div>', unsafe_allow_html=True)

    # Platform features
    features = [
        "✅ Multi-Family Support",
        "✅ Live Australian Employment Data",
        "✅ Community Analytics",
        "✅ Family Progress Tracking",
        "✅ Professional Career Reports"
    ]

    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            st.markdown(
                f'<div style="background: #27ae60; color: white; padding: 0.5rem; border-radius: 15px; text-align: center; font-size: 0.85rem; margin: 0.2rem;">{feature}</div>',
                unsafe_allow_html=True)


def create_community_analytics():
    """Create community analytics dashboard"""
    db = st.session_state.community_db
    analytics = db.get_platform_analytics()

    st.markdown("## 📊 Community Impact Analytics")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="analytics-card">
            <h3>👨‍👩‍👧‍👦</h3>
            <h2>{analytics['total_families']}</h2>
            <p>Families Helped</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="analytics-card">
            <h3>🎓</h3>
            <h2>{analytics['total_students']}</h2>
            <p>Students Guided</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="analytics-card">
            <h3>💬</h3>
            <h2>{analytics['total_conversations']}</h2>
            <p>Total Conversations</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="analytics-card">
            <h3>📈</h3>
            <h2>{analytics['active_families_week']}</h2>
            <p>Active This Week</p>
        </div>
        """, unsafe_allow_html=True)


def create_family_selector():
    """Create family selection interface"""
    db = st.session_state.community_db

    st.markdown("## 👨‍👩‍👧‍👦 Select Your Family")

    # Get all families
    families = db.get_all_families()

    if not families:
        st.info("No families registered yet. Let's add the first family!")
        return create_family_registration()

    # Display family cards
    cols = st.columns(min(3, len(families)))

    for i, family in enumerate(families):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="family-card">
                <h3>👨‍👩‍👧‍👦 {family['family_name']}</h3>
                <p><strong>Students:</strong> {family['student_count']}</p>
                <p><strong>Location:</strong> {family['location'] or 'Not specified'}</p>
                <p><strong>Last Active:</strong> {family['last_active'][:10] if family['last_active'] else 'Never'}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Access {family['family_name']}", key=f"family_{family['id']}", use_container_width=True):
                st.session_state.selected_family_id = family['id']
                st.session_state.selected_family_name = family['family_name']
                st.rerun()

    # Add new family option
    st.markdown("---")
    if st.button("➕ Add New Family", use_container_width=True):
        st.session_state.show_family_registration = True
        st.rerun()


def create_family_registration():
    """Create new family registration form"""
    st.markdown("## ➕ Register New Family")

    with st.form("new_family_form"):
        col1, col2 = st.columns(2)

        with col1:
            family_name = st.text_input("Family Name *", placeholder="e.g., Smith Family")
            email = st.text_input("Email", placeholder="family@email.com")

        with col2:
            location = st.text_input("Location", placeholder="e.g., Sydney, NSW")

        st.markdown("### Add Your First Student")

        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input("Student Name *", placeholder="e.g., Emma")
            age = st.number_input("Age", min_value=14, max_value=20, value=16)
            year_level = st.selectbox("Year Level", [9, 10, 11, 12], index=2)

        with col2:
            interests = st.text_area("Interests", placeholder="e.g., psychology, social work, helping others")
            timeline = st.selectbox("Application Timeline",
                                    ["Applying in 2+ years", "Applying in 12 months", "Applying in 6 months",
                                     "Applying now"])
            location_preference = st.text_input("Location Preference", placeholder="e.g., NSW/ACT")

        submitted = st.form_submit_button("Register Family & Student")

        if submitted:
            if family_name and student_name:
                db = st.session_state.community_db

                # Create family
                family_id = db.create_family(family_name, email, location)

                # Add student
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

                st.success(f"✅ Successfully registered {family_name}!")
                st.session_state.selected_family_id = family_id
                st.session_state.selected_family_name = family_name
                st.rerun()
            else:
                st.error("Please fill in required fields (Family Name and Student Name)")


def create_family_interface(family_id: str, family_name: str):
    """Create interface for selected family"""
    db = st.session_state.community_db

    # Family header
    st.markdown(f"### 👨‍👩‍👧‍👦 {family_name}")

    # Get family students
    students = db.get_family_students(family_id)

    if not students:
        st.info("No students found for this family.")
        return

    # Student selection in sidebar
    with st.sidebar:
        st.markdown(f"### Students in {family_name}")

        for student in students:
            if st.button(f"💬 Chat with {student['name']} (Year {student['year_level']})",
                         key=f"student_{student['id']}", use_container_width=True):
                st.session_state.selected_student = student
                st.rerun()

        st.markdown("---")
        if st.button("🔄 Switch Families", use_container_width=True):
            # Clear selections
            for key in ['selected_family_id', 'selected_family_name', 'selected_student']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Main interface
    if 'selected_student' in st.session_state:
        create_student_chat_interface(st.session_state.selected_student, family_id)
    else:
        # Show family overview
        create_family_overview(students)


def create_student_chat_interface(student: dict, family_id: str):
    """Create chat interface for selected student"""

    # Student header
    st.markdown(f"""
    <div style="background: #3498db; color: white; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h2>💬 Chatting with {student['name']} (Year {student['year_level']})</h2>
        <p><strong>Interests:</strong> {', '.join(student['interests'])}</p>
        <p><strong>Timeline:</strong> {student['timeline']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Simple chat interface
    st.write("**AI Career Counselor Ready!**")

    user_input = st.text_area("Ask a career guidance question:",
                              placeholder=f"What career options are available for {student['name']}'s interests?")

    if st.button("Get Career Guidance", use_container_width=True):
        if user_input:
            # Simple response for demo
            st.write("**Career Counselor Response:**")
            st.write(
                f"Thank you for your question about {student['name']}'s career path. Based on their interests in {', '.join(student['interests'])}, I can provide personalized guidance. This community platform helps families navigate university and career decisions with live Australian employment data.")

            # Save to database (simplified)
            db = st.session_state.community_db
            db.save_conversation(family_id, student['id'], student['name'],
                                 user_input, "Demo response", ['career_guidance'])


def create_family_overview(students):
    """Create overview for family"""
    st.markdown("## 📊 Family Overview")

    # Student cards
    cols = st.columns(min(3, len(students)))

    for i, student in enumerate(students):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 4px solid #3498db; margin: 0.5rem 0;">
                <h4>{student['name']} - Year {student['year_level']}</h4>
                <p><strong>Age:</strong> {student['age']}</p>
                <p><strong>Interests:</strong> {', '.join(student['interests'][:3]) if student['interests'] else 'None specified'}...</p>
                <p><strong>Timeline:</strong> {student['timeline']}</p>
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application function"""

    try:
        # Initialize session state
        if 'agent' not in st.session_state:
            st.session_state.agent = CommunityCareerExplorerAgent()

        # Create dashboard
        create_community_dashboard()

        # Show community analytics
        create_community_analytics()

        # Main application logic
        if 'selected_family_id' not in st.session_state:
            # Show family selection or registration
            if 'show_family_registration' in st.session_state:
                create_family_registration()
            else:
                create_family_selector()
        else:
            # Show family interface
            create_family_interface(
                st.session_state.selected_family_id,
                st.session_state.selected_family_name
            )

    except Exception as e:
        st.error(f"❌ Application Error: {str(e)}")
        st.write("Please refresh the page. If the problem persists, contact support.")

if __name__ == "__main__":
    main()