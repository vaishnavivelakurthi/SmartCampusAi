import streamlit as st

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, USERS_FILE
from utils.security import validate_phone

# Set page config
st.set_page_config(
    page_title="My Profile - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth status
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Profile")

email = st.session_state.user_email
user_data = st.session_state.user_data

# Render page header
render_page_header(
    title="My Institutional Profile 👤",
    subtitle="View your academic record details and update your contact configurations."
)

# Center container
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0; text-align:center;">Student Credentials Card</h4>', unsafe_allow_html=True)
    
    # Profile avatar card
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 25px;">
            <div style="width: 100px; height: 100px; background-color: #EFF6FF; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; border: 2px solid #2563EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <span style="font-size: 3rem; color: #2563EB; font-weight: 700;">{user_data.get('full_name', 'S')[0].upper()}</span>
            </div>
            <h3 style="color: #1E293B; margin-top: 12px; margin-bottom: 2px; font-weight: 700;">{user_data.get('full_name')}</h3>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0;">Student ID: {user_data.get('student_id')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Form
    with st.form("update_profile_form"):
        # Static/Read-only fields
        st.text_input("Email Address (Read-only)", value=email, disabled=True)
        st.text_input("Student ID Number (Read-only)", value=user_data.get("student_id"), disabled=True)
        
        # Editable fields
        new_name = st.text_input("Full Name", value=user_data.get("full_name"))
        new_phone = st.text_input("Phone Number", value=user_data.get("phone"))
        
        col_select1, col_select2 = st.columns(2)
        with col_select1:
            departments = ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration"]
            default_dept_idx = departments.index(user_data.get("department")) if user_data.get("department") in departments else 0
            new_dept = st.selectbox("Department Branch", departments, index=default_dept_idx)
        with col_select2:
            years = ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            default_year_idx = years.index(user_data.get("year")) if user_data.get("year") in years else 0
            new_year = st.selectbox("Academic Year", years, index=default_year_idx)
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_profile = st.form_submit_button("Update Profile Details", use_container_width=True, type="primary")
        
    if submit_profile:
        if not new_name.strip() or not new_phone.strip():
            st.error("Please enter both your name and phone number details.")
        elif not validate_phone(new_phone):
            st.error("Please enter a valid phone number (e.g. +1234567890).")
        else:
            # Save updates
            users = load_json(USERS_FILE) or {}
            if email in users:
                users[email]["full_name"] = new_name.strip()
                users[email]["phone"] = new_phone.strip()
                users[email]["department"] = new_dept
                users[email]["year"] = new_year
                
                if save_json(USERS_FILE, users):
                    # Update local session data
                    st.session_state.user_data = users[email].copy()
                    if "password_hash" in st.session_state.user_data:
                        del st.session_state.user_data["password_hash"]
                        
                    st.success("Profile credentials updated successfully!")
                    st.rerun()
                else:
                    st.error("Could not write update. Database error.")
            else:
                st.error("User record not found in system databases.")
                
    st.markdown('</div>', unsafe_allow_html=True)
