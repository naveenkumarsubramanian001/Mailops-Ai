-- Employees
CREATE TABLE employees (
  employee_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  department TEXT,
  role TEXT,
  status TEXT CHECK (status IN ('active','inactive')),
  joined_date DATE
);

-- Daily Attendance
CREATE TABLE attendance_daily (
  employee_id TEXT,
  date DATE,
  status TEXT CHECK (status IN ('present','absent','leave')),
  PRIMARY KEY (employee_id, date)
);

-- Leave Balance
CREATE TABLE leave_balance (
  employee_id TEXT PRIMARY KEY,
  sick_used INTEGER,
  sick_total INTEGER,
  casual_used INTEGER,
  casual_total INTEGER,
  earned_used INTEGER,
  earned_total INTEGER
);

-- Email logs
CREATE TABLE email_logs (
  email_id TEXT PRIMARY KEY,
  sender_email TEXT,
  intent TEXT,
  received_at TEXT,
  processed_at TEXT
);

-- Document verification results
CREATE TABLE document_verification (
  email_id TEXT,
  trust_score INTEGER,
  verdict TEXT,
  flags TEXT
);

-- Issues
CREATE TABLE issues (
  issue_id TEXT PRIMARY KEY,
  employee_id TEXT,
  category TEXT,
  status TEXT,
  priority TEXT,
  created_at TEXT
);

-- Decisions & audit trail
CREATE TABLE decisions (
  decision_id TEXT PRIMARY KEY,
  email_id TEXT,
  acceptance_score INTEGER,
  decision TEXT,
  reasoning TEXT,
  created_at TEXT
);
