import datetime
import streamlit as st

from utils.auth import check_auth_or_redirect
from utils.helpers import apply_custom_css, render_sidebar, render_page_header
from utils.database import load_json, save_json, ANNOUNCEMENTS_FILE

# Set page config
st.set_page_config(
    page_title="Announcements - SmartCampusAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Validate auth status
check_auth_or_redirect()

# Ingest CSS and render sidebar
apply_custom_css()
render_sidebar("Announcements")

user_data = st.session_state.user_data
dept = user_data.get("department", "Computer Science")
year = user_data.get("year", "3rd Year")

# Load announcements
announcements = load_json(ANNOUNCEMENTS_FILE) or []

# Render page header
render_page_header(
    title="Campus Bulletin Board 📢",
    subtitle="View general announcements, administrative bulletins, and department notifications."
)

tab_notices, tab_post = st.tabs(["📋 Campus Notices", "✍️ Post Announcement"])

# --- TAB 1: NOTICES VIEW ---
with tab_notices:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Search & Filters</h4>', unsafe_allow_html=True)
    
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    with col_f1:
        # Department options: All, user's department, and other departments stored in database
        dept_options = ["All", dept]
        selected_dept = st.selectbox("Filter Department", dept_options)
        
    with col_f2:
        year_options = ["All", year]
        selected_year = st.selectbox("Filter Academic Year", year_options)
        
    with col_f3:
        search_query = st.text_input("🔍 Search Bulletins", placeholder="Filter by keyword...").strip().lower()
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter announcements list
    filtered_list = []
    for ann in announcements:
        # Check department target matching
        dept_match = ann.get("department") in ["All", selected_dept]
        # Check year target matching
        year_match = ann.get("year") in ["All", selected_year]
        # Check query search matching
        query_match = True
        if search_query:
            query_match = (
                search_query in ann["title"].lower() or 
                search_query in ann["content"].lower() or 
                search_query in ann.get("author", "").lower()
            )
            
        if dept_match and year_match and query_match:
            filtered_list.append(ann)
            
    # Sort announcements: newest date first
    # Dates are in format YYYY-MM-DD
    filtered_list.sort(key=lambda x: x["date"], reverse=True)
    
    # Render notices
    if not filtered_list:
        st.info("No announcements matching your search criteria.")
    else:
        for ann in filtered_list:
            # Highlight target badges
            target_dept = ann.get("department", "All")
            target_year = ann.get("year", "All")
            
            badge_html = f"""
                <span style="background-color:#EFF6FF; color:#2563EB; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; border:1px solid #DBEAFE; margin-right:5px;">Dept: {target_dept}</span>
                <span style="background-color:#F5F5F5; color:#4B5563; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:600; border:1px solid #E5E5E5;">Year: {target_year}</span>
            """
            
            st.markdown(f"""
                <div class="custom-card" style="border-left: 5px solid #F59E0B;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                        <span style="font-size:1.15rem; font-weight:700; color:#1E293B;">{ann['title']}</span>
                        <div>{badge_html}</div>
                    </div>
                    <div style="font-size:0.78rem; color:#64748B; margin: 6px 0;">
                        Published on <strong>{ann['date']}</strong> by <strong>{ann.get('author', 'Campus Admin')}</strong>
                    </div>
                    <hr style="margin:8px 0; border-top:1px solid #F1F5F9;">
                    <p style="color:#334155; font-size:0.9rem; line-height:1.5; margin:10px 0 0 0;">{ann['content']}</p>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 2: POST NOTICE FORM ---
with tab_post:
    st.markdown('<div class="custom-card" style="max-width:600px; margin:0 auto;">', unsafe_allow_html=True)
    st.markdown('<h4 class="subgradient-header" style="margin-top:0;">Publish New Bulletin</h4>', unsafe_allow_html=True)
    
    with st.form("post_announcement_form", clear_on_submit=True):
        post_title = st.text_input("Bulletin Title", placeholder="e.g. Artificial Intelligence Workshop Rescheduled")
        post_author = st.text_input("Publishing Authority / Author Name", value=st.session_state.user_data.get("full_name", "Administration"))
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            post_dept = st.selectbox("Target Department", ["All", dept, "Electrical Engineering", "Mechanical Engineering", "Civil Engineering", "Business Administration"])
        with col_p2:
            post_year = st.selectbox("Target Year Group", ["All", year, "1st Year", "2nd Year", "4th Year"])
            
        post_content = st.text_area("Detailed Announcement Text", placeholder="Write notification message...")
        
        submit_post = st.form_submit_button("Post Announcement", use_container_width=True, type="primary")
        
    if submit_post:
        if not post_title or not post_content:
            st.error("Please fill in the title and description content of the announcement.")
        else:
            new_ann_id = f"ann_{int(datetime.datetime.now().timestamp())}"
            new_ann = {
                "id": new_ann_id,
                "title": post_title.strip(),
                "content": post_content.strip(),
                "date": datetime.date.today().strftime("%Y-%m-%d"),
                "department": post_dept,
                "year": post_year,
                "author": post_author.strip()
            }
            announcements.append(new_ann)
            save_json(ANNOUNCEMENTS_FILE, announcements)
            st.success("New bulletin posted successfully!")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
