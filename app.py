from flask import Flask, jsonify, request, render_template, send_file
import os
import re
import threading
import smtplib
import time
import signal
from datetime import datetime
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Import existing database logic
from database import (
    init_db,
    get_connection,
    get_setting,
    set_setting,
    get_departments,
    get_issue_types,
    get_next_ticket,
    get_all_employees,
    bulk_upsert_employees,
    upsert_employee
)

app = Flask(__name__, template_folder="templates", static_folder="static")

DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%I:%M %p"

# Initialize DB on server start
init_db()

# ==========================================
# EMPLOYEE SYNC HELPERS (from main.py)
# ==========================================
_last_csv_mtime = 0
_last_xlsx_mtime = 0

def sync_employees_from_file():
    global _last_csv_mtime, _last_xlsx_mtime
    
    csv_file = None
    xlsx_file = None
    
    for folder in [".", "dist"]:
        csv_path = os.path.join(folder, "employees.csv")
        xlsx_path = os.path.join(folder, "employees.xlsx")
        
        if os.path.exists(csv_path):
            csv_file = csv_path
            break
        elif os.path.exists(xlsx_path):
            xlsx_file = xlsx_path
            break
            
    if not csv_file and not xlsx_file:
        return
        
    if csv_file:
        try:
            mtime = os.path.getmtime(csv_file)
            if mtime <= _last_csv_mtime:
                return
        except Exception:
            return
    elif xlsx_file:
        try:
            mtime = os.path.getmtime(xlsx_file)
            if mtime <= _last_xlsx_mtime:
                return
        except Exception:
            return

    df = None
    new_mtime = 0
    if csv_file:
        try:
            new_mtime = os.path.getmtime(csv_file)
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
            return
    elif xlsx_file:
        try:
            new_mtime = os.path.getmtime(xlsx_file)
            df = pd.read_excel(xlsx_file)
        except Exception as e:
            print(f"Error reading {xlsx_file}: {e}")
            return
            
    if df is not None:
        employee_list = []
        for _, row in df.iterrows():
            name = str(row.get("Name", row.get("name", ""))).strip()
            email = str(row.get("Email", row.get("email", ""))).strip()
            dept = str(row.get("Department", row.get("department", ""))).strip()
            
            if name and name.lower() != "nan":
                email_clean = email if email.lower() != "nan" else ""
                dept_clean = dept if dept.lower() != "nan" else ""
                employee_list.append((name, email_clean, dept_clean))
                
        if employee_list:
            bulk_upsert_employees(employee_list)

        # Update last synced mtime only after successful read and DB upsert
        if csv_file:
            _last_csv_mtime = new_mtime
        elif xlsx_file:
            _last_xlsx_mtime = new_mtime

def get_employee_mapping():
    try:
        sync_employees_from_file()
    except Exception as e:
        print(f"Error during employee file sync: {e}")

    mapping = {}
    try:
        db_employees = get_all_employees()
        for name, email, dept in db_employees:
            if name:
                mapping[name.strip().lower()] = {
                    "name": name.strip(),
                    "email": email.strip() if email else "",
                    "department": dept.strip() if dept else ""
                }
    except Exception as e:
        print(f"Error loading employees from table: {e}")

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT employee_name, employee_email, department 
            FROM call_logs 
            WHERE employee_name IS NOT NULL AND employee_name != '' AND deleted = 0
            ORDER BY id ASC
        """)
        for name, email, dept in cur.fetchall():
            name_key = name.strip().lower()
            if name_key not in mapping:
                mapping[name_key] = {
                    "name": name.strip(),
                    "email": email.strip() if email else "",
                    "department": dept.strip() if dept else ""
                }
    except Exception as e:
        print(f"Error loading employees from call_logs: {e}")
    finally:
        conn.close()

    return mapping

# ==========================================
# EMAIL SENDING HELPERS
# ==========================================
def validate_email(email):
    if not email:
        return True
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def trigger_ticket_email(ticket_no, email_type, details):
    smtp_host = get_setting("smtp_host", "smtp.gmail.com")
    smtp_port = get_setting("smtp_port", "587")
    smtp_user = get_setting("smtp_user", "")
    smtp_password = get_setting("smtp_password", "")
    smtp_use_tls = get_setting("smtp_use_tls", "1") == "1"
    email_enabled = get_setting("email_enabled", "0") == "1"
                                           
    if not email_enabled or not details.get("employee_email"):
        return
        
    if not smtp_user or not smtp_password:
        print("SMTP settings incomplete. Skipping email.")
        return

    email_type_lower = email_type.lower()
    
    base_url = "http://127.0.0.1:5000"
    try:
        if request and request.host_url:
            base_url = request.host_url.rstrip("/")
    except Exception:
        pass

    excellent_url = f"{base_url}/api/feedback/{ticket_no}?rating=Excellent"
    poor_url = f"{base_url}/api/feedback/{ticket_no}?rating=Poor"

    if email_type_lower in ("registered", "open"):                      
        subject = f"Ticket Registered - {ticket_no}"
        body = f"""Dear {details['employee_name']},
                                      
