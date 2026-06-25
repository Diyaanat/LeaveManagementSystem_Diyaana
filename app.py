import os
import re
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

# Import custom utilities
from ml_engine import predictor
from mailer import send_email

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'diyaana_secret_system_key'

# MySQL Configuration (configured via environment variables or fallbacks)
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', '127.0.0.1')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'password123')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'leave_system_db')

# ----------------- ADAPTIVE DATABASE ENGINE -----------------
import sqlite3
import MySQLdb

class DatabaseEngine:
    def __init__(self, app):
        self.use_sqlite = False
        self.sqlite_db_path = os.path.join(app.root_path, 'leave_system.db')
        self.mysql = None
        
        # Try establishing MySQL connection
        try:
            conn = MySQLdb.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                passwd=app.config['MYSQL_PASSWORD'],
                db=app.config['MYSQL_DB'],
                connect_timeout=2
            )
            conn.close()
            self.mysql = MySQL(app)
            print("[DATABASE] MySQL connection verified. Using MySQL.")
        except Exception as e:
            print(f"[DATABASE WARNING] MySQL connection failed ({e}). Falling back to SQLite.")
            self.use_sqlite = True
            self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect(self.sqlite_db_path)
        cursor = conn.cursor()
        
        # Read and run schema script
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.sql')
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
            conn.commit()
            
        # Seed test data if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            self._seed_sqlite(cursor, conn)
            
        cursor.close()
        conn.close()

    def _seed_sqlite(self, cursor, conn):
        print("[DATABASE] Seeding SQLite database with default employees, managers, tasks...")
        hashed_pw = bcrypt.generate_password_hash("password123").decode('utf-8')
        
        # Managers
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, gender, position, total_leaves, leaves_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Alice Smith", "alice@company.com", "alice", hashed_pw, "manager", "Female", "Engineering Director", 24, 0)
        )
        alice_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, gender, position, total_leaves, leaves_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Bob Jones", "bob@company.com", "bob", hashed_pw, "manager", "Male", "Product Director", 24, 0)
        )
        bob_id = cursor.lastrowid
        
        # Employees (under Alice)
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, gender, position, manager_id, total_leaves, leaves_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Charlie Dev", "charlie@company.com", "charlie", hashed_pw, "employee", "Male", "Senior Backend Developer", alice_id, 24, 4)
        )
        charlie_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, gender, position, manager_id, total_leaves, leaves_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("David Quality", "david@company.com", "david", hashed_pw, "employee", "Male", "QA Automation Engineer", alice_id, 24, 0)
        )
        david_id = cursor.lastrowid
        
        # Employee (under Bob)
        cursor.execute(
            "INSERT INTO users (name, email, username, password, role, gender, position, manager_id, total_leaves, leaves_taken) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("Eve Design", "eve@company.com", "eve", hashed_pw, "employee", "Female", "Lead UI/UX Designer", bob_id, 24, 2)
        )
        eve_id = cursor.lastrowid
        
        # Tasks & Deadlines
        tasks = [
            (charlie_id, "Platform Migration", "Database schema upgrade & index optimizations", "2026-07-02", "Pending"),
            (charlie_id, "Leave Analytics", "Build predictive model scoring endpoints", "2026-06-29", "In Progress"),
            (david_id, "Security Suite", "Implement dynamic JWT validations & audit trails", "2026-07-05", "Pending"),
            (eve_id, "UI Redesign", "Draft high-fidelity mockups for glassmorphism screens", "2026-06-30", "Completed")
        ]
        for t in tasks:
            cursor.execute("INSERT INTO tasks (user_id, project_name, task_name, deadline, status) VALUES (?, ?, ?, ?, ?)", t)
            
        # Leave history
        leaves = [
            (charlie_id, "Casual", "2026-06-15", "2026-06-18", "Annual family trip out-of-state", "Approved", "Enjoy your time off!"),
            (eve_id, "Sick", "2026-06-22", "2026-06-23", "Severe migraine and fever", "Approved", "Take rest, recover well."),
            (charlie_id, "Sick", "2026-06-29", "2026-06-30", "Dental wisdom tooth extraction", "Pending", None)
        ]
        for l in leaves:
            cursor.execute("INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status, remarks) VALUES (?, ?, ?, ?, ?, ?, ?)", l)
            
        conn.commit()

    def execute(self, query, params=None, fetch='all', commit=False):
        if params is None:
            params = []
            
        if self.use_sqlite:
            # Adapt query formatting from %s to ? for SQLite
            sqlite_query = query.replace('%s', '?')
            conn = sqlite3.connect(self.sqlite_db_path)
            cursor = conn.cursor()
            try:
                cursor.execute(sqlite_query, params)
                if commit:
                    conn.commit()
                    return cursor.lastrowid
                else:
                    if fetch == 'one':
                        row = cursor.fetchone()
                        return tuple(row) if row else None
                    else:
                        rows = cursor.fetchall()
                        return [tuple(r) for r in rows] if rows else []
            except Exception as e:
                print(f"[SQLITE ERROR] Query: {sqlite_query} | Error: {e}")
                raise e
            finally:
                cursor.close()
                conn.close()
        else:
            # MySQL engine
            cursor = self.mysql.connection.cursor()
            try:
                cursor.execute(query, params)
                if commit:
                    self.mysql.connection.commit()
                    return cursor.lastrowid
                else:
                    if fetch == 'one':
                        return cursor.fetchone()
                    else:
                        return cursor.fetchall()
            except Exception as e:
                print(f"[MYSQL ERROR] Query: {query} | Error: {e}")
                raise e
            finally:
                cursor.close()

