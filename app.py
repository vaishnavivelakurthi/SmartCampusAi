import streamlit as st
from utils.database import initialize_databases
from utils.auth import init_session_state, is_logged_in

# Initialize database JSON files and folders on application boot
initialize_databases()

# Establish wide-layout and browser page configs
st.set_page_config(
    page_title="SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize authentication variables inside st.session_state
init_session_state()

# Handle redirection based on authentication state
if is_logged_in():
    st.switch_page("pages/dashboard.py")
else:
    st.switch_page("pages/login.py")
