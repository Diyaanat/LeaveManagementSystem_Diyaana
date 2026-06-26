# Presentation Guide: LeavePortal Leave Management System

Use this slide-by-slide outline and speaker notes script for your PowerPoint presentation tomorrow. Keep this file open in VS Code to reference while demonstrating the code.

---

## Slide 1: Title Slide
*   **Slide Title**: LeavePortal: A Hierarchical Leave Management System with ML Risk Assessment
*   **Subtitle**: Industry-Standard Random Forest Integration for Operations Coverage & Task Collision Risk
*   **Presenter**: [Your Name]
*   **Speaker Notes**:
    > "Hello everyone and [Mentor Name]. Today, I will be demonstrating LeavePortal, a web application designed to optimize how companies approve and manage employee leave. Unlike traditional systems that look at employees in isolation, LeavePortal maps organizational hierarchies and uses a Scikit-Learn Random Forest Classifier to assess team coverage and task deadline conflicts in real-time."

---

## Slide 2: The Problem Statement (Why this should exist)
*   **Key Points**:
    *   *Siloed Leave Approvals*: Standard portals let managers approve leaves without seeing overlaps with active teammate leaves or approaching deadlines.
    *   *Operational Understaffing*: A manager might approve a leave only to discover later that the team is understaffed (e.g. 2 out of 3 developers off).
    *   *Missed Deadlines*: Leaves approved close to critical project/task deadlines lead to missed delivery milestones.
    *   *Separated Logins*: Managers and employees are often forced into separate systems or roles, causing friction.
*   **Speaker Notes**:
    > "The core issue with current leave portals is that they treat leave requests as isolated events. In reality, an employee's absence impacts the whole team. LeavePortal solves this by linking leave requests with team availability and task deadlines, and uses machine learning to alert managers of potential operational understaffing or project delays *before* they approve the request."

---

## Slide 3: The Technology Stack
*   **Frontend**:
    *   HTML5 (semantic structuring)
    *   Vanilla CSS3 (designed with a custom HSL property system and modern glassmorphic layouts)
    *   Vanilla JavaScript (handling password checkers, asynchronous tasks, and calendar rendering)
*   **Backend & DB**:
    *   Python 3.x & Flask (routing, session state management)
    *   Flask-Bcrypt (secure password hashing)
    *   SQLite3 (local relational database used for zero-dependency development and seeding)
    *   MySQL Client (production-ready database connector)
*   **Machine Learning**:
    *   Scikit-Learn (`RandomForestClassifier`)
    *   NumPy & Pandas (data structures and manipulation)
*   **Speaker Notes**:
    > "For the tech stack, we went with a lightweight Python/Flask backend and a clean, responsive glassmorphic frontend built in Vanilla CSS and JavaScript. For the intelligence layer, we installed Scikit-Learn, NumPy, and Pandas to run an ensemble Random Forest model directly in our backend. We also implemented a database wrapper that uses MySQL, but seamlessly falls back to local SQLite if MySQL is offline."

---

## Slide 4: Database Schema & Relationships (Show tables)
*   **The 3 Connected Tables**:
    *   `users`: Tracks names, logins, roles, and a self-referencing `manager_id`.
    *   `leave_requests`: Stores applied leave categories, start/end dates, reason, status (Pending/Approved/Rejected), and manager remarks.
    *   `tasks`: Tracks projects, task descriptions, deadlines, and assignees.
*   **Visual Relationship Diagram (Mermaid)**:
    ```
    +------------------+         +--------------------+
    |      users       |1       *|   leave_requests   |
    |------------------|<--------|--------------------|
    | id (PK)          |         | id (PK)            |
    | name             |         | user_id (FK)       |
    | email            |         | start_date         |
    | manager_id (FK)  |--+      | end_date           |
    +------------------+  |      | status             |
      ^                   |      +--------------------+
      |                   |
      +-------------------+      +--------------------+
      1                 *        |       tasks        |
                                 |--------------------|
                                 | id (PK)            |
                                 | user_id (FK)       |
                                 | deadline           |
                                 +--------------------+
    ```
*   **Speaker Notes**:
    > "Here is our database architecture. We have three main tables. The key to our organizational hierarchy is the `manager_id` inside the `users` table, which points back to the `id` of another user. This establishes a reporting structure where managers can view leaves for only their direct reports. `leave_requests` and `tasks` both reference the `users` table via foreign keys."

---

## Slide 5: Core Features
*   **Slide Bullet Points**:
    *   **Unified Workspace**: Single login portal for everyone. Managers automatically get a "Leave Approval" tab based on database roles.
    *   **Interactive Month Calendar**: Shows personal leaves, teammate leaves, and task deadlines in a single visual grid.
    *   **Real-Time Forms**: Live password criteria validator, live leave duration calculator (skips weekends automatically).
    *   **Development Mail Logger**: Writes rich HTML emails to a local `sent_emails.log` file on actions like registration, login, and approvals.
    *   **Subordinate Tasks & Progress Tracker**: Let's managers monitor active workloads and deadlines of direct reports in real-time.
*   **Speaker Notes**:
    > "LeavePortal offers a unified workspace. Employees can apply for leave, monitor their task deadlines, check their teammates' leaves on an interactive calendar, and track their password strength. Managers can monitor their direct reports' leave history and view a real-time 'Subordinate Tasks & Progress Tracker' to see exactly what deliverables are currently active across their team."

---

