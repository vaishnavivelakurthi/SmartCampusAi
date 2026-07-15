import os
import streamlit as st
from streamlit_option_menu import option_menu
from utils.auth import logout_user

def apply_custom_css():
    """Reads assets/styles.css and injects it into the Streamlit app page."""
    css_path = "assets/styles.css"
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading styles: {e}")

def render_sidebar(current_selection: str):
    """Renders the custom sidebar with app logo, user details, navigation menu, and logout."""
    options = [
        "Dashboard", "AI Assistant", "Notes", "Attendance", 
        "Timetable", "Assignments", "Announcements", "Profile", 
        "Settings", "Logout"
    ]
    icons = [
        "speedometer2", "robot", "journal-text", "calendar-check", 
        "calendar3", "file-earmark-text", "megaphone", "person-badge", 
        "gear", "box-arrow-right"
    ]
    
    try:
        default_index = options.index(current_selection)
    except ValueError:
        default_index = 0
        
    with st.sidebar:
        # Title and logo layout
        st.markdown('<div style="text-align: center; margin-bottom: 10px;">', unsafe_allow_html=True)
        # Verify logo exists
        if os.path.exists("assets/logo.png"):
            st.image("assets/logo.png", width=95)
        st.markdown('<h3 style="margin-top: 10px; margin-bottom: 2px; color: #2563EB; font-weight: 700;">SmartCampusAI</h3>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.8rem; color: #64748B; margin-bottom: 20px;">AI Student Portal</p>', unsafe_allow_html=True)
        
        # User details card
        user_data = st.session_state.get("user_data", {})
        full_name = user_data.get("full_name", "Student User")
        dept = user_data.get("department", "Computer Science")
        st.markdown(f"""
            <div style="background-color: #F8FAFC; border-radius: 12px; padding: 12px 16px; border: 1px solid #E2E8F0; margin-bottom: 25px; text-align: left;">
                <div style="font-weight: 600; color: #1E293B; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{full_name}</div>
                <div style="color: #64748B; font-size: 0.75rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{dept}</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sidebar Option Menu
        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            menu_icon="cast",
            default_index=default_index,
            styles={
                "container": {"padding": "0!important", "background-color": "transparent"},
                "icon": {"color": "#64748B", "font-size": "15px"}, 
                "nav-link": {
                    "font-size": "13px", 
                    "text-align": "left", 
                    "margin": "2px 0px", 
                    "border-radius": "8px",
                    "color": "#334155",
                    "padding-top": "8px",
                    "padding-bottom": "8px",
                    "--hover-color": "#EFF6FF"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
                    "color": "#FFFFFF", 
                    "font-weight": "500"
                },
            }
        )
        
        page_mapping = {
            "Dashboard": "pages/dashboard.py",
            "AI Assistant": "pages/ai_assistant.py",
            "Notes": "pages/notes.py",
            "Attendance": "pages/attendance.py",
            "Timetable": "pages/timetable.py",
            "Assignments": "pages/assignments.py",
            "Announcements": "pages/announcements.py",
            "Profile": "pages/profile.py",
            "Settings": "pages/settings.py"
        }
        
        if selected == "Logout":
            logout_user()
        elif selected != current_selection:
            st.switch_page(page_mapping[selected])

def render_page_header(title: str, subtitle: str):
    """Renders a beautiful modern page header using CSS gradients."""
    st.markdown(f"""
        <div class="welcome-banner">
            <h1 class="gradient-header" style="margin: 0; font-size: 2rem;">{title}</h1>
            <p style="margin: 5px 0 0 0; color: #475569; font-size: 1rem;">{subtitle}</p>
        </div>
    """, unsafe_allow_html=True)
