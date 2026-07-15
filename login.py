import streamlit as st
from utils.auth import init_session_state, is_logged_in, login_user
from utils.helpers import apply_custom_css
from utils.security import validate_email

# Set page config
st.set_page_config(
    page_title="Login - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize states and apply layout styles
init_session_state()
apply_custom_css()

# Redirect to dashboard if session is already active
if is_logged_in():
    st.switch_page("pages/dashboard.py")

# Create column grids to center the login container
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    # Stylized logo header
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; margin-bottom: 25px;">', unsafe_allow_html=True)
    st.markdown('<h1 class="gradient-header" style="font-size: 2.2rem; margin-bottom: 5px;">SmartCampusAI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #64748B; font-size: 0.95rem;">University Management & Study Assistant Portal</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Form fields
    with st.form("login_form"):
        email_input = st.text_input("Institutional Email Address", placeholder="student@university.edu").strip()
        password_input = st.text_input("Password", type="password", placeholder="••••••••")
        
        remember_me = st.checkbox("Remember Me")
        
        # Dual submit actions inside the form container
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        with col_btn2:
            submit_forgot = st.form_submit_button("Forgot?", use_container_width=True)
            
    # Process actions
    if submit_login:
        if not email_input or not password_input:
            st.error("Please input both email and password credentials.")
        elif not validate_email(email_input):
            st.error("Please provide a valid institutional email address.")
        else:
            success, message = login_user(email_input, password_input, remember_me)
            if success:
                st.success("Authentication successful! Loading dashboard...")
                st.switch_page("pages/dashboard.py")
            else:
                st.error(message)
                
    if submit_forgot:
        st.info("Password recovery is currently limited. Please contact Campus Administrative Support.")
        
    st.markdown("<hr style='border-top: 1px solid #E2E8F0; margin: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; color: #475569; font-size: 0.9rem;'>", unsafe_allow_html=True)
    st.write("First time logging in?")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Create a Student Account", use_container_width=True, type="secondary"):
        st.switch_page("pages/register.py")
        
    st.markdown('</div>', unsafe_allow_html=True)