Your IT Helpdesk ticket has been successfully registered.

Ticket Details:
---------------------------------------------
Ticket No:    {ticket_no}
Date Logged:  {details['log_date']} {details['call_time']}
Issue:        {details['issue']}
Status:       Open
---------------------------------------------

Our team has received your ticket, and an engineer will review it shortly.

Best regards,
IT Helpdesk Support
"""
    elif email_type_lower == "in progress":
        subject = f"Ticket In Progress - {ticket_no}"
        body = f"""Dear {details['employee_name']},
 
We would like to inform you that work on your IT Helpdesk ticket is now in progress.
 
Ticket Details:
---------------------------------------------
Ticket No:    {ticket_no}
Issue:        {details['issue']}
Status:       In Progress
Engineer:     {details['engineer']}
Remarks:      {details['remarks']}
---------------------------------------------
 
Our engineers are actively working to resolve your issue. We will notify you once it is resolved.
 
Best regards,
IT Helpdesk Support
"""
    elif email_type_lower in ("resolved", "solved"):
        subject = f"Ticket Resolved - {ticket_no}"
        body = f"""Dear {details['employee_name']},
 
We are pleased to inform you that your IT Helpdesk ticket has been resolved.
 
Ticket Details:
---------------------------------------------
Ticket No:     {ticket_no}
Issue:         {details['issue']}
Resolved Date: {details['resolved_date']} {details['resolved_time']}
Engineer:      {details['engineer']}
Remarks:       {details['remarks']}
---------------------------------------------
 
Rate your support experience:
👍 Excellent: {excellent_url}
👎 Poor:      {poor_url}
 
If you have any further questions or if the issue persists, please feel free to reach out.
 
Best regards,
IT Helpdesk Support
"""
    elif email_type_lower == "closed":
        subject = f"Ticket Closed - {ticket_no}"
        body = f"""Dear {details['employee_name']},
 
Your IT Helpdesk ticket is now closed.
 
Ticket Details:
---------------------------------------------
Ticket No:     {ticket_no}
Issue:         {details['issue']}
Resolved Date: {details['resolved_date']} {details['resolved_time']}
Engineer:      {details['engineer']}
Remarks:       {details['remarks']}
---------------------------------------------
 
Rate your support experience:
👍 Excellent: {excellent_url}
👎 Poor:      {poor_url}
 
Thank you for your patience. This ticket is now completed and closed.
 
