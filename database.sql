-- Employee Leave Management System Database Schema
-- Compatible with MySQL and SQLite

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'employee', -- 'employee' or 'manager'
    gender VARCHAR(20) DEFAULT 'Male',
    dob DATE NULL,
    position VARCHAR(100) DEFAULT 'Developer',
    manager_id INTEGER NULL,
    total_leaves INTEGER DEFAULT 24,
    leaves_taken INTEGER DEFAULT 0,
    profile_pic VARCHAR(255) NULL,
    FOREIGN KEY(manager_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 2. Leave Requests Table
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    leave_type VARCHAR(50) NOT NULL, -- e.g. Casual, Sick, Menstrual, Paid, Maternal, Paternal
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'Approved', 'Rejected'
    remarks TEXT NULL, -- Manager's rejection reason
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Tasks / Deadlines Table
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_name VARCHAR(100) NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    deadline DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);