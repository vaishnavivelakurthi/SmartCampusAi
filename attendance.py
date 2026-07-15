import datetime
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, ATTENDANCE_FILE

# Set page config
st.set_page_config(
    page_title="Attendance Tracker - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verify auth
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Attendance")

email = st.session_state.user_email
user_data = st.session_state.user_data
dept = user_data.get("department", "Computer Science")

# Load attendance records
attendance_db = load_json(ATTENDANCE_FILE) or {}
if email not in attendance_db:
    attendance_db[email] = []
    save_json(ATTENDANCE_FILE, attendance_db)
    
records = attendance_db[email]

# Render page header
render_page_header(
    title="Attendance Tracker 📅",
    subtitle="Keep track of your course lectures, view statistics, and ensure you remain above the required 75% limit."
)

# --- ATTENDANCE CALCULATIONS ---
total_classes = len(records)
present_classes = sum(1 for r in records if r["status"] == "Present")
absent_classes = sum(1 for r in records if r["status"] == "Absent")
attendance_pct = (present_classes / total_classes * 100) if total_classes > 0 else 0.0

# Define list of subjects depending on dept
subjects_list = [
    "Neural Networks", "Database Systems", "Software Engineering", 
    "Web Development", "Artificial Intelligence", "Technical Seminar",
    "Computer Architecture", "Data Structures", "Control Systems", "Power Electronics"
]

# Layout splits
col_form, col_stats = st.columns([1, 2])

with col_form:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Log Class Attendance</h4>', unsafe_allow_html=True)
    
    with st.form("add_attendance_form", clear_on_submit=True):
        subject_select = st.selectbox("Course Subject", subjects_list)
        date_select = st.date_input("Date of Lecture", datetime.date.today())
        status_select = st.radio("Status", ["Present", "Absent"], horizontal=True)
        
        submit_btn = st.form_submit_button("Add Record", use_container_width=True, type="primary")
        
    if submit_btn:
        # Check if record already exists for this subject and date to avoid duplicates
        date_str = date_select.strftime("%Y-%m-%d")
        duplicate = any(r["date"] == date_str and r["subject"] == subject_select for r in records)
        
        if duplicate:
            st.error("An attendance record for this course on this date already exists.")
        else:
            new_record = {
                "date": date_str,
                "subject": subject_select,
                "status": status_select
            }
            records.append(new_record)
            # Sort records by date descending
            records.sort(key=lambda x: x["date"], reverse=True)
            
            attendance_db[email] = records
            save_json(ATTENDANCE_FILE, attendance_db)
            st.success(f"Log updated: {subject_select} marked as {status_select} for {date_str}.")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_stats:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Attendance Performance Summary</h4>', unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.metric("Total Classes Logged", total_classes)
    with col_c2:
        st.metric("Attended", present_classes)
    with col_c3:
        st.metric("Missed", absent_classes)
    with col_c4:
        # Display warning colors if attendance is critical (< 75%)
        pct_color = "red" if attendance_pct < 75.0 else "green"
        st.markdown(f"""
            <div style="font-size:0.85rem; color:#64748B; font-weight:600; text-transform:uppercase;">Attendance Rate</div>
            <div style="font-size:1.8rem; font-weight:700; color:{pct_color};">{attendance_pct:.1f}%</div>
        """, unsafe_allow_html=True)
        
    if attendance_pct < 75.0 and total_classes > 0:
        st.warning("⚠️ Your overall attendance rate has fallen below the university mandatory 75% limit. Attend more lectures to avoid eligibility restrictions.")
    elif total_classes > 0:
        st.success("✅ Good job! Your attendance rate meets the criteria.")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Plotly subject-wise analytics
    if records:
        df = pd.DataFrame(records)
        subject_stats = df.groupby(["subject", "status"]).size().unstack(fill_value=0).reset_index()
        
        # Ensure columns exist
        if "Present" not in subject_stats.columns:
            subject_stats["Present"] = 0
        if "Absent" not in subject_stats.columns:
            subject_stats["Absent"] = 0
            
        subject_stats["Total"] = subject_stats["Present"] + subject_stats["Absent"]
        subject_stats["Rate"] = (subject_stats["Present"] / subject_stats["Total"] * 100)
        
        # Display subject-wise progress bars and details
        st.markdown('<div class="custom-card" style="margin-top:20px;">', unsafe_allow_html=True)
        st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Subject-wise Attendance Rate</h4>', unsafe_allow_html=True)
        
        for idx, row in subject_stats.iterrows():
            sub_name = row["subject"]
            present_val = row["Present"]
            total_val = row["Total"]
            rate_val = row["Rate"]
            
            # Progress bar colors
            bar_color = "#14B8A6" if rate_val >= 75.0 else "#EF4444"
            st.markdown(f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.88rem; font-weight:600; color:#334155;">
                        <span>{sub_name} ({present_val}/{total_val})</span>
                        <span style="color:{bar_color};">{rate_val:.1f}%</span>
                    </div>
                    <div style="background-color:#E2E8F0; border-radius:4px; height:8px; width:100%; margin-top:4px;">
                        <div style="background-color:{bar_color}; border-radius:4px; height:8px; width:{rate_val}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

# --- RECENT ATTENDANCE LOG TABLE ---
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Attendance History Log</h4>', unsafe_allow_html=True)

if records:
    # Build history display table
    hist_html = """
    <table class="timetable-table">
        <thead>
            <tr>
                <th class="timetable-th" style="width: 25%;">Date</th>
                <th class="timetable-th" style="width: 50%;">Subject Course</th>
                <th class="timetable-th" style="width: 25%;">Status</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in records:
        status_badge = '<span style="background-color:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:12px; font-weight:600; font-size:0.8rem;">Present</span>' if r['status'] == 'Present' else '<span style="background-color:#FEE2E2; color:#991B1B; padding:2px 8px; border-radius:12px; font-weight:600; font-size:0.8rem;">Absent</span>'
        hist_html += f"""
            <tr class="timetable-tr">
                <td class="timetable-td" style="font-weight:600; color:#475569;">{r['date']}</td>
                <td class="timetable-td">{r['subject']}</td>
                <td class="timetable-td">{status_badge}</td>
            </tr>
        """
    hist_html += "</tbody></table>"
    st.markdown(hist_html, unsafe_allow_html=True)
else:
    st.info("No attendance logs available. Add some records in the left column form to initialize your logs.")
    
st.markdown('</div>', unsafe_allow_html=True)
