import sqlite3
import os
import shutil
from datetime import datetime

CONFIG_PATH = "config.txt"
DB_PATH = "database/helpdesk.db"

# Load database path from config.txt if it exists
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, val = line.split("=", 1)
                        if key.strip().upper() == "DB_PATH":
                            DB_PATH = val.strip().strip('"').strip("'")
                            break
    except Exception as e:
        pass

# Ensure parent directory of DB_PATH exists
db_dir = os.path.dirname(DB_PATH)
if db_dir:
    os.makedirs(db_dir, exist_ok=True)

def get_connection():
    return sqlite3.connect(DB_PATH, timeout=10.0)


def init_db():

    conn = get_connection()
    try:
        cur = conn.cursor()

        os.makedirs("backup", exist_ok=True)

        if os.path.exists(DB_PATH):

            backup_name = datetime.now().strftime(
                "backup/helpdesk_%Y%m%d.db"
            )

            if not os.path.exists(backup_name):
                shutil.copy(DB_PATH, backup_name)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS call_logs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_no TEXT UNIQUE,

            log_date TEXT,
            call_time TEXT,

            employee_name TEXT,
            employee_email TEXT,
            department TEXT,
            issue_type TEXT,

            issue TEXT,

            priority TEXT CHECK(
                priority IN (
                    'Low',
                    'Medium',
                    'High',
                    'Critical'
                )
            ),

            status TEXT CHECK(
                status IN (
                    'Open',
                    'In Progress',
                    'Resolved',
                    'Closed'
                )
            ),

            remarks TEXT,
            engineer TEXT,

            resolved_date TEXT,
            resolved_time TEXT,

            resolved_email_sent INTEGER DEFAULT 0,
            engineer_email TEXT,

            deleted INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Migration for existing databases
        try:
            cur.execute("ALTER TABLE call_logs ADD COLUMN resolved_email_sent INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass

        try:
            cur.execute("ALTER TABLE call_logs ADD COLUMN employee_email TEXT")
        except sqlite3.OperationalError:
            pass

        try:
            cur.execute("ALTER TABLE call_logs ADD COLUMN engineer_email TEXT")
        except sqlite3.OperationalError:
            pass

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ticket
        ON call_logs(ticket_no)
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_employee
        ON call_logs(employee_name)
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_status
        ON call_logs(status)
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_priority
        ON call_logs(priority)
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_engineer
        ON call_logs(engineer)
        """)

        # Create departments lookup table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS departments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)

        # Create issue_types lookup table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS issue_types(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
        """)

        # Create settings table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS email_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_no TEXT,
            recipient TEXT,
            subject TEXT,
            status TEXT,
            sent_time TEXT,
            error_message TEXT
        )
        """)

        # Populate default departments
        default_departments = ["sourcing", "HR", "accounts", "Sales", "IT"]
        for dept in default_departments:
            cur.execute("INSERT OR IGNORE INTO departments (name) VALUES (?)", (dept,))

        # Populate default issue types
        default_issue_types = [
            "Email Issue",
            "Application Issue",
            "Password Reset",
            "Printer Issue",
            "VPN Issue",
            "Internet Issue",
            "Network Issue",
            "System Slow",
            "Software Installation",
            "Hardware Issue",
            "Access Request",
            "Others"
        ]
        for issue in default_issue_types:
            cur.execute("INSERT OR IGNORE INTO issue_types (name) VALUES (?)", (issue,))

        # Populate default settings
        default_settings = [
            ("email_enabled", "0"),
            ("smtp_host", "smtp.gmail.com"),
            ("smtp_port", "587"),
            ("smtp_user", ""),
            ("smtp_password", ""),
            ("smtp_use_tls", "1")
        ]
        for key, val in default_settings:
            cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, val))

        # Create employees lookup table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            email TEXT,
            department TEXT
        )
        """)

        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_employees_name
        ON employees(name)
        """)

        conn.commit()
    finally:
        conn.close()

def upsert_employee(name, email, department):
    name = name.strip()
    if not name:
        return
    email = email.strip() if email else ""
    department = department.strip() if department else ""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM employees WHERE name = ?", (name,))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE employees
                SET email = ?, department = ?
                WHERE id = ?
            """, (email, department, row[0]))
        else:
            cur.execute("""
                INSERT INTO employees (name, email, department)
                VALUES (?, ?, ?)
            """, (name, email, department))
        conn.commit()
    except Exception as e:
        print(f"Error upserting employee: {e}")
    finally:
        conn.close()

def bulk_upsert_employees(employee_list):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Run everything in a single transaction
        for name, email, department in employee_list:
            name = name.strip()
            if not name:
                continue
            email = email.strip() if email else ""
            department = department.strip() if department else ""
            
            cur.execute("SELECT id FROM employees WHERE name = ?", (name,))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    UPDATE employees
                    SET email = ?, department = ?
                    WHERE id = ?
                """, (email, department, row[0]))
            else:
                cur.execute("""
                    INSERT INTO employees (name, email, department)
                    VALUES (?, ?, ?)
                """, (name, email, department))
        conn.commit()
    except Exception as e:
        print(f"Error in bulk upsert: {e}")
    finally:
        conn.close()

def get_all_employees():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, email, department FROM employees ORDER BY name ASC")
        return cur.fetchall()
    except Exception as e:
        print(f"Error getting employees: {e}")
        return []
    finally:
        conn.close()

def get_next_ticket():

    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            "SELECT MAX(id) FROM call_logs"
        )

        last_id = cur.fetchone()[0]
    finally:
        conn.close()

    if last_id is None:
        last_id = 0

    return f"TKT-{last_id + 1:06d}"

def get_departments():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM departments ORDER BY id ASC")
        rows = cur.fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]

def get_issue_types():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM issue_types ORDER BY id ASC")
        rows = cur.fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]

def get_setting(key, default=""):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        return row[0] if row else default
    except sqlite3.OperationalError:
        return default
    finally:
        conn.close()

def set_setting(key, value):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
    finally:
        conn.close()