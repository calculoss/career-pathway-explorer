import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from ai_milestone_generator import AIStudyMilestoneGenerator



def add_milestone_generation_to_assignments():
    """Add milestone generation to the Canvas assignments interface"""

    # Initialize milestone generator
    if 'milestone_generator' not in st.session_state:
        st.session_state.milestone_generator = AIStudyMilestoneGenerator()

    milestone_generator = st.session_state.milestone_generator


def show_enhanced_assignments_table(student, canvas_integrator):
    """Enhanced assignments table with milestone generation"""

    st.markdown("#### 📝 Upcoming Assignments & Exams")

    # Initialize milestone generator
    if 'milestone_generator' not in st.session_state:
        st.session_state.milestone_generator = AIStudyMilestoneGenerator()

    milestone_generator = st.session_state.milestone_generator

    # Get assignments
    assignments = canvas_integrator.get_upcoming_assignments(student['id'], days_ahead=90)

    if not assignments:
        st.info(
            "No upcoming assignments or exams found. This might be between assessment periods, or teachers haven't set due dates yet.")

        # Show sync button
        if st.button("🔄 Try Syncing Again"):
            with st.spinner("Syncing assignments and exams..."):
                sync_result = canvas_integrator.sync_assignments(student['id'])
                if sync_result['status'] == 'success':
                    st.success(sync_result['message'])
                else:
                    st.error(f"Sync failed: {sync_result['message']}")
                st.rerun()
        return

    # Count exams vs assignments
    total_assignments = len([a for a in assignments if not a['is_quiz']])
    total_exams = len([a for a in assignments if a['is_quiz']])

    st.markdown(f"**Found:** {total_assignments} assignments • {total_exams} exams/quizzes")

    # Show upcoming milestones summary
    show_milestone_summary(student, milestone_generator)

    # Filter controls
    col1, col2, col3 = st.columns(3)

    with col1:
        days_filter = st.selectbox("Show items due in:", [7, 14, 30, 60, 90], index=2)

    with col2:
        course_names = sorted(list(set([a['course_name'] for a in assignments])))
        course_filter = st.selectbox("Filter by course:", ['All Courses'] + course_names)

    with col3:
        type_filter = st.selectbox("Show:", ['All Items', 'Assignments Only', 'Exams/Quizzes Only'])

    # Filter assignments
    filtered_assignments = []
    cutoff_date = datetime.now() + timedelta(days=days_filter)

    for assignment in assignments:
        try:
            # Date filter
            if assignment['due_date']:
                due_date = assignment['due_date']
                if due_date.tzinfo is not None:
                    due_date = due_date.replace(tzinfo=None)

                if due_date > cutoff_date:
                    continue

            # Course filter
            if course_filter != 'All Courses' and assignment['course_name'] != course_filter:
                continue

            # Type filter
            if type_filter == 'Assignments Only' and assignment['is_quiz']:
                continue
            elif type_filter == 'Exams/Quizzes Only' and not assignment['is_quiz']:
                continue

            filtered_assignments.append(assignment)

        except Exception as e:
            print(f"Skipping assignment due to date error: {e}")
            continue

    if not filtered_assignments:
        st.info("No items match your filters.")
        return

    # Enhanced assignments display with milestone generation
    show_assignments_with_milestones(student, filtered_assignments, milestone_generator)


def show_milestone_summary(student, milestone_generator):
    """Show upcoming milestones summary"""

    milestones = milestone_generator.get_student_milestones(student['id'], days_ahead=7)

    if milestones:
        st.markdown("#### 🎯 Your Study Plan - Next 7 Days")

        upcoming_milestones = [m for m in milestones if not m['completed']]
        completed_today = [m for m in milestones if m['completed'] and
                           (datetime.now() - m.get('completed_date', datetime.now())).days == 0]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("📋 Upcoming Tasks", len(upcoming_milestones))

        with col2:
            st.metric("✅ Completed Today", len(completed_today))

        with col3:
            overdue_milestones = [m for m in upcoming_milestones if m['target_date'] < datetime.now()]
            st.metric("⏰ Overdue", len(overdue_milestones))

        # Show next 3 upcoming milestones
        if upcoming_milestones:
            st.markdown("**Next tasks:**")
            for milestone in upcoming_milestones[:3]:
                days_until = (milestone['target_date'] - datetime.now()).days

                if days_until < 0:
                    urgency = "🔴"
                    time_text = f"Overdue by {abs(days_until)} days"
                elif days_until == 0:
                    urgency = "🔴"
                    time_text = "Due today"
                elif days_until == 1:
                    urgency = "🟡"
                    time_text = "Due tomorrow"
                else:
                    urgency = "🟢"
                    time_text = f"Due in {days_until} days"

                st.markdown(f"{urgency} **{milestone['title']}** ({milestone['course_name']}) - {time_text}")


