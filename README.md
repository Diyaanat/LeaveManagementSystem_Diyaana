# LeavePortal: Hierarchical Leave Management System with ML Risk Engine

LeavePortal is a web application designed to optimize leave management. Unlike traditional systems that treat employees in isolation, LeavePortal maps company hierarchies, tracks task deadlines, and uses a **Scikit-Learn Random Forest Classifier** to assess operational coverage and deadline conflicts in real-time before manager approvals.

---

## Key Features

1.  **Unified Workspace & Role Hierarchy**: Employees and managers share the same login. Managers automatically get a "Leave Approval" tab based on reporting structures in the database.
2.  **AI Operational Risk Assessor**: An ensemble Random Forest model evaluates:
    *   *Available Staff coverage* (active direct reports not on approved leaves).
    *   *Proximity to task deadlines* (days until next task is due, ignoring overdue tasks in the past).
    *   *Seasonality* (peak seasonal workload launches in June, July, November, and December).
3.  **Interactive Calendar Grid**: Visualizes approved/pending leaves, task deadlines, and overlapping teammate leaves.
4.  **Subordinate Tasks & Progress Tracker**: Allows managers to monitor team task completions and project deliverables in real-time.
5.  **Dynamic Frontend Validations**: Real-time password criteria checklist and live business-days counter (omits Saturdays/Sundays).
6.  **Email Notification fallback logging**: Dispatches notifications on login, leave requests, and approvals. Writes HTML emails to `sent_emails.log` if SMTP is offline.
7.  **Adaptive Database Engine**: Standard connection to MySQL with seamless fallback to SQLite3 for zero-configuration local runs.

---

## Technology Stack

*   **Frontend**: HTML5, Vanilla CSS3 (custom CSS variables, glassmorphic layout), Vanilla JavaScript.
*   **Backend**: Python 3.x, Flask (routing and sessions), Flask-Bcrypt (password hashing).
*   **Database**: SQLite3 (local fallback), MySQL (production client connection).
*   **Machine Learning**: Scikit-Learn (`RandomForestClassifier`), NumPy, and Pandas.

---

## Directory Structure

*   `app.py`: Main Flask application, routes, and database routing logic.
*   `ml_engine.py`: Machine Learning Random Forest pipeline.
*   `mailer.py`: Email notifications utility with log-file fallback.
*   `database.sql`: Schema definition file.
*   `update_names.py`: Helper script to customize mock user names in the database.
*   `presentation_guide.md`: Slide-by-slide PowerPoint script and Q&A sheet for presentations.
*   `sent_emails.log`: Real-time logged HTML emails.
*   `Static/`: CSS styles and calendar/validator JavaScript helpers.
*   `templates/`: HTML Jinja2 templates (dashboard, request panel, security panel, and layout).

---

## Installation & Setup

1.  **Activate Environment**:
    Navigate to the project root directory and run the virtual environment:
    ```powershell
    venv\Scripts\activate
    ```
2.  **Run Server**:
    Start the Flask development server on port 5001:
    ```powershell
    python app.py
    ```
3.  **Access the Portal**:
    Open **[http://localhost:5001](http://localhost:5001)** in your web browser.

---

## Seeded Demonstration Accounts

The database is pre-seeded with these mock credentials for demonstration:

| Name | Work Email | Password | Role | Reports To |
| :--- | :--- | :--- | :--- | :--- |
| **Alice Smith** | `alice@company.com` | `password123` | Manager / Engineering Director | *None* |
| **Bob Jones** | `bob@company.com` | `password123` | Manager / Product Director | *None* |
| **Charlie Dev** | `charlie@company.com` | `password123` | Employee / Senior Developer | Alice Smith |
| **David Quality** | `david@company.com` | `password123` | Employee / QA Automation | Alice Smith |
| **Eve Design** | `eve@company.com` | `password123` | Employee / Lead UX Designer | Bob Jones |
| **Anjali Krishna** | `anjalikrish2006@gmail.com` | `password123` | Employee / QA Engineer | Alice Smith |
