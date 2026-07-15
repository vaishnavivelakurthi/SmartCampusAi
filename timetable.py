import streamlit as st
from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, TIMETABLE_FILE

# Set page config
st.set_page_config(
    page_title="Class Timetable - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth status
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Timetable")

# Get user details
user_data = st.session_state.user_data
user_dept = user_data.get("department", "Computer Science")
user_year = user_data.get("year", "3rd Year")

# Render header
render_page_header(
    title="Academic Timetable 📅",
    subtitle=f"View your weekly lecture schedules, classrooms, and instructors."
)

# Load timetable database
timetable_db = load_json(TIMETABLE_FILE) or {}

# Filters to view other department schedules (pre-populated with user defaults)
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Select Program & Semester</h4>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)
with col_f1:
    dept_keys = list(timetable_db.keys())
    # Ensure user's department is in keys, if not fallback
    default_dept_idx = dept_keys.index(user_dept) if user_dept in dept_keys else 0
    selected_dept = st.selectbox("Department", dept_keys, index=default_dept_idx)

with col_f2:
    year_keys = list(timetable_db.get(selected_dept, {}).keys())
    default_year_idx = year_keys.index(user_year) if user_year in year_keys else 0
    selected_year = st.selectbox("Year / Semester", year_keys, index=default_year_idx)
    
st.markdown('</div>', unsafe_allow_html=True)

# Fetch schedule
schedule = timetable_db.get(selected_dept, {}).get(selected_year, {})

# Render weekly view using tabs
st.markdown('<div class="custom-card">', unsafe_allow_html=True)
st.markdown(f'<h4 class="subgradient-header" style="margin-top:0;">Weekly Schedule for {selected_dept} ({selected_year})</h4>', unsafe_allow_html=True)

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
tabs = st.tabs(weekdays)

for index, day in enumerate(weekdays):
    with tabs[index]:
        day_schedule = schedule.get(day, [])
        
        if day_schedule:
            # Render schedule table
            table_html = f"""
            <table class="timetable-table">
                <thead>
                    <tr>
                        <th class="timetable-th" style="width: 20%;">Time Slot</th>
                        <th class="timetable-th" style="width: 40%;">Course Subject</th>
                        <th class="timetable-th" style="width: 20%;">Location</th>
                        <th class="timetable-th" style="width: 20%;">Instructor</th>
                    </tr>
                </thead>
                <tbody>
            """
            for slot in day_schedule:
                table_html += f"""
                    <tr class="timetable-tr">
                        <td class="timetable-td" style="font-weight: 600; color: #2563EB;">{slot['time']}</td>
                        <td class="timetable-td" style="font-weight: 500;">{slot['subject']}</td>
                        <td class="timetable-td">
                            <span style="background-color: #F1F5F9; color: #334155; padding: 4px 8px; border-radius: 6px; font-size: 0.82rem; border: 1px solid #E2E8F0;">
                                📍 {slot['classroom']}
                            </span>
                        </td>
                        <td class="timetable-td" style="color: #475569;">{slot['instructor']}</td>
                    </tr>
                """
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="text-align: center; padding: 30px; color: #64748B; background-color: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1;">
                    <p style="font-size: 1rem; margin: 0;">No lectures or lab sessions scheduled for this day. Free study period!</p>
                </div>
            """, unsafe_allow_html=True)
            
st.markdown('</div>', unsafe_allow_html=True)

# Print helper or note
st.markdown("""
    <div style="text-align: right; font-size: 0.8rem; color: #94A3B8; margin-top: -10px;">
        *To print this schedule, press Ctrl + P (Cmd + P on Mac) and select print.
    </div>
""", unsafe_allow_html=True)
