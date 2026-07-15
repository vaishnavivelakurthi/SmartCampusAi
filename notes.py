import datetime
import streamlit as st

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, NOTES_FILE

# Set page config
st.set_page_config(
    page_title="Lecture Notes - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth status
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Notes")

email = st.session_state.user_email

# Load user notes
notes_db = load_json(NOTES_FILE) or {}
if email not in notes_db:
    notes_db[email] = []
    save_json(NOTES_FILE, notes_db)
    
user_notes = notes_db[email]

# Render page header
render_page_header(
    title="Personal Study Notes 📝",
    subtitle="Draft lecture logs, outline research studies, and keep coursework journals organized."
)

# Establish active note state tracker
if "active_note_id" not in st.session_state:
    st.session_state.active_note_id = None

# Search interface and Notes selector column
col_list, col_edit = st.columns([1, 2])

with col_list:
    st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0; margin-bottom:10px;">My Directory</h4>', unsafe_allow_html=True)
    
    # New note trigger button
    btn_new = st.button("➕ Create New Note", use_container_width=True, type="primary")
    if btn_new:
        st.session_state.active_note_id = None
        st.rerun()
        
    st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)
    
    # Search input
    search_query = st.text_input("🔍 Search Notes", placeholder="Filter by title...").strip().lower()
    
    # Filter notes list
    filtered_notes = user_notes
    if search_query:
        filtered_notes = [
            n for n in user_notes 
            if search_query in n["title"].lower() or search_query in n["content"].lower()
        ]
        
    # Render note list cards
    if not filtered_notes:
        st.info("No matching notes found.")
    else:
        for note in filtered_notes:
            active_border = "border-left: 4px solid #2563EB;" if st.session_state.active_note_id == note["id"] else "border-left: 4px solid #CBD5E1;"
            
            # Note selector layout
            note_card_html = f"""
                <div style="background-color:#FFFFFF; border-radius:8px; border:1px solid #E2E8F0; {active_border} padding:10px; margin-bottom:8px; cursor:pointer;">
                    <div style="font-weight:600; color:#1E293B; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{note['title']}</div>
                    <div style="font-size:0.72rem; color:#94A3B8; margin-top:3px;">Modified: {note['last_modified']}</div>
                </div>
            """
            st.markdown(note_card_html, unsafe_allow_html=True)
            
            # Simple select button
            if st.button(f"Open: {note['title'][:20]}...", key=f"sel_{note['id']}", use_container_width=True):
                st.session_state.active_note_id = note["id"]
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

# Editor screen
with col_edit:
    st.markdown('<div class="custom-card" style="height: 100%;">', unsafe_allow_html=True)
    
    # Find active note details
    active_note = next((n for n in user_notes if n["id"] == st.session_state.active_note_id), None)
    
    if active_note:
        st.markdown(f'<h4 class="subgradient-header" style="margin-top:0;">Edit Note: {active_note["title"]}</h4>', unsafe_allow_html=True)
        
        with st.form("edit_note_form"):
            edit_title = st.text_input("Note Title", value=active_note["title"])
            edit_content = st.text_area("Note Body (Markdown is supported)", value=active_note["content"], height=300)
            
            col_eb1, col_eb2 = st.columns(2)
            with col_eb1:
                save_btn = st.form_submit_button("Save Modifications", use_container_width=True, type="primary")
            with col_eb2:
                delete_btn = st.form_submit_button("Delete Note", use_container_width=True)
                
        if save_btn:
            if not edit_title:
                st.error("Note title cannot be blank.")
            else:
                active_note["title"] = edit_title.strip()
                active_note["content"] = edit_content
                active_note["last_modified"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                notes_db[email] = user_notes
                save_json(NOTES_FILE, notes_db)
                st.success("Note changes saved successfully.")
                st.rerun()
                
        if delete_btn:
            # Delete note from user's lists
            user_notes = [n for n in user_notes if n["id"] != active_note["id"]]
            notes_db[email] = user_notes
            save_json(NOTES_FILE, notes_db)
            st.session_state.active_note_id = None
            st.success("Note deleted successfully.")
            st.rerun()
            
    else:
        # Render "New Note" creation form
        st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Draft New Note</h4>', unsafe_allow_html=True)
        
        with st.form("create_note_form"):
            new_title = st.text_input("Note Title", placeholder="e.g. Algorithms Lecture 1")
            new_content = st.text_area("Note Body (Markdown is supported)", placeholder="Draft note content details...", height=300)
            
            create_btn = st.form_submit_button("Create Note", use_container_width=True, type="primary")
            
        if create_btn:
            if not new_title:
                st.error("Please enter a note title.")
            else:
                note_id = f"note_{int(datetime.datetime.now().timestamp())}"
                new_note_record = {
                    "id": note_id,
                    "title": new_title.strip(),
                    "content": new_content,
                    "last_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                user_notes.append(new_note_record)
                # Sort descending
                user_notes.sort(key=lambda x: x["last_modified"], reverse=True)
                
                notes_db[email] = user_notes
                save_json(NOTES_FILE, notes_db)
                st.session_state.active_note_id = note_id
                st.success("New note successfully drafted.")
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)