Best regards,
IT Helpdesk Support
"""
    else:
        return

    def run_send():
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = details['employee_email']
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            port_val = int(smtp_port)
            # Increased timeout to 30s to help prevent TLS handshake timeout errors
            if port_val == 465:
                server = smtplib.SMTP_SSL(smtp_host, port_val, timeout=30)
            else:
                server = smtplib.SMTP(smtp_host, port_val, timeout=30)
                if smtp_use_tls:
                    server.starttls()
            
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()


            # Log Success in DB
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO email_logs(ticket_no, recipient, subject, status, sent_time)
                VALUES(?,?,?,?,?)
            """, (
                ticket_no,
                details['employee_email'],
                subject,
                "SUCCESS",
                datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}")
            ))
            conn.commit()
            conn.close()
        except Exception as ex:
            # Log failure in DB
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO email_logs(ticket_no, recipient, subject, status, sent_time, error_message)
                    VALUES(?,?,?,?,?,?)
                """, (
                    ticket_no,
                    details['employee_email'],
                    subject,
                    "FAILED",
                    datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}"),
                    str(ex)
                ))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Error logging failed email status: {e}")
            print(f"Email notification error: {ex}")

    threading.Thread(target=run_send, daemon=True).start()

# ==========================================
# CLIENT KEEPALIVE / SHUTDOWN MONITOR
# ==========================================
last_ping_time = time.time()

def shutdown_monitor():
    global last_ping_time
    # 15 seconds grace period for server to start and client to connect
    time.sleep(15)
    while True:
        time.sleep(2)
        if time.time() - last_ping_time > 60.0:
            print("No active clients detected. Shutting down server...")
            os.kill(os.getpid(), signal.SIGTERM)
            break

@app.route("/api/ping", methods=["POST"])
def api_ping():
    global last_ping_time
    last_ping_time = time.time()
    return jsonify({"success": True})

# ==========================================
# UNIFIED TICKET SERIALIZATION HELPERS
# ==========================================
TICKET_COLUMNS_SQL = """
    ticket_no, log_date, call_time, employee_name, department,
    issue_type, issue, priority, status, remarks, engineer,
    resolved_date, resolved_time, employee_email, engineer_email,
    rating, rating_time
"""

def parse_ticket_row(r):
    return {
        "ticket_no": r[0],
        "log_date": r[1],
        "call_time": r[2],
        "employee_name": r[3],
        "department": r[4],
        "issue_type": r[5],
        "issue": r[6],
        "priority": r[7],
        "status": r[8],
        "remarks": r[9],
        "engineer": r[10],
        "resolved_date": r[11],
        "resolved_time": r[12],
        "employee_email": r[13],
        "engineer_email": r[14],
        "rating": r[15] if len(r) > 15 else None,
        "rating_time": r[16] if len(r) > 16 else None
    }

# ==========================================
# CORE WEB ROUTES
# ==========================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    return send_file(os.path.join(app.root_path, "static", "favicon.ico"))

# Fetch autocomplete mapping for frontend
@app.route("/api/employees")
def api_employees():
    mapping = get_employee_mapping()
    return jsonify(mapping)

# Fetch static dropdown listings
@app.route("/api/meta")
def api_meta():
    return jsonify({
        "departments": get_departments(),
        "issue_types": get_issue_types(),
        "next_ticket": get_next_ticket(),
        "current_date": datetime.now().strftime(DATE_FORMAT),
        "current_time": datetime.now().strftime(TIME_FORMAT)
    })

# Fetch dashboard counts
@app.route("/api/dashboard")
def api_dashboard():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM call_logs WHERE deleted = 0")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM call_logs WHERE deleted = 0 AND status IN ('Open', 'In Progress')")
        open_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM call_logs WHERE deleted = 0 AND status IN ('Resolved', 'Closed')")
        resolved_count = cur.fetchone()[0]
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({
        "total": total,
        "open": open_count,
        "resolved": resolved_count
    })

# Fetch all tickets with filters & search
@app.route("/api/tickets")
def api_tickets():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "All").strip()

    query = f"""
    SELECT {TICKET_COLUMNS_SQL}
    FROM call_logs
    WHERE deleted = 0
    """
    params = []

    if search:
        query += """
        AND (
            ticket_no LIKE ?
            OR employee_name LIKE ?
            OR engineer LIKE ?
            OR issue LIKE ?
            OR department LIKE ?
        )
        """
        like_str = f"%{search}%"
        params.extend([like_str, like_str, like_str, like_str, like_str])

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    conn = get_connection()
    tickets = []
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        for r in rows:
            tickets.append(parse_ticket_row(r))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify(tickets)

# Get specific ticket
@app.route("/api/tickets/<ticket_no>")
def api_get_ticket(ticket_no):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {TICKET_COLUMNS_SQL}
            FROM call_logs
            WHERE ticket_no = ? AND deleted = 0
        """, (ticket_no,))
        r = cur.fetchone()
        if not r:
            return jsonify({"error": "Ticket not found"}), 404
        
        ticket = parse_ticket_row(r)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify(ticket)

