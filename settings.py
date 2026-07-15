import streamlit as st
import os

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, USERS_FILE
from utils.security import verify_password, hash_password, validate_password_strength

# Set page config
st.set_page_config(
    page_title="Settings - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Settings")

email = st.session_state.user_email
user_data = st.session_state.user_data

# Render page header
render_page_header(
    title="Portal Settings ⚙️",
    subtitle="Configure password updates and adjust your virtual study assistant API parameters."
)

tab_security, tab_ai = st.tabs(["🔒 Portal Security", "🤖 AI Assistant Configurations"])

# --- TAB 1: PORTAL SECURITY (PASSWORD CHANGE) ---
with tab_security:
    st.markdown('<div class="custom-card" style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Change Access Password</h4>', unsafe_allow_html=True)
    
    with st.form("change_password_form", clear_on_submit=True):
        old_pwd = st.text_input("Current Password", type="password", placeholder="••••••••")
        new_pwd = st.text_input("New Password (Min 6 chars)", type="password", placeholder="••••••••")
        confirm_pwd = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
        
        submit_pwd = st.form_submit_button("Update Password", use_container_width=True, type="primary")
        
    if submit_pwd:
        if not all([old_pwd, new_pwd, confirm_pwd]):
            st.error("Please fill out all password fields.")
        elif new_pwd != confirm_pwd:
            st.error("New password inputs do not match.")
        else:
            # Load users to authenticate current password
            users = load_json(USERS_FILE) or {}
            user_record = users.get(email, {})
            
            # Verify old password
            if not verify_password(old_pwd, user_record.get("password_hash", "")):
                st.error("Your current password is incorrect.")
            else:
                # Validate strength
                is_strong, strength_err = validate_password_strength(new_pwd)
                if not is_strong:
                    st.error(strength_err)
                else:
                    # Hash and update
                    user_record["password_hash"] = hash_password(new_pwd)
                    users[email] = user_record
                    if save_json(USERS_FILE, users):
                        st.success("Your password has been changed successfully.")
                    else:
                        st.error("Could not write changes. Database write error.")
                        
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: AI CONFIGURATION OVERRIDES ---
with tab_ai:
    st.markdown('<div class="custom-card" style="max-width: 600px; margin: 0 auto;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">API Override Control</h4>', unsafe_allow_html=True)
    st.markdown("""
        Configure custom endpoint parameters for your AI Assistant. 
        You can use system defaults, configure your own OpenAI key, or connect to custom endpoints (like OpenRouter).
    """)
    
    # Get current configurations
    active_override = st.session_state.get("api_override", {})
    
    # Pre-populate fields
    current_key = active_override.get("api_key") or ""
    current_url = active_override.get("base_url") or "https://api.openai.com/v1"
    current_model = active_override.get("model_name") or "gpt-4o-mini"
    
    with st.form("ai_override_form"):
        # API Key input with password masking
        api_key_input = st.text_input(
            "API Authentication Key", 
            value=current_key, 
            type="password", 
            placeholder="e.g. sk-proj-..."
        )
        base_url_input = st.text_input(
            "API Target Base URL", 
            value=current_url, 
            placeholder="e.g. https://api.openai.com/v1"
        )
        model_input = st.text_input(
            "Model Identifier Name", 
            value=current_model, 
            placeholder="e.g. gpt-4o-mini"
        )
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            save_override = st.form_submit_button("Save Config Override", use_container_width=True, type="primary")
        with col_s2:
            reset_override = st.form_submit_button("Restore Defaults", use_container_width=True)
            
    if save_override:
        # Save values directly to active session overrides
        st.session_state.api_override = {
            "api_key": api_key_input.strip(),
            "base_url": base_url_input.strip(),
            "model_name": model_input.strip()
        }
        st.success("API settings overridden for this session. Chatbot will use these configurations.")
        
    if reset_override:
        # Reset overrides to default
        st.session_state.api_override = {}
        st.success("API configurations reset to default environment settings.")
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)
