import datetime
import streamlit as st
import os

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, ASSIGNMENTS_FILE

# Set page config
st.set_page_config(
    page_title="Assignments - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth status
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Assignments")

email = st.session_state.user_email

# Load assignments
assignments_db = load_json(ASSIGNMENTS_FILE) or {}
if email not in assignments_db:
    assignments_db[email] = []
    save_json(ASSIGNMENTS_FILE, assignments_db)
    
user_assignments = assignments_db[email]

# Render page header
render_page_header(
    title="Assignments & Coursework 📝",
    subtitle="Keep track of your projects, submit homework online, and view grading reports."
)

# Split page into tabs
tab_pending, tab_completed, tab_add = st.tabs([
    "📥 Pending Tasks", 
    "✅ Submitted & Graded", 
    "➕ Log New Task"
])

# Define course list
subjects_list = [
    "Neural Networks", "Database Systems", "Software Engineering", 
    "Web Development", "Artificial Intelligence", "Technical Seminar"
]

# --- TAB 1: PENDING ASSIGNMENTS ---
with tab_pending:
    pending_tasks = [a for a in user_assignments if a["status"] == "Pending"]
    
    if not pending_tasks:
        st.success("🎉 Excellent work! No pending assignments on your list.")
    else:
        for idx, task in enumerate(pending_tasks):
            # Parse due date and check if critical (<= 2 days)
            due_date = datetime.datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            days_left = (due_date - datetime.date.today()).days
            
            if days_left < 0:
                due_badge = f'<span style="background-color:#FEE2E2; color:#991B1B; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">Overdue ({abs(days_left)} days ago)</span>'
            elif days_left <= 2:
                due_badge = f'<span style="background-color:#FEF3C7; color:#92400E; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">Due in {days_left} days!</span>'
            else:
                due_badge = f'<span style="background-color:#E0F2FE; color:#0369A1; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">Due in {days_left} days</span>'
                
            st.markdown(f"""
                <div class="custom-card" style="border-left: 5px solid #EF4444;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.15rem; font-weight:700; color:#1E293B;">{task['title']}</span>
                        {due_badge}
                    </div>
                    <div style="font-size:0.82rem; font-weight:600; color:#2563EB; margin: 4px 0;">Subject: {task['subject']}</div>
                    <p style="color:#475569; font-size:0.9rem; margin-top:8px; line-height:1.4;">{task['description']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Submit Section within expander
            with st.expander(f"📥 Submit Submissions for: {task['title']}"):
                with st.form(f"submission_form_{idx}"):
                    submission_text = st.text_area(
                        "Submission Notes / Link to Code Repository", 
                        placeholder="e.g. GitHub link or answer text here..."
                    )
                    uploaded_file = st.file_uploader("Upload File Attachment (optional)", key=f"file_{task['id']}")
                    
                    submit_action = st.form_submit_button("Submit Assignment", use_container_width=True, type="primary")
                    
                if submit_action:
                    # Update status in db
                    task["status"] = "Submitted"
                    task["submission_date"] = datetime.date.today().strftime("%Y-%m-%d")
                    task["submission_text"] = submission_text
                    task["attachment"] = uploaded_file.name if uploaded_file else None
                    task["grade"] = "Pending Grading"
                    
                    assignments_db[email] = user_assignments
                    save_json(ASSIGNMENTS_FILE, assignments_db)
                    st.success(f"Successfully submitted coursework: {task['title']}.")
                    st.rerun()

# --- TAB 2: COMPLETED & GRADED ---
with tab_completed:
    completed_tasks = [a for a in user_assignments if a["status"] in ["Submitted", "Graded"]]
    
    if not completed_tasks:
        st.info("No completed submissions logged. Finish and submit assignments to view them here.")
    else:
        for task in completed_tasks:
            # Setup grade badge
            grade = task.get("grade", "Pending Grading")
            if grade == "Pending Grading":
                grade_badge = '<span style="background-color:#E2E8F0; color:#334155; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">Pending Grade</span>'
            else:
                grade_badge = f'<span style="background-color:#D1FAE5; color:#065F46; padding:3px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">Grade: {grade}</span>'
                
            st.markdown(f"""
                <div class="custom-card" style="border-left: 5px solid #14B8A6;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.1rem; font-weight:700; color:#1E293B;">{task['title']}</span>
                        {grade_badge}
                    </div>
                    <div style="font-size:0.82rem; font-weight:600; color:#14B8A6; margin: 4px 0;">Subject: {task['subject']}</div>
                    <p style="color:#64748B; font-size:0.88rem; margin: 5px 0;">Submitted on: {task.get('submission_date', 'N/A')}</p>
                    <div style="background-color:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:10px; font-size:0.85rem; color:#334155;">
                        <strong>Your submission:</strong><br>{task.get('submission_text', 'No submission text entered.')}
                        { f'<br><br>📎 Attachment: <em>{task.get("attachment")}</em>' if task.get("attachment") else '' }
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 3: ADD NEW TASK ---
with tab_add:
    st.markdown('<div class="custom-card" style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Log Custom Assignment</h4>', unsafe_allow_html=True)
    
    with st.form("create_task_form", clear_on_submit=True):
        new_title = st.text_input("Assignment Title", placeholder="e.g. Calculus Homework 2")
        new_subject = st.selectbox("Course Subject", subjects_list)
        new_desc = st.text_area("Task Guidelines / Instructions", placeholder="Describe the assignment details...")
        new_due = st.date_input("Due Date", datetime.date.today() + datetime.timedelta(days=7))
        
        submit_create = st.form_submit_button("Log Assignment", use_container_width=True, type="primary")
        
    if submit_create:
        if not new_title or not new_desc:
            st.error("Please enter a title and description for the assignment.")
        else:
            new_id = f"assign_{int(datetime.datetime.now().timestamp())}"
            new_task = {
                "id": new_id,
                "title": new_title.strip(),
                "subject": new_subject,
                "description": new_desc.strip(),
                "due_date": new_due.strftime("%Y-%m-%d"),
                "status": "Pending"
            }
            user_assignments.append(new_task)
            assignments_db[email] = user_assignments
            save_json(ASSIGNMENTS_FILE, assignments_db)
            st.success(f"Logged new assignment: {new_title}.")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
