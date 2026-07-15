import datetime
import base64
import streamlit as st

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, CHAT_HISTORY_FILE
from utils.ai import generate_chat_response

# Set page config
st.set_page_config(
    page_title="AI Study Assistant - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verify auth status
check_auth_or_redirect()

# Ingest CSS styles and sidebar navigation
apply_custom_css()
render_sidebar("AI Assistant")

# Set active session email
email = st.session_state.user_email

# Load chat histories
chat_db = load_json(CHAT_HISTORY_FILE) or {}
if email not in chat_db:
    chat_db[email] = []
    save_json(CHAT_HISTORY_FILE, chat_db)

history = chat_db[email]

# Render page header
render_page_header(
    title="AI Study Assistant 🤖",
    subtitle="Ask questions, generate study schedules, write code, or summarize complex lecture notes instantly."
)

def get_copy_button_html(text_content: str) -> str:
    """Generates an HTML snippet containing a safe Base64-based text-copying button."""
    encoded_b64 = base64.b64encode(text_content.encode("utf-8")).decode("utf-8")
    return f"""
    <div style="text-align: right;">
        <button onclick="
            var text = atob('{encoded_b64}');
            navigator.clipboard.writeText(text);
            var btn = this;
            btn.innerHTML = '✓ Copied!';
            btn.style.backgroundColor = '#DCFCE7';
            btn.style.color = '#15803D';
            btn.style.borderColor = '#86EFAC';
            setTimeout(function() {{
                btn.innerHTML = '📋 Copy Response';
                btn.style.backgroundColor = '#FFFFFF';
                btn.style.color = '#475569';
                btn.style.borderColor = '#CBD5E1';
            }}, 2000);
        " style="
            border: 1px solid #CBD5E1;
            background-color: #FFFFFF;
            color: #475569;
            border-radius: 6px;
            padding: 4px 12px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        " onmouseover="this.style.backgroundColor='#F8FAFC'" onmouseout="this.style.backgroundColor='#FFFFFF'">
            📋 Copy Response
        </button>
    </div>
    """

# Chat controls container
col_controls1, col_controls2 = st.columns([4, 1])
with col_controls2:
    clear_chat = st.button("🗑️ Clear Chat History", use_container_width=True, type="secondary")
    if clear_chat:
        chat_db[email] = []
        save_json(CHAT_HISTORY_FILE, chat_db)
        history = []
        st.session_state.ai_queries_used = 0
        st.rerun()

# Render chat logs
chat_container = st.container()
with chat_container:
    if not history:
        st.markdown("""
            <div style="text-align: center; padding: 40px; color: #64748B;">
                <p style="font-size: 1.2rem; font-weight: 500;">No messages yet. Start by sending a message below! 👇</p>
                <div style="display: flex; justify-content: center; gap: 10px; margin-top: 15px;">
                    <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #E2E8F0;">Explain Backpropagation</span>
                    <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #E2E8F0;">Recommend a study plan for exams</span>
                    <span style="background: #F1F5F9; padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; border: 1px solid #E2E8F0;">Debug this Python function</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(content)
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)
                    st.markdown(get_copy_button_html(content), unsafe_allow_html=True)

# Input container
user_input = st.chat_input("Ask SmartCampusAI anything...")

if user_input:
    # 1. Show user's input immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
        
    # Append message to list & save to db
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history.append({"role": "user", "content": user_input, "timestamp": now_str})
    chat_db[email] = history
    save_json(CHAT_HISTORY_FILE, chat_db)
    
    # Update AI queries count in session state
    st.session_state.ai_queries_used = st.session_state.get("ai_queries_used", 0) + 1
    
    # 2. Call OpenAI API with loading indicator
    with st.chat_message("assistant", avatar="🤖"):
        # Compile system and historical prompts
        system_prompt = {
            "role": "system",
            "content": f"You are SmartCampusAI, a highly intelligent virtual study assistant at the campus. Assist the student (Name: {st.session_state.user_data.get('full_name')}, Dept: {st.session_state.user_data.get('department')}, Year: {st.session_state.user_data.get('year')}) with their course topics, schedules, coding, and general student life."
        }
        
        # Prepare context (last 10 messages to save tokens/context limits)
        api_messages = [system_prompt]
        for msg in history[-10:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        with st.spinner("AI thinking..."):
            success, response_content = generate_chat_response(api_messages)
            
        st.markdown(response_content)
        st.markdown(get_copy_button_html(response_content), unsafe_allow_html=True)
        
    # Save Assistant Response
    history.append({"role": "assistant", "content": response_content, "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    chat_db[email] = history
    save_json(CHAT_HISTORY_FILE, chat_db)
    st.rerun()
