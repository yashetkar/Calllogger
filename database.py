import sqlite3
import os

from datetime import datetime

os.makedirs("database", exist_ok=True)

DB_PATH = "database/helpdesk.db"
import shutil

def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():

    conn = get_connection()
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

        deleted INTEGER DEFAULT 0,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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

    conn.commit()
    conn.close()

def get_next_ticket():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT MAX(id) FROM call_logs"
    )

    last_id = cur.fetchone()[0]

    conn.close()

    if last_id is None:
        last_id = 0

    return f"TKT-{last_id + 1:06d}"