# SmartCampusAI 🎓

SmartCampusAI is a production-ready, AI-powered university management portal built using **Python** and **Streamlit**. It provides students with an engaging dashboard, integrated AI Assistant chatbot, notes management, attendance tracker, assignments board, announcements bulletin, and class schedules.

The application features a modern, responsive UI with customized brand gradients, secure session-state based routing, local JSON file-based database storage, and robust security measures including bcrypt password hashing.

---

## Features

1. **Secure Authentication**: Register and login with validation checks, duplicate email checks, and hashed credentials.
2. **Interactive Dashboard**: Metric summary cards (Attendance, Today's Classes, Pending Assignments) alongside dynamic Plotly visual insights.
3. **AI Study Assistant**: Chatbot page featuring rich Markdown responses, syntax code formatting, copy responses, and saved chat logs.
4. **Attendance Tracker**: Visual metrics, interactive logs, and history of student attendance.
5. **Class Timetable**: Standardized weekly lecture calendar.
6. **Assignments Tracker**: Actionable Kanban style listings for assignments (Pending, Submitted, Graded).
7. **Personal Notes**: Dynamic notepad allowing CRUD operations for student notes.
8. **Announcements**: Announcements board filtered by department and academic year.
9. **Student Profile**: Secure profile records showing personal metadata.
10. **Application Settings**: Manage password updates and custom AI endpoint configurations.

---

## Folder Structure

```
SmartCampusAI/
├── app.py                     # Main router & entry point
├── pages/                     # Sub-pages (Dynamic routing)
│   ├── login.py
│   ├── register.py
│   ├── dashboard.py
│   ├── ai_assistant.py
│   ├── attendance.py
│   ├── timetable.py
│   ├── assignments.py
│   ├── notes.py
│   ├── announcements.py
│   ├── profile.py
│   └── settings.py
├── database/                  # JSON files acting as DB tables
│   ├── users.json
│   ├── attendance.json
│   ├── assignments.json
│   ├── announcements.json
│   ├── notes.json
│   ├── timetable.json
│   └── chat_history.json
├── utils/                     # Modular business logic
│   ├── auth.py                # Session control, login & register logic
│   ├── database.py            # JSON operations & seeder methods
│   ├── helpers.py             # Custom HTML/CSS injections & sidebar navigation
│   ├── security.py            # Password hashing & text validation helpers
│   └── ai.py                  # API chat completion interface
├── assets/                    # Static assets
│   ├── logo.png               # Brand icon
│   └── styles.css             # Main styling sheet
├── .env.example               # Template environment variables
├── .gitignore                 # Files excluded from git
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation
└── LICENSE                    # Licensing information
```

---

## Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.11** or higher installed.

### 2. Virtual Environment Setup
Open your terminal (PowerShell, Command Prompt, or bash) and run:

```bash
# Clone the repository and navigate inside
cd smartai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
Run the following command to install required Python libraries:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your OpenAI (or OpenAI-compatible) details:

```bash
copy .env.example .env
```
Open `.env` and enter:
```env
API_KEY=your_openai_compatible_api_key_here
MODEL_NAME=gpt-4o-mini
BASE_URL=https://api.openai.com/v1
```

---

## Running the Project

Start the Streamlit development server:

```bash
streamlit run app.py
```
This command automatically opens your browser at `http://localhost:8501`.

---

## Deployment on Streamlit Cloud

1. Commit your codebase to a public GitHub repository. Ensure `.env` and the contents of `database/` are ignored.
2. Visit [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New app**, select your repository, branch, and set the entry file to `app.py`.
4. Expand **Advanced settings** and set the environment variables (secrets) in the text box:
   ```toml
   API_KEY="your_actual_key"
   MODEL_NAME="gpt-4o-mini"
   BASE_URL="https://api.openai.com/v1"
   ```
5. Click **Deploy!**

---

## Screenshots Placeholder
Here are some visual placeholders of the modern UI:
- **Dashboard Overview**: ![Dashboard Screenshot](assets/logo.png)
- **AI Chatbot interface**: ![Chatbot Screenshot](assets/logo.png)

---

## Troubleshooting

* **Missing API Key**: If the chatbot displays an error or warning about missing API configuration, navigate to the **Settings** page within the app to override or check your API key, or check that your `.env` contains a valid key.
* **Streamlit Option Menu Styling**: If colors are not showing correctly, verify that `assets/styles.css` is successfully loaded by checking developer console logs.
* **Corrupt JSON Files**: If a database JSON file gets corrupted or has invalid formatting, delete the file; the application will automatically recreate and re-seed it with demo data upon next startup.