# Create / Save Ticket
@app.route("/api/tickets", methods=["POST"])
def api_save_ticket():
    data = request.json
    if not data:
        return jsonify({"error": "No payload provided"}), 400

    ticket_no = (data.get("ticket_no") or "").strip()
    is_new = False
    if not ticket_no:
        ticket_no = get_next_ticket()
        is_new = True

    employee_name = (data.get("employee_name") or "").strip()
    employee_email = (data.get("employee_email") or "").strip()
    engineer = (data.get("engineer") or "").strip()
    engineer_email = (data.get("engineer_email") or "").strip()
    issue = (data.get("issue") or "").strip()
    log_date = (data.get("log_date") or "").strip()
    call_time = (data.get("call_time") or "").strip()
    status = (data.get("status") or "In Progress").strip()
    resolved_date = (data.get("resolved_date") or "").strip()
    resolved_time = (data.get("resolved_time") or "").strip()
    priority = (data.get("priority") or "High").strip()
    department = (data.get("department") or "").strip()
    issue_type = (data.get("issue_type") or "").strip()
    remarks = (data.get("remarks") or "").strip()

    # Validations
    if not employee_name:
        return jsonify({"error": "Employee Name cannot be empty"}), 400
    if not engineer:
        return jsonify({"error": "Engineer cannot be empty"}), 400
    if not issue:
        return jsonify({"error": "Issue cannot be empty"}), 400

    if employee_email and not validate_email(employee_email):
        return jsonify({"error": "Invalid Employee Email format"}), 400
    if engineer_email and not validate_email(engineer_email):
        return jsonify({"error": "Invalid Engineer Email format"}), 400

    # Auto-adjust dates/times based on status change
    if (resolved_date or resolved_time) and status not in ("Resolved", "Closed"):
        status = "Resolved"

    if status in ("Resolved", "Closed"):
        if not resolved_date:
            resolved_date = datetime.now().strftime(DATE_FORMAT)
        if not resolved_time:
            resolved_time = datetime.now().strftime(TIME_FORMAT)
    else:
        resolved_date = ""
        resolved_time = ""

    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # Determine if ticket is an insert or update by checking if it already exists (including soft-deleted)
        cur.execute("SELECT status, resolved_email_sent, deleted FROM call_logs WHERE ticket_no = ?", (ticket_no,))
        existing = cur.fetchone()
        
        prev_status = None
        resolved_email_sent = 0
        should_send_resolved_email = False
        should_send_closed_email = False
        
        if existing:
            prev_status = existing[0]
            resolved_email_sent = existing[1]
            was_deleted = existing[2]
            if was_deleted:
                is_new = True
            
            # UPDATE (also un-deletes if soft-deleted)
            cur.execute("""
                UPDATE call_logs
                SET
                    log_date=?, call_time=?, employee_name=?, employee_email=?, department=?,
                    issue_type=?, issue=?, priority=?, status=?, remarks=?, engineer=?,
                    resolved_date=?, resolved_time=?, engineer_email=?, deleted=0
                WHERE ticket_no=?
            """, (
                log_date, call_time, employee_name, employee_email, department,
                issue_type, issue, priority, status, remarks, engineer,
                resolved_date, resolved_time, engineer_email, ticket_no
            ))
        else:
            is_new = True
            # INSERT
            cur.execute("""
                INSERT INTO call_logs
                (
                    ticket_no, log_date, call_time, employee_name, employee_email, department,
                    issue_type, issue, priority, status, remarks, engineer,
                    resolved_date, resolved_time, engineer_email, resolved_email_sent
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_no, log_date, call_time, employee_name, employee_email, department,
                issue_type, issue, priority, status, remarks, engineer,
                resolved_date, resolved_time, engineer_email,
                1 if status in ("Resolved", "Closed") else 0
            ))

        # Upsert employee details to employees table
        upsert_employee(employee_name, employee_email, department, cur)

        # Check email triggers inside transaction before committing
        if not is_new and status != prev_status:
            if status == "Resolved" and resolved_email_sent == 0:
                should_send_resolved_email = True
                cur.execute("UPDATE call_logs SET resolved_email_sent=1 WHERE ticket_no=?", (ticket_no,))
            elif status == "Closed":
                should_send_closed_email = True

        conn.commit()

        # Build details dict for email triggers
        email_details = {
            "employee_name": employee_name,
            "employee_email": employee_email,
            "engineer_email": engineer_email,
            "log_date": log_date,
            "call_time": call_time,
            "issue": issue,
            "priority": priority,
            "status": status,
            "resolved_date": resolved_date,
            "resolved_time": resolved_time,
            "engineer": engineer,
            "remarks": remarks
        }

        # Asynchronously send email notification AFTER committing DB transaction
        if is_new:
            trigger_ticket_email(ticket_no, "registered", email_details)
        else:
            if should_send_resolved_email:
                trigger_ticket_email(ticket_no, "Resolved", email_details)
            elif should_send_closed_email:
                trigger_ticket_email(ticket_no, "Closed", email_details)

    except Exception as e:
        conn.rollback()
        if "UNIQUE constraint failed" in str(e):
            return jsonify({"error": "Ticket Number already exists! Use a unique number."}), 409
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"success": True, "ticket_no": ticket_no})

# Resend Email Notification for specific ticket
@app.route("/api/tickets/<ticket_no>/resend_email", methods=["POST"])
def api_resend_ticket_email(ticket_no):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(f"""
            SELECT {TICKET_COLUMNS_SQL}
            FROM call_logs
            WHERE ticket_no = ? AND deleted = 0
        """, (ticket_no,))
        r = cur.fetchone()
        if not r:
            return jsonify({"error": "Ticket not found"}), 404

        ticket = parse_ticket_row(r)
        if not ticket.get("employee_email"):
            return jsonify({"error": "No employee email address associated with this ticket."}), 400

        email_details = {
            "employee_name": ticket["employee_name"],
            "employee_email": ticket["employee_email"],
            "engineer_email": ticket["engineer_email"],
            "log_date": ticket["log_date"],
            "call_time": ticket["call_time"],
            "issue": ticket["issue"],
            "priority": ticket["priority"],
            "status": ticket["status"],
            "resolved_date": ticket["resolved_date"],
            "resolved_time": ticket["resolved_time"],
            "engineer": ticket["engineer"],
            "remarks": ticket["remarks"]
        }

        st = ticket["status"].lower()
        if st in ("resolved", "closed"):
            trigger_type = ticket["status"]
        else:
            trigger_type = "registered"

        trigger_ticket_email(ticket_no, trigger_type, email_details)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"success": True, "message": f"Email notification resent for {ticket_no}"})

# Customer Feedback Endpoint
@app.route("/api/feedback/<ticket_no>")
def api_ticket_feedback(ticket_no):
    rating = request.args.get("rating", "").strip()
    if rating not in ("Excellent", "Poor"):
        return "Invalid rating selection.", 400

    rating_time = datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE call_logs
            SET rating = ?, rating_time = ?
            WHERE ticket_no = ? AND deleted = 0
        """, (rating, rating_time, ticket_no))
        conn.commit()
    except Exception as e:
        return f"Error recording feedback: {e}", 500
    finally:
        conn.close()

    emoji = "👍" if rating == "Excellent" else "👎"
    color = "#16a34a" if rating == "Excellent" else "#dc2626"

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feedback Received - IT Helpdesk</title>
        <style>
            body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f8fafc; color: #1e293b; }}
            .card {{ background: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08); text-align: center; max-width: 420px; border: 1px solid #e2e8f0; }}
            .icon {{ font-size: 56px; margin-bottom: 16px; }}
            h2 {{ margin: 0 0 12px; color: {color}; font-size: 24px; }}
            p {{ color: #64748b; margin: 0; line-height: 1.5; }}
            .ticket-badge {{ display: inline-block; margin-top: 16px; padding: 6px 12px; background: #f1f5f9; border-radius: 6px; font-weight: 600; color: #334155; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon">{emoji}</div>
            <h2>Thank You For Your Feedback!</h2>
            <p>Your rating (<strong>{rating}</strong>) has been recorded successfully.</p>
            <div class="ticket-badge">Ticket: {ticket_no}</div>
        </div>
    </body>
    </html>
    """

# Delete/Soft-Delete Ticket
@app.route("/api/tickets/<ticket_no>", methods=["DELETE"])
def api_delete_ticket(ticket_no):
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Fetch ticket details to log into deleted history
        cur.execute("""
            SELECT
                ticket_no, log_date, call_time, employee_name, department,
                issue_type, issue, priority, status, remarks, engineer,
                resolved_date, resolved_time, employee_email
            FROM call_logs
            WHERE ticket_no = ? AND deleted = 0
        """, (ticket_no,))
        row = cur.fetchone()

        if not row:
            return jsonify({"error": "Ticket not found"}), 404

        # Save to history Excel file
        history_dir = "history"
        os.makedirs(history_dir, exist_ok=True)
        ticket_no, log_date, call_time, employee_name, department, issue_type, issue, priority, status, remarks, engineer, resolved_date, resolved_time, employee_email = row
        deleted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ticket_data = {
            "Ticket No": [ticket_no],
            "Status": [status],
            "Priority": [priority],
            "Date Logged": [log_date],
            "Time Logged": [call_time],
            "Employee Name": [employee_name],
            "Employee Email": [employee_email or ''],
            "Department": [department],
            "Issue Type": [issue_type],
            "Engineer": [engineer],
            "Resolved Date": [resolved_date or 'N/A'],
            "Resolved Time": [resolved_time or 'N/A'],
            "Issue Description": [issue],
            "Remarks": [remarks or ''],
            "Deleted At": [deleted_at]
        }

        file_path = os.path.join(history_dir, "deleted_history.xlsx")
        if os.path.exists(file_path):
            try:
                existing_df = pd.read_excel(file_path)
                df = pd.concat([existing_df, pd.DataFrame(ticket_data)], ignore_index=True)
            except Exception as ex:
                return jsonify({"error": f"Could not read deleted history Excel file: {ex}"}), 500
        else:
            df = pd.DataFrame(ticket_data)

        try:
            df.to_excel(file_path, index=False)
        except PermissionError:
            return jsonify({"error": "Deleted history Excel sheet is open in Excel. Close it and try again."}), 423

        # Update soft delete key in database
        cur.execute("UPDATE call_logs SET deleted = 1 WHERE ticket_no = ?", (ticket_no,))
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"success": True})

# Export Excel of all tickets
@app.route("/api/export", methods=["POST"])
def api_export():
    try:
        os.makedirs("exports", exist_ok=True)
        filename = datetime.now().strftime("exports/call_logs_%Y%m%d_%H%M%S.xlsx")
        filepath = os.path.join(os.getcwd(), filename)

        conn = get_connection()
        try:
            df = pd.read_sql_query("""
                SELECT
                    ticket_no AS [Ticket],
                    employee_name AS [Employee],
                    employee_email AS [Employee Email],
                    log_date AS [Date],
                    call_time AS [Time],
                    resolved_date AS [Resolved Date],
                    resolved_time AS [Resolved Time],
                    department AS [Department],
                    issue AS [Issue],
                    issue_type AS [Issue Type],
                    priority AS [Priority],
                    status AS [Status],
                    engineer AS [Engineer],
                    remarks AS [Remarks]
                FROM call_logs
                WHERE deleted = 0
                ORDER BY id DESC
            """, conn)
        finally:
            conn.close()

        df.to_excel(filepath, index=False)
        
        return send_file(filepath, as_attachment=True, download_name=os.path.basename(filename))
    except Exception as e:
        if isinstance(e, PermissionError) or "Permission denied" in str(e):
            return jsonify({"error": "Export file is open or locked in another program. Please close Excel and try again."}), 423
        return jsonify({"error": str(e)}), 500

# Get current SMTP settings
@app.route("/api/settings")
def api_get_settings():
    try:
        return jsonify({
            "email_enabled": get_setting("email_enabled", "0") == "1",
            "smtp_host": get_setting("smtp_host", "smtp.gmail.com"),
            "smtp_port": get_setting("smtp_port", "587"),
            "smtp_user": get_setting("smtp_user", ""),
            "smtp_password": get_setting("smtp_password", ""),
            "smtp_use_tls": get_setting("smtp_use_tls", "1") == "1"
        })
    except Exception as e:
        print(f"Error loading SMTP settings: {e}")
        return jsonify({"error": str(e)}), 500

# Save SMTP settings
@app.route("/api/settings", methods=["POST"])
def api_save_settings():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No settings payload provided"}), 400

        set_setting("email_enabled", "1" if data.get("email_enabled") else "0")
        set_setting("smtp_host", data.get("smtp_host", "smtp.gmail.com").strip())
        set_setting("smtp_port", str(data.get("smtp_port", "587")).strip())
        set_setting("smtp_user", data.get("smtp_user", "").strip())
        set_setting("smtp_password", data.get("smtp_password", ""))
        set_setting("smtp_use_tls", "1" if data.get("smtp_use_tls") else "0")

        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving SMTP settings: {e}")
        return jsonify({"error": str(e)}), 500

# Test SMTP Connection Settings
@app.route("/api/settings/test", methods=["POST"])
def api_test_settings():
    data = request.json
    if not data:
        return jsonify({"error": "No parameters provided"}), 400

    host = data.get("smtp_host", "").strip()
    port = data.get("smtp_port", "").strip()
    user = data.get("smtp_user", "").strip()
    pwd = data.get("smtp_password", "")
    use_tls = data.get("smtp_use_tls")
    test_to = data.get("test_recipient", "").strip()

    if not host or not port or not user or not pwd or not test_to:
        return jsonify({"error": "Please fill in all SMTP fields and the Test Recipient Email."}), 400

    if not validate_email(test_to):
        return jsonify({"error": "Invalid Test Recipient Email format."}), 400

    try:
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = test_to
        msg['Subject'] = "IT Helpdesk Call Logger - SMTP Test Connection"
        msg.attach(MIMEText("This is a test email. Your SMTP configuration works!", 'plain'))

        port_num = int(port)
        # Higher timeout of 30 seconds for test connection to prevent handshake timeouts
        if port_num == 465:
            server = smtplib.SMTP_SSL(host, port_num, timeout=30)
        else:
            server = smtplib.SMTP(host, port_num, timeout=30)
            if use_tls:
                server.starttls()

        server.login(user, pwd)
        server.send_message(msg)
        server.quit()
    except Exception as ex:
        return jsonify({"success": False, "error": str(ex)})

    return jsonify({"success": True})

if __name__ == "__main__":
    # Start the client monitoring thread if this is the main process / not the reloader wrapper
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        monitor_thread = threading.Thread(target=shutdown_monitor, daemon=True)
        monitor_thread.start()

    # Run on all network interfaces so it can be reached by mobile devices on local Wi-Fi
    app.run(host="0.0.0.0", port=5000, debug=True)