## Slide 6: The Machine Learning Engine (How it works under the hood)
*   **Model**: Scikit-Learn `RandomForestClassifier` (100 estimators, max depth 5).
*   **Input Features**:
    1.  `available_staff`: Number of teammates (direct reports) active during the requested leave window.
    2.  `days_to_deadline`: Number of days from the leave start date to the employee's nearest task deadline.
    3.  `season`: Workload intensity flag ($0$: Off-peak, $1$: Peak project release seasons in June, July, November, and December).
*   **Output**: Risk Level (`Low`, `Medium`, or `High`) and the model's prediction **Confidence %** (using `predict_proba()`).
*   **Speaker Notes**:
    > "Our ML engine is a Random Forest Classifier. A Random Forest builds 100 separate decision trees on random subsets of the data and takes the majority vote. When a manager opens a request, our backend dynamically calculates: how many other team members are available, how many days Charlie has until his nearest task is due, and if it is a busy release season. The model outputs a predicted risk category and our confidence percentage."

---

## Slide 7: Training Data & Prototype Status
*   **Training Data Source**:
    *   Synthetically generated dataset ($1,000$ historical request rows).
    *   Maps company rules (e.g. leaving during a busy season with tasks due in under 7 days is labeled High Risk).
*   **Prototype Status ("Training Mode")**:
    *   Currently in **Prototype & Training Mode**.
    *   We use simulated business parameters to train the model on startup.
    *   *Why?* To demonstrate the complete functionality and math without requiring months of historical company records.
*   **Speaker Notes**:
    > "It is important to note that the system is currently in a prototype and training phase. The model is trained on startup using 1,000 synthetically generated historical request entries representing logical company scenarios. As a prototype, it demonstrates the machine learning pipeline from database queries to model classification, but is designed to switch to real company history once deployed."

---

## Slide 8: Setbacks Faced & Edge Cases Handled
*   **Setbacks Faced**:
    *   *Windows Port 5000 Conflict*: Port 5000 is occupied by system services on Windows 11. Shifting the app to port 5001 and binding to `0.0.0.0` resolved connection issues.
    *   *Local SQLite Fallback*: Created a custom database manager class to automatically handle SQL syntax differences between SQLite and MySQL so the app runs immediately.
    *   *Calendar Timezone Shifts*: JavaScript's `new Date("YYYY-MM-DD")` parses dates as UTC, causing event boxes to shift back by one day in local timezones. We solved this by writing a custom local date string parser.
    *   *Overdue Task Collision Bug*: Fixed a bug where tasks with deadlines in the past (overdue tasks) caused all future leave requests to evaluate to a `0-day deadline` and flag as High Risk. We rewrote the backend to ignore tasks due in the past.
*   **Edge Cases Handled**:
    *   Omit Saturdays and Sundays from leave deductions.
    *   Block overlaps with already approved leaves.
    *   Block past dates in the leave form.
*   **Speaker Notes**:
    > "During development, we overcame several technical setbacks. Windows 11 often blocks port 5000, so we moved to port 5001. We also resolved a bug where calendar event dates shifted back one day in local timezones due to UTC date parsing. The current drawbacks are that we use synthetic data for training and have a basic task tracker rather than external integrations."

---

## Slide 9: Project Drawbacks & Future Work
*   **Drawbacks**:
    *   *Cold Start*: Requires bootstrapping before real company history is collected.
    *   *Isolated Tasks*: Tasks are created inside the portal rather than syncing with external systems.
*   **Future Features**:
    *   *API Integrations*: Sync tasks and deadlines directly with JIRA, GitHub, or Trello.
    *   *Vacation Forecasting*: Add a time-series forecasting model to predict department leave trends.
    *   *SMTP Gateway*: Hook up real email servers (e.g. SendGrid or Amazon SES) for real email delivery.
*   **Speaker Notes**:
    > "Current drawbacks include relying on synthetic data for initial training and having a simple, local task manager. In the future, we plan to sync tasks directly with JIRA and GitHub APIs, integrate forecasting models to predict vacation spikes, and configure SMTP servers like SendGrid to deliver real email notifications."

---

## Slide 10: My Contribution
*   **Slide Bullet Points**:
    *   Designed the unified, mobile-responsive glassmorphic sidebar layout.
    *   Added a **Subordinate Tasks & Progress Tracker** card to let managers monitor team task completions in real-time.
    *   Migrated the intelligence layer to Scikit-Learn's Random Forest classifier.
    *   Wrote the database wrapper class supporting MySQL and SQLite fallback.
    *   Implemented the local email logging fallback for offline dev audit.
*   **Speaker Notes**:
    > "My key contributions were designing the unified workspace frontend, implementing the Scikit-Learn Random Forest pipeline, setting up the adaptive database engine, adding the team task tracker card for managers, and writing the local email logging fallback."

---

## Slide 11: Mentorship Q&A Cheat Sheet (Preparation for Questions)
*   **Q: Why choose Random Forest over a single Decision Tree?**
    *   *A*: A single decision tree suffers from high variance and can easily overfit the training data. Random Forest averages the predictions of 100 trees, reducing variance and yielding a more stable, robust model.
*   **Q: How does the model predict risk when there isn't real company history?**
    *   *A*: We generate 1,000 mock evaluations in-memory on startup to train the classifier. The model learns these simulated patterns. Once deployed, the training code can be switched to load actual historical approvals.
*   **Q: What happens to registered employees if the server restarts?**
    *   *A*: They are saved persistently inside the local SQLite database file `leave_system.db`. Only the first launch seeds the database; subsequent restarts preserve all registered users, tasks, and leave histories.
*   **Q: How do you show the database tables in VS Code?**
    *   *A*: Install the **SQLite Viewer** extension in VS Code. Simply double-click `leave_system.db` in your explorer to view the tables as spreadsheets.
