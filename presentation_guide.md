# Presentation Guide: LeavePortal Leave Management System

Keep this guide open in VS Code during your presentation tomorrow. It outlines the directory structure, database tables, machine learning model details, and a step-by-step script for your live demonstration.

---

## 1. Directory Structure Walkthrough (Show in VS Code)

When walking through the codebase in VS Code, you can explain the files as follows:

*   **`app.py`** ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/app.py]): The main backend engine. Handles database connections (with automatic SQLite fallback), sessions, routing logic, leave application rules, and feeds data to the ML engine.
*   **`ml_engine.py`** ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/ml_engine.py]): The Machine Learning processor. Implements a Decision Tree classifier in pure Python without external dependencies, ensuring it runs on any system.
*   **`mailer.py`** ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/mailer.py]): The email notification engine. Attempts SMTP mail sending and falls back to writing formatted logs inside `sent_emails.log` in development.
*   **`database.sql`** ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/database.sql]): The database setup script defining tables, keys, and self-referencing hierarchy rules.
*   **`sent_emails.log`** ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/sent_emails.log]): A log file showing real-time email dispatches for actions like login, leave requests, and manager decisions.
*   **`Static/`**:
    *   `css/style.css` ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/Static/css/style.css]): Clean UI styled using modern Vanilla CSS custom properties, featuring glassmorphism, responsive columns, and transition effects.
    *   `js/script.js` ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/Static/js/script.js]): Handles interactive elements like the dynamic password strength checklist, automatic leave-length calculations (excluding weekends), task completion toggles, and drawing the month calendar.
*   **`templates/`**:
    *   `base.html` ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/templates/base.html]): The master layout featuring the unified sidebar.
    *   `login.html` & `Register.html`: Glassmorphic authentication screens.
    *   `home.html` ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/templates/home.html]): The core workspace dashboard housing the interactive calendar.
    *   `leaveRequest.html`: Form to request leaves and logs of personal leave history.
    *   `manager_dashboard.html` ([file:///c:/Users/diyaa/OneDrive/Desktop/LeaveManagementSystem_Diyaana/templates/manager_dashboard.html]): The manager portal containing direct report listings and cards representing pending approvals equipped with AI risk scoring metrics.
    *   `profile.html` & `account.html`: User profile sync and password reset views.

---

## 2. Database Schema & Tables

Explain that the system uses three interconnected tables to manage the organization:

### `users` Table
*   **Purpose**: Stores all users in the system.
*   **Key Fields**:
    *   `role`: Can be `'employee'` or `'manager'`. Both use the same login layout, but managers gain access to the "Leave Approval" tab.
    *   `manager_id`: A self-referencing foreign key linking to `users.id`. This represents the reporting chain (e.g., an employee reports to a manager, and a manager can report to a director).
    *   `total_leaves` & `leaves_taken`: Tracks individual leave balances.

### `leave_requests` Table
*   **Purpose**: Stores leave applications filed by employees.
*   **Key Fields**:
    *   `user_id`: Foreign key linking to the employee in the `users` table.
    *   `status`: Tracked as `'Pending'`, `'Approved'`, or `'Rejected'`.
    *   `remarks`: Stores the reason written by the manager if the leave is rejected.

### `tasks` Table
*   **Purpose**: Tracks individual projects, task items, and upcoming deadlines.
*   **Key Fields**:
    *   `user_id`: The assignee's ID. Used to check if they have critical task deadlines approaching while they are on leave.

---

## 3. How the Machine Learning Predictor Works

If asked **"How does the AI predict risk?"**, open `ml_engine.py` and explain these core components:

1.  **Decision Tree from Scratch**: We built a custom decision tree class (`DecisionTree`) using math entropy. This splits scenarios recursively to find the most clean decision boundary.
2.  **Staffing Coverage Risk**:
    *   *Features calculated*: Manager's total team size, number of overlapping approved leaves during the request period, the team's total pending tasks.
    *   *Logic*: If a large percentage of a manager's team is already on leave (high overlap ratio), the tree classifies this request as **High Staffing Risk**.
3.  **Task Deadline Collision Risk**:
    *   *Features calculated*: Number of days between the requested leave start date and the employee's nearest task deadline, whether it is a busy season, and the employee's active task count.
    *   *Logic*: If the start of a leave overlaps with or falls within 3 days of a critical task deadline, or if it overlaps with a busy season, the tree classifies it as **Critical/Risky**.
4.  **Actionable Recommendations**: Integrates these predictions to output a recommendation like *"Safe to Approve"* or *"Reject (High Risk of operation coverage or deadline collision)"*.

---

## 4. Live Demo Script (Step-by-Step Presentation)

Follow this sequence to deliver a perfect live demonstration:

### Step 1: Start the server and load the site
1.  Run the application in your terminal: `venv\Scripts\python.exe app.py`
2.  Open **[http://localhost:5001](http://localhost:5001)**.
3.  Show the glassmorphic login screen.

### Step 2: Show the Register Form & Live Password Strength
1.  Click **Create an account**.
2.  Start typing a password (e.g. `abc`). Show how the red checklist criteria remain greyed out.
3.  Type a strong password (e.g. `SecurePass@123`). Show the criteria turn green.
4.  Point out the **Reporting Manager** dropdown, which lists current managers loaded from the database.
5.  *Do not register a new user yet—go back to login to use the pre-seeded accounts.*

### Step 3: Login as Charlie (Employee)
1.  Login with: **Email**: `charlie@company.com` | **Password**: `password123`.
2.  **Dashboard Overview**:
    *   Show the metric cards: Allocation (24), Utilized (4), Remaining (20).
    *   Show the **Leave & Deadline Calendar**: Explain that Charlie can see his tasks, approved leaves, and teammate leaves.
    *   Show the **My Active Tasks** widget. Toggle a checkbox (e.g., click check on "Platform Migration"). Notice the text gets crossed out in real-time.
    *   Show the **Leave Statistics** doughnut chart.

### Step 4: Apply for Leave
1.  Click **Apply Leave** in the sidebar.
2.  Select **Sick Leave** or **Menstrual Leave**.
3.  Choose dates. Pick a Friday to next Monday (e.g. Friday to Monday).
4.  Point out the live calculation box showing: *"Total leave days: 2 business day(s) (excluding weekends)"*. This proves that Saturdays/Sundays do not deduct leaves.
5.  Type a reason and click **Submit Application**.
6.  Look at the history table below to see the new request logged as `Pending`.

### Step 5: Check Email Logs
1.  Open **`sent_emails.log`** in VS Code.
2.  Scroll to the bottom. Show the formatted HTML email alert notifying Charlie's manager (Alice Smith) that Charlie has requested leave.

### Step 6: Log out and log in as Alice (Manager)
1.  Click the power icon at the bottom of the sidebar.
2.  Log in with: **Email**: `alice@company.com` | **Password**: `password123`.
3.  Point out that Alice has an extra tab in her sidebar: **Leave Approval**.
4.  Click **Leave Approval**.
5.  Show the **Subordinate Roster** listing Charlie Dev and David Quality with their balances.
6.  Look at the **Pending Leave Applications** card:
    *   Show that Alice can see Charlie's request, reason, and his recent leave history.
    *   Highlight the **AI Staffing & Deadline Analyzer** panel. Point out the **Staffing Coverage Risk** and **Deadline Proximity Risk** scores computed by our Decision Tree, along with the recommendation.
7.  Click **Approve** or **Reject** (if Reject, type a remark e.g., *"Projects are understaffed"*).
8.  Show that the request disappears.
9.  Open `sent_emails.log` to prove that the employee received an email notifying them of their application update!
