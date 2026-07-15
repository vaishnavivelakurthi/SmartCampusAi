import streamlit as st
from utils.auth import init_session_state, is_logged_in, register_user
from utils.helpers import apply_custom_css
from utils.security import (
    validate_email, validate_phone, validate_password_strength
)

# Set page config
st.set_page_config(
    page_title="Register - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize states and styles
init_session_state()
apply_custom_css()

# Redirect to dashboard if logged in
if is_logged_in():
    st.switch_page("pages/dashboard.py")

# Create column layout to center register container
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    st.markdown('<div class="form-container" style="max-width: 600px;">', unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; margin-bottom: 25px;">', unsafe_allow_html=True)
    st.markdown('<h1 class="gradient-header" style="font-size: 2.2rem; margin-bottom: 5px;">Student Registration</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748B; font-size: 0.95rem;">Join the smart campus academic community</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Form
    with st.form("register_form"):
        # Grid layout for inputs
        col_reg1, col_reg2 = st.columns(2)
        with col_reg1:
            full_name = st.text_input("Full Name", placeholder="e.g. John Doe").strip()
            student_id = st.text_input("Student ID Number", placeholder="e.g. STU12345").strip()
        with col_reg2:
            email_address = st.text_input("Institutional Email", placeholder="e.g. john@university.edu").strip()
            phone_number = st.text_input("Phone Number", placeholder="e.g. +1234567890").strip()
            
        col_reg3, col_reg4 = st.columns(2)
        with col_reg3:
            department = st.selectbox(
                "Academic Department",
                ["Computer Science", "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration"]
            )
        with col_reg4:
            academic_year = st.selectbox(
                "Academic Year",
                ["1st Year", "2nd Year", "3rd Year", "4th Year"]
            )
            
        col_reg5, col_reg6 = st.columns(2)
        with col_reg5:
            password = st.text_input("Password", type="password", placeholder="••••••••")
        with col_reg6:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
            
        st.markdown("<br>", unsafe_allow_html=True)
        submit_register = st.form_submit_button("Register Account", use_container_width=True, type="primary")
        
    if submit_register:
        # Form field validations
        if not all([full_name, student_id, email_address, phone_number, password, confirm_password]):
            st.error("Please fill out all input fields.")
        elif not validate_email(email_address):
            st.error("Please enter a valid institutional email address.")
        elif not validate_phone(phone_number):
            st.error("Please enter a valid phone number (e.g. +1234567890).")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            is_strong, pass_err = validate_password_strength(password)
            if not is_strong:
                st.error(pass_err)
            else:
                # Call register user helper
                success, msg = register_user(
                    full_name, student_id, email_address, phone_number, 
                    department, academic_year, password
                )
                if success:
                    st.success("Registration successful! Redirecting to login...")
                    # Delay helper or prompt redirect
                    st.info("Click the 'Back to Login' button to sign in.")
                else:
                    st.error(msg)
                    
    st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
    if st.button("Back to Login", use_container_width=True, type="secondary"):
        st.switch_page("pages/login.py")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
