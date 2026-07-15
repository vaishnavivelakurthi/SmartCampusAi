import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import (
    load_json, ATTENDANCE_FILE, ASSIGNMENTS_FILE, 
    TIMETABLE_FILE, ANNOUNCEMENTS_FILE
)

# Set page config
st.set_page_config(
    page_title="Dashboard - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verify user is logged in
check_auth_or_redirect()

# Inject styling and sidebar
apply_custom_css()
render_sidebar("Dashboard")

# Load session state variables
user_data = st.session_state.user_data
email = st.session_state.user_email
full_name = user_data.get("full_name", "Student")
dept = user_data.get("department", "Computer Science")
year = user_data.get("year", "3rd Year")

# Render header
render_page_header(
    title=f"Welcome back, {full_name}! 👋",
    subtitle=f"Here is your academic overview for today. Department: {dept} | Year: {year}"
)

# --- DATABASE QUERIES & COMPUTATIONS ---

# 1. Calculate Attendance metrics
attendance_db = load_json(ATTENDANCE_FILE) or {}
user_att = attendance_db.get(email, [])

p_count = sum(1 for r in user_att if r["status"] == "Present")
tot_count = len(user_att)
attendance_pct = (p_count / tot_count * 100) if tot_count > 0 else 0.0

# 2. Calculate Assignment metrics
assignments_db = load_json(ASSIGNMENTS_FILE) or {}
user_assign = assignments_db.get(email, [])
pending_count = sum(1 for a in user_assign if a["status"] == "Pending")
submitted_count = sum(1 for a in user_assign if a["status"] in ["Submitted", "Graded"])

# 3. Retrieve schedule
timetable_db = load_json(TIMETABLE_FILE) or {}
dept_timetable = timetable_db.get(dept, {}).get(year, {})
current_day = datetime.datetime.now().strftime("%A")

# If weekend, default preview to Monday so screen isn't empty
is_weekend = current_day not in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
display_day = "Monday" if is_weekend else current_day
today_classes = dept_timetable.get(display_day, [])
classes_count = len(today_classes)

# 4. Upcoming events from announcements
announcements_db = load_json(ANNOUNCEMENTS_FILE) or []
filtered_ann = [
    a for a in announcements_db 
    if a["department"] in ["All", dept] and a["year"] in ["All", year]
]
upcoming_events_count = len(filtered_ann)

# 5. Retrieve AI Queries
queries_used = st.session_state.get("ai_queries_used", 0)

# --- METRIC CARDS SECTION ---
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

with col_m1:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #2563EB;">
            <div class="metric-title">Total Attendance</div>
            <div class="metric-val">{attendance_pct:.1f}%</div>
        </div>
    """, unsafe_allow_html=True)
    
with col_m2:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #14B8A6;">
            <div class="metric-title">Classes { ' (Mon)' if is_weekend else 'Today' }</div>
            <div class="metric-val">{classes_count} Lectures</div>
        </div>
    """, unsafe_allow_html=True)
    
with col_m3:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #EF4444;">
            <div class="metric-title">Pending Tasks</div>
            <div class="metric-val">{pending_count} Assigns</div>
        </div>
    """, unsafe_allow_html=True)
    
with col_m4:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #F59E0B;">
            <div class="metric-title">AI Queries Used</div>
            <div class="metric-val">{queries_used} Prompts</div>
        </div>
    """, unsafe_allow_html=True)

with col_m5:
    st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #8B5CF6;">
            <div class="metric-title">Recent Bulletins</div>
            <div class="metric-val">{upcoming_events_count} Notices</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- PLOTLY CHARTS SECTION ---
col_ch1, col_ch2 = st.columns(2)

with col_ch1:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin: 0 0 15px 0;">Attendance Breakdown by Subject</h4>', unsafe_allow_html=True)
    if user_att:
        df_att = pd.DataFrame(user_att)
        df_grouped = df_att.groupby(["subject", "status"]).size().reset_index(name="Count")
        
        fig_att = px.bar(
            df_grouped,
            x="subject",
            y="Count",
            color="status",
            barmode="group",
            color_discrete_map={"Present": "#14B8A6", "Absent": "#EF4444"},
            labels={"subject": "Subject", "Count": "Lectures Count", "status": "Attendance"}
        )
        fig_att.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_att, use_container_width=True)
    else:
        st.info("No attendance log data available yet.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_ch2:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin: 0 0 15px 0;">Assignment Completion Status</h4>', unsafe_allow_html=True)
    if user_assign:
        df_assign = pd.DataFrame(user_assign)
        status_counts = df_assign["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        
        fig_pie = px.pie(
            status_counts,
            values="count",
            names="status",
            color="status",
            color_discrete_map={"Pending": "#EF4444", "Submitted": "#2563EB", "Graded": "#14B8A6"},
            hole=0.4
        )
        fig_pie.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
        )
        fig_pie.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#FFFFFF', width=2)))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No assignment records found.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- DAILY SCHEDULE & BULLETINS LIST ---
col_inf1, col_inf2 = st.columns([3, 2])

with col_inf1:
    st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown(f'<h4 class="subgradient-header" style="margin: 0 0 10px 0;">Class Schedule preview for {display_day} { "(Weekend Preview)" if is_weekend else "" }</h4>', unsafe_allow_html=True)
    
    if today_classes:
        # Create standard schedule table list
        schedule_html = """
        <table class="timetable-table">
            <thead>
                <tr>
                    <th class="timetable-th">Time</th>
                    <th class="timetable-th">Subject</th>
                    <th class="timetable-th">Classroom</th>
                    <th class="timetable-th">Instructor</th>
                </tr>
            </thead>
            <tbody>
        """
        for item in today_classes:
            schedule_html += f"""
                <tr class="timetable-tr">
                    <td class="timetable-td" style="font-weight:600; color:#2563EB;">{item['time']}</td>
                    <td class="timetable-td">{item['subject']}</td>
                    <td class="timetable-td"><span style="background-color:#E2E8F0; padding:2px 6px; border-radius:4px; font-size:0.8rem;">{item['classroom']}</span></td>
                    <td class="timetable-td">{item['instructor']}</td>
                </tr>
            """
        schedule_html += "</tbody></table>"
        st.markdown(schedule_html, unsafe_allow_html=True)
    else:
        st.info("No lectures scheduled for today.")
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_inf2:
    st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin: 0 0 15px 0;">Recent Campus Announcements</h4>', unsafe_allow_html=True)
    
    if filtered_ann:
        # Show top 3 announcements
        for ann in filtered_ann[:3]:
            st.markdown(f"""
                <div class="announcement-box">
                    <div style="font-weight:700; color:#1E293B; font-size:0.95rem;">{ann['title']}</div>
                    <div style="color:#64748B; font-size:0.75rem; margin-bottom: 5px;">Published on {ann['date']} by {ann.get('author', 'Admin')}</div>
                    <div style="color:#334155; font-size:0.85rem; line-height: 1.4;">{ann['content'][:140] + '...' if len(ann['content']) > 140 else ann['content']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent announcements found for your group.")
        
    st.markdown('</div>', unsafe_allow_html=True)
