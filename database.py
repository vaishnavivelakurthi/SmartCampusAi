import os
import json
import tempfile
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseUtil")

DATABASE_DIR = "database"
USERS_FILE = os.path.join(DATABASE_DIR, "users.json")
ATTENDANCE_FILE = os.path.join(DATABASE_DIR, "attendance.json")
ASSIGNMENTS_FILE = os.path.join(DATABASE_DIR, "assignments.json")
ANNOUNCEMENTS_FILE = os.path.join(DATABASE_DIR, "announcements.json")
NOTES_FILE = os.path.join(DATABASE_DIR, "notes.json")
TIMETABLE_FILE = os.path.join(DATABASE_DIR, "timetable.json")
CHAT_HISTORY_FILE = os.path.join(DATABASE_DIR, "chat_history.json")

def create_file_if_missing(file_path: str, default_data) -> None:
    """Creates the target file with default_data if it does not exist or is empty."""
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        save_json(file_path, default_data)
        logger.info(f"Initialized database file: {file_path}")

def load_json(file_path: str):
    """Safely loads a JSON file from disk."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        # Return None to signal corruption or read failure
        return None

def save_json(file_path: str, data) -> bool:
    """Atomically saves data to a JSON file using a temp file to prevent corruption."""
    dir_name = os.path.dirname(file_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
        
    temp_fd, temp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8') as tmp_file:
            json.dump(data, tmp_file, indent=2, ensure_ascii=False)
        
        # Atomic replacement of the file
        if os.path.exists(file_path):
            os.replace(temp_path, file_path)
        else:
            os.rename(temp_path, file_path)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return False

def initialize_databases() -> None:
    """Pre-populates the database folder with empty or default records for each file."""
    # 1. Users File
    create_file_if_missing(USERS_FILE, {})
    
    # 2. Attendance File
    create_file_if_missing(ATTENDANCE_FILE, {})
    
    # 3. Assignments File
    create_file_if_missing(ASSIGNMENTS_FILE, {})
    
    # 4. Notes File
    create_file_if_missing(NOTES_FILE, {})
    
    # 5. Chat History File
    create_file_if_missing(CHAT_HISTORY_FILE, {})
    
    # 6. Announcements File
    default_announcements = [
        {
            "id": "ann_001",
            "title": "Welcome to SmartCampusAI Portal!",
            "content": "We are thrilled to launch the new AI-powered student dashboard. Experience automated attendance analytics, interactive assignment boards, custom note keeping, and chat directly with your virtual AI Assistant.",
            "date": "2026-07-14",
            "department": "All",
            "year": "All",
            "author": "Campus Administration"
        },
        {
            "id": "ann_002",
            "title": "Midterm Examination Registrations",
            "content": "All students must submit their exam registration forms online through the official portal before July 30, 2026. Late submissions will incur a fee.",
            "date": "2026-07-13",
            "department": "All",
            "year": "All",
            "author": "Academic Registrar"
        },
        {
            "id": "ann_003",
            "title": "Computer Science Hackathon 2026",
            "content": "Registration is open for the CS Annual Hackathon. Teams of up to 4 can submit their project proposals focusing on AI & Sustainability.",
            "date": "2026-07-12",
            "department": "Computer Science",
            "year": "3rd Year",
            "author": "Department of CS"
        }
    ]
    create_file_if_missing(ANNOUNCEMENTS_FILE, default_announcements)
    
    # 7. Timetable File
    default_timetable = {
        "Computer Science": {
            "3rd Year": {
                "Monday": [
                    {"time": "09:00 - 10:00", "subject": "Neural Networks", "classroom": "Lab A", "instructor": "Dr. Alan Turing"},
                    {"time": "10:15 - 11:15", "subject": "Database Systems", "classroom": "Room 302", "instructor": "Prof. Grace Hopper"},
                    {"time": "11:30 - 12:30", "subject": "Software Engineering", "classroom": "Room 105", "instructor": "Dr. Barbara Liskov"}
                ],
                "Tuesday": [
                    {"time": "09:00 - 10:00", "subject": "Web Development", "classroom": "Lab B", "instructor": "Prof. Tim Berners-Lee"},
                    {"time": "10:15 - 11:15", "subject": "Neural Networks", "classroom": "Lab A", "instructor": "Dr. Alan Turing"},
                    {"time": "14:00 - 16:00", "subject": "Cyber Security Lab", "classroom": "Lab C", "instructor": "Dr. Dorothy Denning"}
                ],
                "Wednesday": [
                    {"time": "09:00 - 10:00", "subject": "Software Engineering", "classroom": "Room 105", "instructor": "Dr. Barbara Liskov"},
                    {"time": "10:15 - 11:15", "subject": "Database Systems", "classroom": "Room 302", "instructor": "Prof. Grace Hopper"},
                    {"time": "11:30 - 12:30", "subject": "Artificial Intelligence", "classroom": "Lab A", "instructor": "Prof. John McCarthy"}
                ],
                "Thursday": [
                    {"time": "09:00 - 10:00", "subject": "Web Development", "classroom": "Lab B", "instructor": "Prof. Tim Berners-Lee"},
                    {"time": "10:15 - 11:15", "subject": "Artificial Intelligence", "classroom": "Lab A", "instructor": "Prof. John McCarthy"}
                ],
                "Friday": [
                    {"time": "09:00 - 10:00", "subject": "Neural Networks", "classroom": "Lab A", "instructor": "Dr. Alan Turing"},
                    {"time": "11:30 - 13:00", "subject": "Technical Seminar", "classroom": "Seminar Hall", "instructor": "Prof. Richard Feynman"}
                ]
            },
            "2nd Year": {
                "Monday": [
                    {"time": "09:00 - 10:00", "subject": "Data Structures", "classroom": "Room 201", "instructor": "Dr. Donald Knuth"},
                    {"time": "10:15 - 11:15", "subject": "Discrete Mathematics", "classroom": "Room 204", "instructor": "Prof. Paul Erdős"}
                ],
                "Wednesday": [
                    {"time": "11:30 - 12:30", "subject": "Computer Architecture", "classroom": "Room 205", "instructor": "Dr. Gene Amdahl"}
                ]
            }
        },
        "Electrical Engineering": {
            "3rd Year": {
                "Monday": [
                    {"time": "09:00 - 10:00", "subject": "Control Systems", "classroom": "Lab D", "instructor": "Dr. Rudolf Kálmán"},
                    {"time": "10:15 - 11:15", "subject": "Power Electronics", "classroom": "Room 112", "instructor": "Dr. Nikola Tesla"}
                ]
            }
        }
    }
    create_file_if_missing(TIMETABLE_FILE, default_timetable)
