import streamlit as st
import datetime
from utils.database import (
    load_json, save_json, USERS_FILE, ATTENDANCE_FILE, 
    ASSIGNMENTS_FILE, NOTES_FILE, CHAT_HISTORY_FILE
)
from utils.security import verify_password, hash_password

def init_session_state():
    """Initializes Streamlit session state parameters."""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "api_override" not in st.session_state:
        st.session_state.api_override = {}

def is_logged_in() -> bool:
    """Returns True if user is authenticated."""
    return st.session_state.get("logged_in", False)

def login_user(email: str, password: str, remember_me: bool = False) -> tuple[bool, str]:
    """Authenticates user against users.json and updates session state."""
    email = email.strip().lower()
    users = load_json(USERS_FILE)
    
    if not users or email not in users:
        return False, "Invalid email or password."
        
    user_data = users[email]
    
    if verify_password(password, user_data.get("password_hash", "")):
        st.session_state.logged_in = True
        st.session_state.user_email = email
        # Store user metadata (strip password hash for security in session state)
        session_user_data = user_data.copy()
        if "password_hash" in session_user_data:
            del session_user_data["password_hash"]
        st.session_state.user_data = session_user_data
        
        # Load AI queries count from history
        chat_hist = load_json(CHAT_HISTORY_FILE) or {}
        user_history = chat_hist.get(email, [])
        user_queries = sum(1 for msg in user_history if msg.get("role") == "user")
        st.session_state.ai_queries_used = user_queries
        
        return True, "Login successful!"
    else:
        return False, "Invalid email or password."

def register_user(
    full_name: str, 
    student_id: str, 
    email: str, 
    phone: str, 
    department: str, 
    year: str, 
    password: str
) -> tuple[bool, str]:
    """Registers a new user, hashes password, and pre-seeds demo data."""
    email = email.strip().lower()
    users = load_json(USERS_FILE) or {}
    
    if email in users:
        return False, "A user with this email address already exists."
        
    # Check duplicate student ID
    for u_email, u_info in users.items():
        if u_info.get("student_id") == student_id:
            return False, "A user with this Student ID already exists."
            
    # Hash password and create record
    hashed = hash_password(password)
    new_user = {
        "full_name": full_name.strip(),
        "student_id": student_id.strip(),
        "email": email,
        "phone": phone.strip(),
        "department": department,
        "year": year,
        "password_hash": hashed,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    users[email] = new_user
    if not save_json(USERS_FILE, users):
        return False, "Failed to save user records. Contact support."
        
    # Pre-seed realistic Attendance records (target attendance: 80%)
    attendance = load_json(ATTENDANCE_FILE) or {}
    attendance[email] = [
        {"date": "2026-07-06", "subject": "Neural Networks", "status": "Present"},
        {"date": "2026-07-06", "subject": "Database Systems", "status": "Present"},
        {"date": "2026-07-07", "subject": "Web Development", "status": "Present"},
        {"date": "2026-07-07", "subject": "Cyber Security Lab", "status": "Present"},
        {"date": "2026-07-08", "subject": "Software Engineering", "status": "Absent"},
        {"date": "2026-07-08", "subject": "Database Systems", "status": "Present"},
        {"date": "2026-07-09", "subject": "Web Development", "status": "Present"},
        {"date": "2026-07-09", "subject": "Artificial Intelligence", "status": "Present"},
        {"date": "2026-07-10", "subject": "Neural Networks", "status": "Present"},
        {"date": "2026-07-10", "subject": "Technical Seminar", "status": "Absent"},
        {"date": "2026-07-13", "subject": "Neural Networks", "status": "Present"},
        {"date": "2026-07-13", "subject": "Database Systems", "status": "Present"}
    ]
    save_json(ATTENDANCE_FILE, attendance)
    
    # Pre-seed Assignments (1 Submitted, 2 Pending)
    assignments = load_json(ASSIGNMENTS_FILE) or {}
    assignments[email] = [
        {
            "id": "assign_1",
            "title": "Machine Learning Lab 1",
            "subject": "Neural Networks",
            "description": "Implement backpropagation algorithm from scratch in Python using only NumPy.",
            "due_date": "2026-07-20",
            "status": "Pending"
        },
        {
            "id": "assign_2",
            "title": "Database Schema Design",
            "subject": "Database Systems",
            "description": "Create a normalized relational schema (up to BCNF) for a library system.",
            "due_date": "2026-07-18",
            "status": "Pending"
        },
        {
            "id": "assign_3",
            "title": "HTML5 & CSS Grid Layout",
            "subject": "Web Development",
            "description": "Construct a responsive grid gallery mockup with CSS hover transitions.",
            "due_date": "2026-07-10",
            "status": "Submitted"
        }
    ]
    save_json(ASSIGNMENTS_FILE, assignments)
    
    # Pre-seed Notes
    notes = load_json(NOTES_FILE) or {}
    notes[email] = [
        {
            "id": "note_1",
            "title": "Exam Prep Cheatsheet",
            "content": "Database key concepts:\n- 1NF: Atomic values\n- 2NF: No partial dependency\n- 3NF: No transitive dependency\n- BCNF: For every functional dependency X -> Y, X must be a superkey.",
            "last_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    save_json(NOTES_FILE, notes)
    
    # Pre-seed empty Chat History
    chat_hist = load_json(CHAT_HISTORY_FILE) or {}
    chat_hist[email] = []
    save_json(CHAT_HISTORY_FILE, chat_hist)
    
    return True, "Registration successful!"

def logout_user():
    """Logs the user out and clears session state credentials."""
    st.session_state.logged_in = False
    st.session_state.user_email = None
    st.session_state.user_data = {}
    st.switch_page("app.py")

def check_auth_or_redirect():
    """Verifies user authentication on each page; redirects to login if unauthorized."""
    init_session_state()
    if not is_logged_in():
        st.warning("Unauthorized access. Please login first.")
        st.switch_page("app.py")
        st.stop()