db = DatabaseEngine(app)

# Helper function to check password strength
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[_@$!%*#?&]", password):
        return False
    return True

# Helper to format and send registration email
def send_registration_email(name, email, role):
    subject = "Welcome to LeavePortal - Registration Successful!"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc; border-radius: 12px; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0;">
        <h2 style="color: #4f46e5; margin-bottom: 20px;">Welcome to LeavePortal, {name}!</h2>
        <p style="color: #334155; font-size: 16px; line-height: 1.5;">Your account has been successfully registered on the Employee Leave Management System.</p>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; color: #475569;"><strong>Email/Login ID:</strong> {email}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Designated Role:</strong> {role.capitalize()}</p>
        </div>
        <p style="color: #334155; font-size: 14px;">You can now log in to request leaves, track task deadlines, and view the team calendar.</p>
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
        <p style="font-size: 12px; color: #94a3b8; text-align: center;">This is an automated notification. Please do not reply directly to this email.</p>
    </div>
    """
    send_email(email, subject, html)

# Helper to format and send login alert email
def send_login_email(name, email):
    subject = "Security Alert: New Sign-in Detected"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc; border-radius: 12px; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0;">
        <h3 style="color: #4f46e5; margin-bottom: 20px;">Hello, {name}</h3>
        <p style="color: #334155; font-size: 15px;">A new sign-in was detected for your LeavePortal account.</p>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; color: #475569;"><strong>Account Email:</strong> {email}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Sign-in Time:</strong> {now_str} (Server Local Time)</p>
        </div>
        <p style="color: #64748b; font-size: 13px;">If this was you, no action is required. If you did not initiate this login, please change your password immediately in your account portal.</p>
    </div>
    """
    send_email(email, subject, html)

# Helper to format and send leave application notification to manager
def send_leave_requested_email(employee_name, leave_type, start_date, end_date, reason, manager_email, manager_name):
    subject = f"New Leave Application: {employee_name} ({leave_type})"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc; border-radius: 12px; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0;">
        <h3 style="color: #4f46e5; margin-bottom: 15px;">Leave Approval Request</h3>
        <p style="color: #334155; font-size: 15px;">Hello {manager_name},</p>
        <p style="color: #334155; font-size: 15px;">An employee reporting to you, <strong>{employee_name}</strong>, has requested leave. Please review the details below:</p>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; color: #475569;"><strong>Leave Type:</strong> {leave_type}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Duration:</strong> {start_date} to {end_date}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Reason:</strong> {reason}</p>
        </div>
        <p style="color: #334155; font-size: 14px;">Log in to the manager dashboard to view the team staffing risk, check deadline collisions, and approve/reject the request.</p>
    </div>
    """
    send_email(manager_email, subject, html)

# Helper to format and send approval/rejection updates to employee
def send_leave_status_email(employee_name, employee_email, leave_type, start_date, end_date, status, remarks, manager_name):
    subject = f"Leave Request Update: {status}"
    color = "#10b981" if status == 'Approved' else "#f43f5e"
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc; border-radius: 12px; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0;">
        <h3 style="color: {color}; margin-bottom: 15px;">Leave Application {status}</h3>
        <p style="color: #334155; font-size: 15px;">Hello {employee_name},</p>
        <p style="color: #334155; font-size: 15px;">Your manager, <strong>{manager_name}</strong>, has processed your leave request.</p>
        <div style="background-color: #ffffff; padding: 15px; border-radius: 8px; margin: 20px 0; border: 1px solid #e2e8f0;">
            <p style="margin: 5px 0; color: #475569;"><strong>Leave Type:</strong> {leave_type}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Duration:</strong> {start_date} to {end_date}</p>
            <p style="margin: 5px 0; color: #475569;"><strong>Status:</strong> <span style="color: {color}; font-weight: bold;">{status}</span></p>
            {f'<p style="margin: 5px 0; color: #475569;"><strong>Manager Remarks:</strong> {remarks}</p>' if remarks else ''}
        </div>
        <p style="color: #64748b; font-size: 13px;">If you have any questions, please contact your reporting manager.</p>
    </div>
    """
    send_email(employee_email, subject, html)

# Helper to send password reset email
def send_password_change_email(name, email):
    subject = "Security Alert: Password Changed"
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px; background-color: #f8fafc; border-radius: 12px; max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0;">
        <h3 style="color: #f43f5e; margin-bottom: 20px;">Password Changed Alert</h3>
        <p style="color: #334155; font-size: 15px;">Hello {name},</p>
        <p style="color: #334155; font-size: 15px;">The password for your LeavePortal account was changed on <strong>{now_str}</strong>.</p>
        <p style="color: #475569; font-size: 14px;">If you made this change, you can safely ignore this mail. If you did not make this change, please contact your administrator or reset your password immediately to secure your account.</p>
    </div>
    """
    send_email(email, subject, html)


# ----------------- AUTHENTICATION ROUTES -----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    # If request is GET, fetch managers for dropdown
    if request.method == 'GET':
        managers = db.execute("SELECT id, name, position FROM users WHERE role = 'manager'")
        return render_template('Register.html', managers=managers)
        
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        gender = request.form['gender']
        role = request.form.get('role', 'employee') # Default to employee
        position = request.form.get('position', 'Software Engineer')
        manager_id = request.form.get('manager_id')
        
        # Convert manager_id to integer or None
        try:
            manager_id = int(manager_id) if manager_id and manager_id != "" else None
        except ValueError:
            manager_id = None
            
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
            
        if not is_strong_password(password):
            flash('Password must contain at least 8 characters, including uppercase, lowercase, numeric, and special character symbols.', 'danger')
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            # Check if email or username already exists
            dup = db.execute("SELECT id FROM users WHERE email = %s OR username = %s", [email, username], fetch='one')
            if dup:
                flash('Email or Username already exists.', 'danger')
                return redirect(url_for('register'))
                
            # Default leaf balance parameters
            total_leaves = 24
            
            db.execute(
                "INSERT INTO users (name, email, username, password, role, gender, position, manager_id, total_leaves, leaves_taken) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                [name, email, username, hashed_password, role, gender, position, manager_id, total_leaves, 0],
                commit=True
            )
            
            # Send notification email
            send_registration_email(name, email, role)
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred during registration: {e}', 'danger')
            return redirect(url_for('register'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.execute("SELECT id, name, email, username, password, role, gender FROM users WHERE email = %s", [email], fetch='one')
        
        if user and bcrypt.check_password_hash(user[4], password):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            session['user_role'] = user[5]
            session['gender'] = user[6]
            
            # Check if this user is a manager (meaning they have direct reports)
            subordinates = db.execute("SELECT COUNT(*) FROM users WHERE manager_id = %s", [user[0]], fetch='one')
            session['is_manager_of_team'] = subordinates[0] > 0 or user[5] == 'manager'
            
            # Send login alert email
            send_login_email(user[1], user[2])
            
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')


# ----------------- HOME / CALENDAR / TASKS -----------------

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    
    # 1. Add Task Form Handler
    if request.method == 'POST' and 'task_name' in request.form:
        project_name = request.form['project_name']
        task_name = request.form['task_name']
        deadline = request.form['deadline']
        db.execute(
            "INSERT INTO tasks (user_id, project_name, task_name, deadline, status) VALUES (%s, %s, %s, %s, %s)",
            [uid, project_name, task_name, deadline, "Pending"],
            commit=True
        )
        flash('Task deadline added successfully!', 'success')
        return redirect(url_for('home'))
        
    # 2. Fetch Dashboard Metrics
    balances = db.execute("SELECT total_leaves, leaves_taken FROM users WHERE id = %s", [uid], fetch='one')
    total = balances[0] if balances else 24
    taken = balances[1] if balances else 0
    remaining = total - taken
    
    # 3. Fetch Tasks
    tasks = db.execute("SELECT id, project_name, task_name, deadline, status FROM tasks WHERE user_id = %s ORDER BY deadline ASC", [uid])
    
    # 4. Recent status updates/notifications (last 5)
    notifications = db.execute(
        "SELECT leave_type, start_date, end_date, status, remarks FROM leave_requests WHERE user_id = %s ORDER BY id DESC LIMIT 5",
        [uid]
    )
    
    # 5. Fetch calendar events (approved and pending leaves, and tasks)
    # Get user and their manager to fetch relevant calendar events
    user_info = db.execute("SELECT manager_id, role FROM users WHERE id = %s", [uid], fetch='one')
    manager_id = user_info[0] if user_info else None
    
    # For employee, show: their leaves, their tasks, and overlapping approved leaves of colleagues
    # For manager, show: their leaves, their tasks, and approved leaves of subordinates
    calendar_events = []
    
    # My leaves
    my_leaves = db.execute("SELECT leave_type, start_date, end_date, status FROM leave_requests WHERE user_id = %s", [uid])
    for l in my_leaves:
        calendar_events.append({
            'title': f"{l[0]} Leave ({l[3]})",
            'start': l[1] if isinstance(l[1], str) else l[1].strftime('%Y-%m-%d'),
            'end': l[2] if isinstance(l[2], str) else l[2].strftime('%Y-%m-%d'),
            'type': 'leave',
            'status': l[3]
        })
        
    # My tasks
    for t in tasks:
        calendar_events.append({
            'title': f"Task: {t[1]} - {t[2]}",
            'start': t[3] if isinstance(t[3], str) else t[3].strftime('%Y-%m-%d'),
            'end': t[3] if isinstance(t[3], str) else t[3].strftime('%Y-%m-%d'),
            'type': 'task',
            'status': t[4]
        })
        
    # Colleagues/Subordinates approved leaves
    if session['is_manager_of_team']:
        # Show approved leaves of direct reports
        team_leaves = db.execute(
            "SELECT u.name, l.leave_type, l.start_date, l.end_date FROM leave_requests l JOIN users u ON l.user_id = u.id WHERE u.manager_id = %s AND l.status = 'Approved'",
            [uid]
        )
        for l in team_leaves:
            calendar_events.append({
                'title': f"{l[0]}: {l[1]} (Approved)",
                'start': l[2] if isinstance(l[2], str) else l[2].strftime('%Y-%m-%d'),
                'end': l[3] if isinstance(l[3], str) else l[3].strftime('%Y-%m-%d'),
                'type': 'team-leave',
                'status': 'Approved'
            })
    elif manager_id:
        # Show approved leaves of teammates reporting to the same manager
        colleague_leaves = db.execute(
            "SELECT u.name, l.leave_type, l.start_date, l.end_date FROM leave_requests l JOIN users u ON l.user_id = u.id WHERE u.manager_id = %s AND u.id != %s AND l.status = 'Approved'",
            [manager_id, uid]
        )
        for l in colleague_leaves:
            calendar_events.append({
                'title': f"Teammate {l[0]}: {l[1]}",
                'start': l[2] if isinstance(l[2], str) else l[2].strftime('%Y-%m-%d'),
                'end': l[3] if isinstance(l[3], str) else l[3].strftime('%Y-%m-%d'),
                'type': 'team-leave',
                'status': 'Approved'
            })

    # Prepare chart data for dashboard breakdown
    approved_cnt = db.execute("SELECT COUNT(*) FROM leave_requests WHERE user_id = %s AND status = 'Approved'", [uid], fetch='one')[0]
    pending_cnt = db.execute("SELECT COUNT(*) FROM leave_requests WHERE user_id = %s AND status = 'Pending'", [uid], fetch='one')[0]
    rejected_cnt = db.execute("SELECT COUNT(*) FROM leave_requests WHERE user_id = %s AND status = 'Rejected'", [uid], fetch='one')[0]
    
    chart_data = {
        'approved': approved_cnt,
        'pending': pending_cnt,
        'rejected': rejected_cnt
    }

    return render_template('home.html', 
                           total_leaves=total, 
                           leaves_taken=taken, 
                           remaining_leaves=remaining, 
                           tasks=tasks, 
                           notifications=notifications, 
                           calendar_events=calendar_events,
                           chart_data=chart_data)

# Route to toggle task status
@app.route('/task/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    current_status = db.execute("SELECT status FROM tasks WHERE id = %s AND user_id = %s", [task_id, session['user_id']], fetch='one')
    if current_status:
        new_status = "Completed" if current_status[0] == "Pending" or current_status[0] == "In Progress" else "Pending"
        db.execute("UPDATE tasks SET status = %s WHERE id = %s", [new_status, task_id], commit=True)
        return jsonify({'success': True, 'new_status': new_status})
    return jsonify({'success': False, 'message': 'Task not found'}), 404


# ----------------- LEAVE REQUESTS & VALIDATION -----------------

@app.route('/leave', methods=['GET', 'POST'])
@app.route('/leave/request', methods=['GET', 'POST'])
def leave_request():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    
    if request.method == 'POST':
        leave_type = request.form['leave_type']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        reason = request.form['reason']
        
        # Validations
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            today = date.today()
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'danger')
            return redirect(url_for('leave_request'))
            
        if start_date < today:
            flash('Start date cannot be in the past!', 'danger')
            return redirect(url_for('leave_request'))
            
        if end_date < start_date:
            flash('End date cannot be prior to start date!', 'danger')
            return redirect(url_for('leave_request'))
            
        # Omit weekends (Saturdays and Sundays)
        curr_dt = start_date
        requested_days = 0
        while curr_dt <= end_date:
            if curr_dt.weekday() < 5:  # 0: Monday to 4: Friday
                requested_days += 1
            curr_dt += timedelta(days=1)
            
        if requested_days == 0:
            flash('Requested dates fall entirely on weekend holidays (Saturday/Sunday). No leaves deducted.', 'warning')
            return redirect(url_for('leave_request'))
            
        # Check overlaps with ALREADY approved leave requests
        # Note: overlapping query checking dates: NOT (lr.end_date < start or lr.start_date > end)
        overlap = db.execute(
            "SELECT id FROM leave_requests WHERE user_id = %s AND status = 'Approved' AND NOT (end_date < %s OR start_date > %s)",
            [uid, start_date_str, end_date_str],
            fetch='one'
        )
        if overlap:
            flash('Date overlap conflict! You have an approved leave request that clashes with these dates.', 'danger')
            return redirect(url_for('leave_request'))
            
        # Check balance
        balances = db.execute("SELECT total_leaves, leaves_taken FROM users WHERE id = %s", [uid], fetch='one')
        total = balances[0] if balances else 24
        taken = balances[1] if balances else 0
        remaining = total - taken
        
        if requested_days > remaining:
            flash(f'Insufficient leave balance! Requested: {requested_days} days. Remaining available: {remaining} days.', 'danger')
            return redirect(url_for('leave_request'))
            
        # Insert request
        db.execute(
            "INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status) VALUES (%s, %s, %s, %s, %s, %s)",
            [uid, leave_type, start_date_str, end_date_str, reason, 'Pending'],
            commit=True
        )
        
        # Send Email to Manager
        user_info = db.execute("SELECT name, manager_id FROM users WHERE id = %s", [uid], fetch='one')
        if user_info and user_info[1]:
            manager = db.execute("SELECT name, email FROM users WHERE id = %s", [user_info[1]], fetch='one')
            if manager:
                send_leave_requested_email(
                    employee_name=user_info[0],
                    leave_type=leave_type,
                    start_date=start_date_str,
                    end_date=end_date_str,
                    reason=reason,
                    manager_email=manager[1],
                    manager_name=manager[0]
                )
                
        flash(f'Leave request submitted successfully for {requested_days} business day(s) (weekends excluded). Pending approval.', 'success')
        return redirect(url_for('leave_request'))
        
    # GET Request: Fetch history and current balance
    balances = db.execute("SELECT total_leaves, leaves_taken FROM users WHERE id = %s", [uid], fetch='one')
    total = balances[0] if balances else 24
    taken = balances[1] if balances else 0
    remaining = total - taken
    
    history = db.execute(
        "SELECT id, leave_type, start_date, end_date, reason, status, remarks FROM leave_requests WHERE user_id = %s ORDER BY id DESC",
        [uid]
    )
    
    return render_template('leaveRequest.html', total_leaves=total, leaves_taken=taken, remaining_leaves=remaining, history=history)

# Cancel pending or approved leave request
@app.route('/leave/cancel/<int:leave_id>', methods=['POST'])
def cancel_leave(leave_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    leave = db.execute("SELECT user_id, start_date, end_date, status FROM leave_requests WHERE id = %s AND user_id = %s", [leave_id, uid], fetch='one')
    
    if leave:
        leave_uid, start_date, end_date, status = leave
        
        # If approved, we must restore the leave balance!
        if status == 'Approved':
            # Parse dates
            if isinstance(start_date, str):
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                start = start_date
                end = end_date
                
            # Count week days
            curr_dt = start
            days = 0
            while curr_dt <= end:
                if curr_dt.weekday() < 5:
                    days += 1
                curr_dt += timedelta(days=1)
                
            # Restore balance
            db.execute("UPDATE users SET leaves_taken = leaves_taken - %s WHERE id = %s", [days, uid], commit=True)
            
        # Delete or set cancelled
        db.execute("DELETE FROM leave_requests WHERE id = %s", [leave_id], commit=True)
        flash('Leave request cancelled successfully. Leave balance restored.', 'success')
    else:
        flash('Leave request not found or unauthorized.', 'danger')
        
    return redirect(url_for('leave_request'))


# ----------------- MANAGER PORTAL & APPROVALS (ML DRIVEN) -----------------

@app.route('/leave/manage', methods=['GET', 'POST'])
def manage_leaves():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    
    # Verify manager check
    subordinates_count = db.execute("SELECT COUNT(*) FROM users WHERE manager_id = %s", [uid], fetch='one')[0]
    if subordinates_count == 0 and session.get('user_role') != 'manager':
        flash('Unauthorized Access Window. Managers only.', 'danger')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        req_id = request.form['req_id']
        action = request.form['action']  # 'Approved' or 'Rejected'
        remarks = request.form.get('remarks', '')
        
        # Fetch request details
        req = db.execute(
            "SELECT lr.user_id, lr.leave_type, lr.start_date, lr.end_date, u.name, u.email "
            "FROM leave_requests lr JOIN users u ON lr.user_id = u.id WHERE lr.id = %s",
            [req_id], fetch='one'
        )
        
        if req:
            u_id, leave_type, start_date, end_date, emp_name, emp_email = req
            
            # If approved, deduct leave balance
            if action == 'Approved':
                # Convert dates
                if isinstance(start_date, str):
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                else:
                    start = start_date
                    end = end_date
                    
                # Calculate business days
                curr_dt = start
                days = 0
                while curr_dt <= end:
                    if curr_dt.weekday() < 5:
                        days += 1
                    curr_dt += timedelta(days=1)
                    
                # Deduct balance
                db.execute("UPDATE users SET leaves_taken = leaves_taken + %s WHERE id = %s", [days, u_id], commit=True)
                
            # Update request status
            db.execute("UPDATE leave_requests SET status = %s, remarks = %s WHERE id = %s", [action, remarks, req_id], commit=True)
            
            # Send Notification Email to Employee
            mgr_name = session['user_name']
            send_leave_status_email(emp_name, emp_email, leave_type, str(start_date), str(end_date), action, remarks, mgr_name)
            
            flash(f"Leave request #{req_id} successfully {action}.", 'success')
            
        return redirect(url_for('manage_leaves'))
        
    # GET request
    # 1. Fetch direct subordinates list (Roster)
    roster = db.execute(
        "SELECT id, name, email, position, total_leaves, leaves_taken, (total_leaves - leaves_taken) as remaining "
        "FROM users WHERE manager_id = %s ORDER BY name ASC",
        [uid]
    )
    
    # 2. Fetch pending requests
    pending_list = db.execute(
        "SELECT lr.id, u.name, lr.leave_type, lr.start_date, lr.end_date, lr.reason, lr.user_id "
        "FROM leave_requests lr JOIN users u ON lr.user_id = u.id "
        "WHERE u.manager_id = %s AND lr.status = 'Pending' ORDER BY lr.start_date ASC",
        [uid]
    )
    
    # 3. Enrich pending requests with Subordinate's Leave History AND Machine Learning Risk Prediction
    enriched_pendings = []
    for r in pending_list:
        req_id, emp_name, leave_type, start_date, end_date, reason, emp_id = r
        
        # Convert date representations
        if isinstance(start_date, str):
            start_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            start_dt = start_date
            end_dt = end_date
            
        # Get historical leaves (approved) for employee
        emp_history = db.execute(
            "SELECT leave_type, start_date, end_date, status FROM leave_requests WHERE user_id = %s AND id != %s ORDER BY id DESC LIMIT 5",
            [emp_id, req_id]
        )
        
        # ML Parameters computation
        # Team Size
        team_size = len(roster)
        
        # Overlapping Leaves (number of other approved leaves reporting to the same manager overlapping)
        # Dates overlap condition: NOT (lr.end_date < start or lr.start_date > end)
        overlap_info = db.execute(
            "SELECT COUNT(DISTINCT lr.user_id) FROM leave_requests lr JOIN users u ON lr.user_id = u.id "
            "WHERE u.manager_id = %s AND u.id != %s AND lr.status = 'Approved' AND NOT (lr.end_date < %s OR lr.start_date > %s)",
            [uid, emp_id, str(start_dt), str(end_dt)],
            fetch='one'
        )
        overlap_count = overlap_info[0] if overlap_info else 0
        
        # Team tasks count (pending)
        team_tasks = db.execute(
            "SELECT COUNT(*) FROM tasks t JOIN users u ON t.user_id = u.id WHERE u.manager_id = %s AND t.status != 'Completed'",
            [uid], fetch='one'
        )
        team_tasks_count = team_tasks[0] if team_tasks else 0
        
        # Nearest task deadline for this employee
        emp_tasks = db.execute(
            "SELECT deadline FROM tasks WHERE user_id = %s AND status != 'Completed' ORDER BY deadline ASC",
            [emp_id]
        )
        
        days_to_deadline = 99  # safe default if no pending tasks
        if emp_tasks:
            # Parse closest deadline date
            closest_deadline = emp_tasks[0][0]
            if isinstance(closest_deadline, str):
                dl_date = datetime.strptime(closest_deadline, '%Y-%m-%d').date()
            else:
                dl_date = closest_deadline
            days_to_deadline = max(0, (dl_date - start_dt).days)
            
        # Busy Season determination (e.g. Month of start date is June, July, Nov, Dec)
        is_busy_season = start_dt.month in [6, 7, 11, 12]
        
        # Employee's pending task count
        emp_tasks_cnt = len(emp_tasks)
        
        # ML Evaluate Risk prediction
        ml_prediction = predictor.evaluate_leave(
            team_size=team_size,
            overlap_count=overlap_count,
            active_tasks=team_tasks_count,
            days_to_deadline=days_to_deadline,
            busy_season=is_busy_season,
            employee_tasks=emp_tasks_cnt
        )
        
        # Append additional metrics for displaying in UI
        ml_prediction['overlap_count'] = overlap_count
        ml_prediction['days_to_deadline'] = days_to_deadline
        ml_prediction['busy_season'] = is_busy_season
        ml_prediction['employee_tasks'] = emp_tasks_cnt
        
        enriched_pendings.append({
            'id': req_id,
            'employee_name': emp_name,
            'leave_type': leave_type,
            'start_date': start_date,
            'end_date': end_date,
            'reason': reason,
            'history': emp_history,
            'ml': ml_prediction
        })
        
    return render_template('manager_dashboard.html', roster=roster, requests=enriched_pendings)


# ----------------- PROFILE / ACCOUNT MANAGEMENT -----------------

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    
    if request.method == 'POST':
        dob = request.form.get('dob')
        position = request.form.get('position')
        gender = request.form.get('gender')
        
        db.execute(
            "UPDATE users SET dob = %s, position = %s, gender = %s WHERE id = %s",
            [dob, position, gender, uid],
            commit=True
        )
        session['gender'] = gender # Update session cache
        flash('Profile settings updated successfully.', 'success')
        return redirect(url_for('profile'))
        
    user_prof = db.execute(
        "SELECT u.name, u.dob, u.position, m.name as manager_name, u.role, u.profile_pic, u.email, u.username "
        "FROM users u LEFT JOIN users m ON u.manager_id = m.id WHERE u.id = %s",
        [uid], fetch='one'
    )
    return render_template('profile.html', profile=user_prof)

@app.route('/account', methods=['GET', 'POST'])
def account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    uid = session['user_id']
    
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('account'))
            
        if is_strong_password(new_password):
            hashed = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.execute("UPDATE users SET password = %s WHERE id = %s", [hashed, uid], commit=True)
            
            # Send notification email
            send_password_change_email(session['user_name'], session['user_email'])
            
            flash('Password reset successful! A security notification email was dispatched.', 'success')
        else:
            flash('Password strength requirements not satisfied. Try again.', 'danger')
            
    details = db.execute("SELECT email, username, name, role FROM users WHERE id = %s", [uid], fetch='one')
    return render_template('account.html', details=details)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # When deploying or launching locally, run on port 5001 in debug mode
    app.run(debug=True, host='0.0.0.0', port=5001)