def show_assignments_with_milestones(student, assignments, milestone_generator):
    """Show assignments with milestone generation options"""

    for assignment in assignments:
        due_date = assignment['due_date']

        # Calculate urgency
        if due_date:
            try:
                if due_date.tzinfo is not None:
                    due_date = due_date.replace(tzinfo=None)

                days_until = (due_date - datetime.now()).days

                if days_until < 0:
                    urgency_color = "#dc2626"
                    urgency_text = f"Overdue by {abs(days_until)} days"
                    urgency_icon = "🔴"
                elif days_until <= 2:
                    urgency_color = "#dc2626"
                    urgency_text = f"Due in {days_until} days"
                    urgency_icon = "🔴"
                elif days_until <= 7:
                    urgency_color = "#f59e0b"
                    urgency_text = f"Due in {days_until} days"
                    urgency_icon = "🟡"
                else:
                    urgency_color = "#10b981"
                    urgency_text = f"Due in {days_until} days"
                    urgency_icon = "🟢"

                date_str = due_date.strftime('%d %b %Y')

            except:
                urgency_color = "#6b7280"
                urgency_text = "Date error"
                urgency_icon = "⚪"
                date_str = "Date error"
        else:
            urgency_color = "#6b7280"
            urgency_text = "No due date"
            urgency_icon = "⚪"
            date_str = "No date"

        # Assignment type
        type_icon = "🎯" if assignment['is_quiz'] else "📝"
        type_text = "EXAM/QUIZ" if assignment['is_quiz'] else "Assignment"

        # Create assignment card with milestone options
        st.markdown(f"""
        <div style="border: 2px solid {urgency_color}; border-radius: 8px; padding: 16px; margin: 12px 0; background: white;">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div style="flex: 1;">
                    <div style="font-size: 18px; font-weight: 600; color: #374151; margin-bottom: 4px;">
                        {type_icon} {assignment['assignment_name']}
                    </div>
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">
                        <strong>{assignment['course_name']}</strong> • {assignment['points_possible']} points
                    </div>
                    <div style="font-size: 14px; color: {urgency_color}; font-weight: 500;">
                        {urgency_icon} {urgency_text} • Due: {date_str}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Milestone section for this assignment
        show_assignment_milestones(student, assignment, milestone_generator)


def show_assignment_milestones(student, assignment, milestone_generator):
    """Show or generate milestones for a specific assignment"""

    # Check if milestones already exist
    existing_milestones = milestone_generator.get_assignment_milestones(
        student['id'],
        str(assignment.get('assignment_id', assignment.get('canvas_assignment_id', '')))
    )

    if existing_milestones:
        # Show existing milestones
        show_existing_milestones(assignment, existing_milestones, milestone_generator)
    else:
        # Show milestone generation option
        show_milestone_generation_option(student, assignment, milestone_generator)


def show_existing_milestones(assignment, milestones, milestone_generator):
    """Display existing milestones for an assignment"""

    with st.expander(f"📋 Study Plan: {assignment['assignment_name']}", expanded=False):
        st.markdown(f"**{len(milestones)} study milestones** for this assignment:")

        # Progress tracking
        completed_count = len([m for m in milestones if m['completed']])
        progress = completed_count / len(milestones) if milestones else 0

        st.progress(progress, text=f"Progress: {completed_count}/{len(milestones)} completed")

        # Show milestones
        for i, milestone in enumerate(milestones, 1):
            days_until = (milestone['target_date'] - datetime.now()).days

            # Status icon and color
            if milestone['completed']:
                status_icon = "✅"
                status_color = "#10b981"
                status_text = "Completed"
            elif days_until < 0:
                status_icon = "🔴"
                status_color = "#dc2626"
                status_text = f"Overdue by {abs(days_until)} days"
            elif days_until == 0:
                status_icon = "🔴"
                status_color = "#dc2626"
                status_text = "Due today"
            elif days_until <= 2:
                status_icon = "🟡"
                status_color = "#f59e0b"
                status_text = f"Due in {days_until} days"
            else:
                status_icon = "🟢"
                status_color = "#10b981"
                status_text = f"Due in {days_until} days"

            # Milestone card
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"""
                <div style="border-left: 4px solid {status_color}; padding-left: 12px; margin: 8px 0;">
                    <div style="font-weight: 600; color: #374151;">{status_icon} {milestone['title']}</div>
                    <div style="font-size: 14px; color: #6b7280; margin: 4px 0;">{milestone['description']}</div>
                    <div style="font-size: 12px; color: {status_color};">
                        {milestone['target_date'].strftime('%A, %d %b')} • {status_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if not milestone['completed']:
                    if st.button("✅ Complete", key=f"complete_{milestone['id']}", use_container_width=True):
                        success = milestone_generator.mark_milestone_complete(milestone['id'])
                        if success:
                            st.success("Milestone completed!")
                            st.rerun()
                        else:
                            st.error("Failed to mark complete")

        # Regenerate option
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Regenerate Study Plan",
                         key=f"regen_{assignment.get('assignment_id', 'unknown')}",
                         use_container_width=True):
                st.session_state[f"regenerate_{assignment.get('assignment_id')}"] = True
                st.rerun()

        with col2:
            if st.button("📊 View Progress",
                         key=f"progress_{assignment.get('assignment_id', 'unknown')}",
                         use_container_width=True):
                show_milestone_progress(milestones)


def show_milestone_generation_option(student, assignment, milestone_generator):
    """Show option to generate milestones for an assignment"""

    # Only show for assignments due more than 1 day away
    due_date = assignment.get('due_date')
    if due_date:
        try:
            if due_date.tzinfo is not None:
                due_date = due_date.replace(tzinfo=None)

            days_until = (due_date - datetime.now()).days

            if days_until > 1:  # More than 1 day away
                with st.expander(f"⭐ Create Study Plan: {assignment['assignment_name']}", expanded=False):
                    st.markdown(f"""
                    **Generate an AI-powered study plan** for this {assignment['course_name']} assessment.

                    The AI will create 4-6 specific milestones to break this assignment into manageable phases:
                    - Research and planning phase
                    - Content development phase  
                    - Writing/creation phase
                    - Review and finalisation phase

                    **Time available:** {days_until} days until due date
                    **Assessment value:** {assignment['points_possible']} points
                    """)

                    if st.button(f"🧠 Generate Smart Study Plan",
                                 key=f"generate_{assignment.get('assignment_id', 'unknown')}",
                                 use_container_width=True):
                        generate_milestones_for_assignment(student, assignment, milestone_generator)
            else:
                st.info(f"⏰ Assignment due very soon ({days_until} days) - focus on final preparation!")
        except:
            pass


def generate_milestones_for_assignment(student, assignment, milestone_generator):
    """Generate milestones for an assignment"""

    with st.spinner("🧠 AI is creating your personalised study plan..."):

        # Get student profile for AI context
        student_profile = get_student_profile(student)

        # Generate milestones
        milestones = milestone_generator.generate_milestones_for_assignment(
            student['id'],
            assignment,
            student_profile
        )

        if milestones:
            st.success(f"✨ Generated {len(milestones)} study milestones for {assignment['assignment_name']}!")
            st.balloons()

            # Show the generated milestones
            st.markdown("**Your new study plan:**")
            for i, milestone in enumerate(milestones, 1):
                days_until = (milestone['target_date'] - datetime.now()).days
                st.markdown(f"**{i}. {milestone['title']}** - Due in {days_until} days")
                st.markdown(f"   {milestone['description']}")

            st.rerun()
        else:
            st.error("Failed to generate milestones. Please try again or contact support.")


def get_student_profile(student):
    """Get student profile for AI context"""

    # Basic profile based on student data
    profile = {
        'student_name': student.get('name', 'Student'),
        'year_level': student.get('year_level', 11),
        'interests': student.get('interests', []),
        'goals': student.get('goals', []),
        'learning_style': 'balanced'  # Could be enhanced with user preferences
    }

    return profile


def show_milestone_progress(milestones):
    """Show milestone progress visualization"""

    st.markdown("#### 📊 Study Progress")

    # Progress by type
    milestone_types = {}
    for milestone in milestones:
        mtype = milestone['type']
        if mtype not in milestone_types:
            milestone_types[mtype] = {'total': 0, 'completed': 0}

        milestone_types[mtype]['total'] += 1
        if milestone['completed']:
            milestone_types[mtype]['completed'] += 1

    # Display progress by type
    for mtype, stats in milestone_types.items():
        progress = stats['completed'] / stats['total'] if stats['total'] > 0 else 0
        st.metric(
            f"{mtype.title()} Phase",
            f"{stats['completed']}/{stats['total']}",
            f"{progress:.0%} complete"
        )


# Update the main Canvas integration to include milestones
def enhanced_show_assignments_table(student, canvas_integrator):
    """Enhanced version of show_assignments_table with milestones"""
    show_enhanced_assignments_table(student, canvas_integrator)