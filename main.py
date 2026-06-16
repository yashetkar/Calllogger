import ttkbootstrap as tb
import shutil
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import os
from database import *
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# ==========================
# CONSTANTS
# ==========================
DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%I:%M %p"

# ==========================
# DATABASE INITIALIZATION
# ==========================

init_db()
# ==========================
# WINDOW
# ==========================
app = tb.Window(themename="flatly")
app.title("IT Helpdesk Call Logger")
app.geometry("1500x850")

# ==========================
# TITLE
# ==========================

title = tb.Label(
    app,
    text="🖥 IT HELPDESK CALL LOGGER",
    font=("Segoe UI", 12, "bold"),
    foreground="#38BDF8"
)
title.pack(pady=5)

# ==========================
# DASHBOARD
# ==========================

dashboard = tb.Frame(app)
dashboard.pack(fill=X, padx=15, pady=2)

total_lbl = tb.Label(
    dashboard,
    text="📋 TOTAL TICKETS: 0",
    font=("Segoe UI", 8, "bold"),
    bootstyle="info"
)
total_lbl.pack(side=LEFT, padx=15)

open_lbl = tb.Label(
    dashboard,
    text="⚠ OPEN: 0",
    font=("Segoe UI", 8, "bold"),
    bootstyle="danger"
)
open_lbl.pack(side=LEFT, padx=15)

resolved_lbl = tb.Label(
    dashboard,
    text="✅ RESOLVED: 0",
    font=("Segoe UI", 8, "bold"),
    bootstyle="success"
)
resolved_lbl.pack(side=LEFT, padx=15)

# ==========================
# FORM
# ==========================

form = tb.LabelFrame(
    app,
    text="TICKET DETAILS"
)

form.pack(
    fill="x",
    padx=10,
    pady=5
)



for i in (0, 2, 4, 6):
    form.grid_columnconfigure(i, weight=0)
for i in (1, 3, 5):
    form.grid_columnconfigure(i, weight=1)

# Ticket No

tb.Label(
    form,
    text="TICKET NO",
    font=("Segoe UI", 8, "bold")
).grid(row=0, column=0, padx=5, pady=3, sticky="e")

ticket_no_entry = tb.Entry(form, width=15)
ticket_no_entry.grid(
    row=0,
    column=1,
    padx=5,
    pady=3,
    sticky="ew"
)

# Date
tb.Label(
    form,
    text="DATE",
    font=("Segoe UI", 8, "bold")
).grid(row=0, column=2, padx=5, pady=3, sticky="e")

date_entry = tb.DateEntry(form, dateformat=DATE_FORMAT, width=12)
date_entry.grid(
    row=0,
    column=3,
    padx=5,
    pady=3,
    sticky="ew"
)

date_entry.entry.delete(0, "end")
date_entry.entry.insert(   
    0,
    datetime.now().strftime(DATE_FORMAT)
)

tb.Label(
    form,
    text="CALL TIME",
    font=("Segoe UI", 8, "bold")
).grid(row=0, column=4, padx=5, pady=3, sticky="e")

call_time_frame = tb.Frame(form)
call_time_frame.grid(
    row=0,
    column=5,
    padx=5,
    pady=3,
    sticky="ew"
)

call_time_entry = tb.Entry(
    call_time_frame,
    width=10
)
call_time_entry.pack(side=LEFT, fill=X, expand=True)

def set_call_time_now():
    call_time_entry.delete(0, END)
    call_time_entry.insert(0, datetime.now().strftime(TIME_FORMAT))

call_time_now_btn = tb.Button(
    call_time_frame,
    text="Now",
    bootstyle="secondary-outline",
    padding=(3, 1),
    command=set_call_time_now
)
call_time_now_btn.pack(side=LEFT, padx=(2, 0))

call_time_entry.insert(
    0,
    datetime.now().strftime(TIME_FORMAT)
)
# Priority

tb.Label(
    form,
    text="PRIORITY",
    font=("Segoe UI", 8, "bold")
).grid(row=1, column=4, padx=5, pady=3, sticky="e")

priority_combo = ttk.Combobox(
    form,
    values=[
        "Low",
        "Medium",
        "High",
        "Critical"
    ],
    state="readonly",
    width=20
)

priority_combo.grid(
    row=1,
    column=5,
    padx=5,
    pady=3,
    sticky="ew"
)
priority_combo.current(2)

# Status

tb.Label(
    form,
    text="STATUS",
    font=("Segoe UI", 8, "bold")
).grid(row=2, column=4, padx=5, pady=3, sticky="e")

status_combo = ttk.Combobox(
    form,
    values=[
        "Open",
        "In Progress",
        "Resolved",
        "Closed"
    ],
    state="readonly",
    width=20
)

status_combo.grid(
    row=2,
    column=5,
    padx=5,
    pady=3,
    sticky="ew"
)
status_combo.current(0)

# Department
tb.Label(
    form,
    text="DEPARTMENT",
    font=("Segoe UI", 8, "bold")
).grid(row=1, column=2, padx=5, pady=3, sticky="e")

department_combo = ttk.Combobox(
    form,
    values=get_departments(),
    state="readonly",
    width=20
)

department_combo.grid(
    row=1,
    column=3,
    padx=5,
    pady=3,
    sticky="ew"
)

department_combo.current(0)

tb.Label(
    form,
    text="RESOLVED DATE",
    font=("Segoe UI", 8, "bold")
).grid(row=3, column=0, padx=5, pady=3, sticky="e")

resolved_date_entry = tb.DateEntry(
    form,
    dateformat=DATE_FORMAT,
    width=12
)

resolved_date_entry.grid(
    row=3,
    column=1,
    padx=5,
    pady=3,
    sticky="ew"
)

tb.Label(
    form,
    text="RESOLVED TIME",
    font=("Segoe UI", 8, "bold")
).grid(row=3, column=2, padx=5, pady=3, sticky="e")

resolved_time_frame = tb.Frame(form)
resolved_time_frame.grid(
    row=3,
    column=3,
    padx=5,
    pady=3,
    sticky="ew"
)

resolved_time_entry = tb.Entry(
    resolved_time_frame,
    width=10
)
resolved_time_entry.pack(side=LEFT, fill=X, expand=True)

def set_resolved_time_now():
    resolved_time_entry.delete(0, END)
    resolved_time_entry.insert(0, datetime.now().strftime(TIME_FORMAT))

resolved_time_now_btn = tb.Button(
    resolved_time_frame,
    text="Now",
    bootstyle="secondary-outline",
    padding=(3, 1),
    command=set_resolved_time_now
)
resolved_time_now_btn.pack(side=LEFT, padx=(2, 0))

# Employee Email
tb.Label(
    form,
    text="EMPLOYEE EMAIL",
    font=("Segoe UI", 8, "bold")
).grid(row=3, column=4, padx=5, pady=3, sticky="e")

employee_email_entry = tb.Entry(
    form,
    width=30
)

employee_email_entry.grid(
    row=3,
    column=5,
    padx=5,
    pady=3,
    sticky="ew"
)


# Employee

tb.Label(
    form,
    text="EMPLOYEE",
    font=("Segoe UI", 8, "bold")
).grid(row=1, column=0, padx=5, pady=3, sticky="e")

employee_entry = ttk.Combobox(
    form,
    width=38
)

employee_entry.grid(
    row=1,
    column=1,
    padx=5,
    pady=3,
    sticky="ew"
)

tb.Label(
    form,
    text="ENGINEER",
    font=("Segoe UI", 8, "bold")
).grid(row=2, column=0, padx=5, pady=3, sticky="e")

engineer_entry = tb.Entry(
    form,
    width=40
)

engineer_entry.grid(
    row=2,
    column=1,
    padx=5,
    pady=3,
    sticky="ew"
)

# Issue Type

tb.Label(
    form,
    text="ISSUE TYPE",
    font=("Segoe UI", 8, "bold")
).grid(
    row=2,
    column=2,
    padx=5,
    pady=3,
    sticky="e"
)

issue_type_combo = ttk.Combobox(
    form,
    values=get_issue_types(),
    state="readonly",
    width=30
)

issue_type_combo.grid(
    row=2,
    column=3,
    padx=5,
    pady=3,
    sticky="ew"
)

issue_type_combo.current(0)
# Issue

tb.Label(
    form,
    text="ISSUE",
    font=("Segoe UI", 8, "bold")
).grid(
    row=4,
    column=0,
    padx=5,
    pady=3,
    sticky="e"
)

issue_text = tb.Text(
    form,
    height=2,
    width=30,
    font=("Segoe UI", 8)
)

issue_text.grid(
    row=4,
    column=1,
    padx=5,
    pady=3,
    sticky="ew"
)

# Remarks

tb.Label(
    form,
    text="REMARKS",
    font=("Segoe UI", 8, "bold")
).grid(
    row=4,
    column=2,
    padx=5,
    pady=3,
    sticky="e"
)

remarks_text = tb.Text(
    form,
    height=2,
    width=20,
    font=("Segoe UI", 8)
)

remarks_text.grid(
    row=4,
    column=3,
    padx=5,
    pady=3,
    sticky="w"
)

# Engineer Email
tb.Label(
    form,
    text="ENGINEER EMAIL",
    font=("Segoe UI", 8, "bold")
).grid(
    row=4,
    column=4,  
    padx=5,
    pady=3,
    sticky="e"
)

engineer_email_entry = tb.Entry(
    form,
    width=30
)

engineer_email_entry.grid(
    row=4,
    column=5,
    padx=5,
    pady=3,
    sticky="ew"
)

search_frame = tb.Frame(app)
search_frame.pack(fill=X, padx=10, pady=5)

search_entry = tb.Entry(
    search_frame,
    width=40
)

search_entry.pack(
    side=LEFT,
    padx=5
)

tb.Button(
    search_frame,
    text="🔍 SEARCH TICKET",
    bootstyle="primary-sm",
    command=lambda: load_data()
).pack(side=LEFT, padx=5)

tb.Label(
    search_frame,
    text="FILTER BY STATUS:",
    font=("Segoe UI", 8, "bold")
).pack(side=LEFT, padx=(20, 5))

status_filter_combo = ttk.Combobox(
    search_frame,
    values=["All", "Open", "In Progress", "Resolved", "Closed"],
    state="readonly",
    width=15
)
status_filter_combo.pack(side=LEFT, padx=5)
status_filter_combo.current(0)

status_filter_combo.bind("<<ComboboxSelected>>", lambda e: load_data())

selected_ticket = None

def load_ticket_to_form(ticket_no):
    global selected_ticket

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
        SELECT
            ticket_no,
            log_date,
            call_time,
            employee_name,
            department,
            issue_type,
            issue,
            priority,
            status,
            remarks,
            engineer,
            resolved_date,
            resolved_time,
            employee_email,
            engineer_email
        FROM call_logs
        WHERE ticket_no = ?
        """, (ticket_no,))
        row = cur.fetchone()
    finally:
        conn.close()

    if not row:
        return False

    selected_ticket = row[0]

    ticket_no_entry.config(state="normal")
    ticket_no_entry.delete(0, END)
    ticket_no_entry.insert(0, row[0])
    ticket_no_entry.config(state="readonly")

    # Date
    date_entry.entry.delete(0, END)
    date_entry.entry.insert(0, row[1])

    # Call Time
    call_time_entry.delete(0, END)
    call_time_entry.insert(0, row[2])

      # Employee
    employee_entry.delete(0, END)
    employee_entry.insert(0, row[3])

    # Department
    department_combo.set(row[4])

     # Issue Type
    issue_type_combo.set(row[5])

    # Issue
    issue_text.delete("1.0", END)
    issue_text.insert("1.0", row[6])
    # Priority
    priority_combo.set(row[7])

    # Status
    status_combo.set(row[8])

    # Remarks
    remarks_text.delete("1.0", END)
    remarks_text.insert("1.0", row[9])

    # Engineer
    engineer_entry.delete(0, END)
    engineer_entry.insert(0, row[10])

    # Resolved Date
    resolved_date_entry.entry.delete(0, END)
    if row[11]:
        resolved_date_entry.entry.insert(0, row[11])

    # Resolved Time
    resolved_time_entry.delete(0, END)
    if row[12]:
        resolved_time_entry.insert(0, row[12])

    # Employee Email
    employee_email_entry.delete(0, END)
    if row[13]:
        employee_email_entry.insert(0, row[13])

    # Engineer Email
    engineer_email_entry.delete(0, END)
    if len(row) > 14 and row[14]:
        engineer_email_entry.insert(0, row[14])

    app.title(f"Editing Ticket : {selected_ticket}")

    return True

def load_selected_ticket(event):
    selected = tree.selection()
    if not selected:
        return

    ticket_no = tree.item(selected[0])["values"][0]
    load_ticket_to_form(ticket_no)
# ==========================
# TABLE
# ==========================

table_frame = tb.Frame(app)
table_frame.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=(0,10)
)

columns = (
    "Ticket",
    "Employee",
    "Date",
    "Time",
    "Resolved Date",
    "Resolved Time",
    "Department",
    "Issue",
    "Issue Type",
    "Priority",
    "Status",
    "Engineer",
    "Remarks"
)

tree = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)

for col in columns:
    tree.heading(
        col,
        text=col,
        anchor=CENTER
    )

    tree.column(
        col,
        anchor=CENTER
    )

tree.column("Ticket", width=120)
tree.column("Employee", width=120)
tree.column("Date", width=120)
tree.column("Time", width=120)
tree.column("Resolved Date", width=120)
tree.column("Resolved Time", width=120)
tree.column("Department", width=120)
tree.column("Issue", width=200)
tree.column("Issue Type", width=130)
tree.column("Priority", width=90)
tree.column("Status", width=100)
tree.column("Engineer", width=100)
tree.column("Remarks", width=200)


scroll = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=tree.yview
)

tree.configure(
    yscrollcommand=scroll.set
)

# Horizontal Scrollbar
h_scroll = ttk.Scrollbar(
    table_frame,
    orient="horizontal",
    command=tree.xview
)

tree.configure(
    xscrollcommand=h_scroll.set
)

scroll.pack(
    side=RIGHT,
    fill=Y
)

h_scroll.pack(
    side=BOTTOM,
    fill=X
)

tree.pack(
    fill=BOTH,
    expand=True
)

tree.bind(
    "<Double-1>",
    load_selected_ticket
)
tree.tag_configure(
    "Critical",
    background="#FEE2E2"
)

tree.tag_configure(
    "High",
    background="#FEF3C7"
)

tree.tag_configure(
    "Open",
    background="#DBEAFE"
)

tree.tag_configure(
    "Resolved",
    background="#D1FAE5"
)

style = ttk.Style()

style.configure(".", font=("Segoe UI", 8))

style.configure(
    "Treeview",
    font=("Segoe UI", 8),
    rowheight=20
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 9, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#2563EB")],
    foreground=[("selected", "white")]
)
# ==========================
# FUNCTIONS
# ==========================
employee_mapping = {}

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
        
    # Check if files have actually changed
    if csv_file:
        try:
            mtime = os.path.getmtime(csv_file)
            if mtime <= _last_csv_mtime:
                return  # File has not changed, skip sync
            _last_csv_mtime = mtime
        except Exception:
            pass
    elif xlsx_file:
        try:
            mtime = os.path.getmtime(xlsx_file)
            if mtime <= _last_xlsx_mtime:
                return  # File has not changed, skip sync
            _last_xlsx_mtime = mtime
        except Exception:
            pass

    df = None
    if csv_file:
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    elif xlsx_file:
        try:
            df = pd.read_excel(xlsx_file)
        except Exception as e:
            print(f"Error reading {xlsx_file}: {e}")
            
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

def refresh_employee_list():
    global employee_mapping
    employee_mapping = get_employee_mapping()
    names = sorted([info["name"] for info in employee_mapping.values()])
    employee_entry['values'] = names

def autofill_employee_details(name):
    if not name:
        return
    info = employee_mapping.get(name.lower())
    if info:
        email = info.get("email", "")
        if email:
            employee_email_entry.delete(0, END)
            employee_email_entry.insert(0, email)
        
        dept = info.get("department", "")
        if dept:
            current_values = list(department_combo['values'])
            if dept not in current_values:
                current_values.append(dept)
                department_combo['values'] = current_values
            department_combo.set(dept)

def on_employee_keyrelease(event):
    if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Escape", "Tab"):
        return
    typed = employee_entry.get()
    if typed == '':
        employee_entry['values'] = sorted([info["name"] for info in employee_mapping.values()])
    else:
        filtered = [
            info["name"] for info in employee_mapping.values()
            if typed.lower() in info["name"].lower()
        ]
        employee_entry['values'] = sorted(filtered)

def on_employee_select(event):
    app.after(10, lambda: autofill_employee_details(employee_entry.get().strip()))

def on_employee_focus_out(event):
    autofill_employee_details(employee_entry.get().strip())

def on_status_change(event):
    status = status_combo.get()
    if status in ("Resolved", "Closed"):
        if not resolved_date_entry.entry.get().strip():
            resolved_date_entry.entry.delete(0, END)
            resolved_date_entry.entry.insert(0, datetime.now().strftime(DATE_FORMAT))
        if not resolved_time_entry.get().strip():
            resolved_time_entry.delete(0, END)
            resolved_time_entry.insert(0, datetime.now().strftime(TIME_FORMAT))
    else:
        resolved_date_entry.entry.delete(0, END)
        resolved_time_entry.delete(0, END)

def validate_email(email):
    if not email:
        return True
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
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
        app.after(0, lambda: messagebox.showwarning(
            "SMTP Warning", 
            "Email notifications are enabled, but SMTP settings are incomplete. Please check Email Settings."
        ))
        return

    email_type_lower = email_type.lower()
    if email_type_lower in ("registered", "open"):
        subject = f"Ticket Registered - {ticket_no}"
        body = f"""Dear {details['employee_name']},

Your IT Helpdesk ticket has been successfully registered.

Ticket Details:
---------------------------------------------
Ticket No:    {ticket_no}
Date Logged:  {details['log_date']} {details['call_time']}
Issue:        {details['issue']}
Priority:     {details['priority']}
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
Priority:     {details['priority']}
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
            if port_val == 465:
                server = smtplib.SMTP_SSL(smtp_host, port_val, timeout=10)
            else:
                server = smtplib.SMTP(smtp_host, port_val, timeout=10)
                if smtp_use_tls:
                    server.starttls()
            
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

            if email_type_lower in ("registered", "open"):
                if details.get("engineer_email"):
                    eng_msg = MIMEMultipart()
                    eng_msg["From"] = smtp_user
                    eng_msg["To"] = details["engineer_email"]
                    eng_msg["Subject"] = f"New Ticket Assigned - {ticket_no}"
                    eng_msg.attach(
                        MIMEText(
                            f"Ticket : {ticket_no}\nEmployee : {details['employee_name']}\nIssue : {details['issue']}",
                            "plain"
                        )
                    )
                    server.send_message(eng_msg)

            server.quit()

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO email_logs(
                    ticket_no,
                    recipient,
                    subject,
                    status,
                    sent_time
                )
                VALUES(?,?,?,?,?)
            """,
            (
                ticket_no,
                details['employee_email'],
                subject,
                "SUCCESS",
                datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}")
            ))
            conn.commit()
            conn.close()
        except Exception as ex:
            err_msg = str(ex)
            try:
                conn = get_connection()
                cur = conn.cursor()

                cur.execute("""
                INSERT INTO email_logs(
                ticket_no,
                recipient,
                subject,
                status,
                sent_time,
                error_message
            )
            VALUES(?,?,?,?,?,?)
            """,
            (
                ticket_no,
                details['employee_email'],
                subject,
                "FAILED",
                datetime.now().strftime(f"{DATE_FORMAT} {TIME_FORMAT}"),
                str(ex)
            ))

                conn.commit()
                conn.close()

            except:
                pass
            app.after(0, lambda: messagebox.showerror(
                "Email Error", 
                f"Failed to send email notification to {details['employee_email']}:\n{err_msg}"
            ))

    threading.Thread(target=run_send, daemon=True).start()

def open_settings_dialog():
    dialog = tb.Toplevel(app)
    dialog.title("Email Settings Configuration")
    dialog.geometry("500x520")
    dialog.resizable(False, False)
    dialog.grab_set() # Modal dialog

    # Load existing settings
    enabled_val = get_setting("email_enabled", "0")
    host_val = get_setting("smtp_host", "smtp.gmail.com")
    port_val = get_setting("smtp_port", "587")
    user_val = get_setting("smtp_user", "")
    pwd_val = get_setting("smtp_password", "")
    tls_val = get_setting("smtp_use_tls", "1")

    # Main container frame
    container = tb.Frame(dialog, padding=20)
    container.pack(fill=BOTH, expand=True)

    tb.Label(container, text="✉ EMAIL NOTIFICATION SETTINGS", font=("Segoe UI", 12, "bold"), foreground="#2563EB").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

    # Notification Toggle
    enabled_var = tb.StringVar(value=enabled_val)
    enabled_chk = tb.Checkbutton(container, text="Enable Email Notifications", variable=enabled_var, onvalue="1", offvalue="0", bootstyle="round-toggle")
    enabled_chk.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="w")

    # SMTP Host
    tb.Label(container, text="SMTP Host:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, pady=5, sticky="w")
    host_entry = tb.Entry(container, width=30)
    host_entry.insert(0, host_val)
    host_entry.grid(row=2, column=1, pady=5, sticky="ew")

    # SMTP Port
    tb.Label(container, text="SMTP Port:", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, pady=5, sticky="w")
    port_entry = tb.Entry(container, width=30)
    port_entry.insert(0, port_val)
    port_entry.grid(row=3, column=1, pady=5, sticky="ew")

    # Sender Email
    tb.Label(container, text="Sender Email:", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, pady=5, sticky="w")
    user_entry = tb.Entry(container, width=30)
    user_entry.insert(0, user_val)
    user_entry.grid(row=4, column=1, pady=5, sticky="ew")

    # Sender Password
    tb.Label(container, text="Sender Password:", font=("Segoe UI", 9, "bold")).grid(row=5, column=0, pady=5, sticky="w")
    pwd_entry = tb.Entry(container, width=30, show="*")
    pwd_entry.insert(0, pwd_val)
    pwd_entry.grid(row=5, column=1, pady=5, sticky="ew")

    # Use TLS Toggle
    tls_var = tb.StringVar(value=tls_val)
    tls_chk = tb.Checkbutton(container, text="Use TLS (recommended for 587)", variable=tls_var, onvalue="1", offvalue="0")
    tls_chk.grid(row=6, column=1, pady=5, sticky="w")

    # Separator
    tb.Separator(container, orient="horizontal").grid(row=7, column=0, columnspan=2, pady=15, sticky="ew")

    # Test Recipient
    tb.Label(container, text="Test Recipient Email:", font=("Segoe UI", 9, "bold")).grid(row=8, column=0, pady=5, sticky="w")
    test_to_entry = tb.Entry(container, width=30)
    test_to_entry.grid(row=8, column=1, pady=5, sticky="ew")

    # Test & Action buttons
    btn_container = tb.Frame(container)
    btn_container.grid(row=9, column=0, columnspan=2, pady=(15, 0), sticky="ew")

    def test_connection():
        host = host_entry.get().strip()
        port = port_entry.get().strip()
        user = user_entry.get().strip()
        pwd = pwd_entry.get()
        use_tls = tls_var.get() == "1"
        test_to = test_to_entry.get().strip()

        if not host or not port or not user or not pwd or not test_to:
            messagebox.showwarning("Warning", "Please fill in all SMTP fields and the Test Recipient Email.", parent=dialog)
            return

        if not validate_email(test_to):
            messagebox.showerror("Error", "Invalid Test Recipient Email format.", parent=dialog)
            return

        # Start testing thread
        def run_test():
            try:
                msg = MIMEMultipart()
                msg['From'] = user
                msg['To'] = test_to
                msg['Subject'] = "IT Helpdesk Call Logger - SMTP Test"
                msg.attach(MIMEText("This is a test email. Your SMTP configuration works!", 'plain'))

                port_num = int(port)
                if port_num == 465:
                    server = smtplib.SMTP_SSL(host, port_num, timeout=10)
                else:
                    server = smtplib.SMTP(host, port_num, timeout=10)
                    if use_tls:
                        server.starttls()

                server.login(user, pwd)
                server.send_message(msg)
                server.quit()
                app.after(0, lambda: messagebox.showinfo("Success", "SMTP Test Connection successful! Check your inbox.", parent=dialog))
            except Exception as ex:
                err_msg = str(ex)
                app.after(0, lambda: messagebox.showerror("Connection Failed", f"SMTP Connection failed:\n{err_msg}", parent=dialog))

        threading.Thread(target=run_test, daemon=True).start()

    def save_settings():
        host = host_entry.get().strip()
        port = port_entry.get().strip()
        user = user_entry.get().strip()
        pwd = pwd_entry.get()
        enabled = enabled_var.get()
        use_tls = tls_var.get()

        if enabled == "1" and (not host or not port or not user or not pwd):
            messagebox.showwarning("Warning", "If notifications are enabled, all SMTP fields must be filled.", parent=dialog)
            return

        set_setting("email_enabled", enabled)
        set_setting("smtp_host", host)
        set_setting("smtp_port", port)
        set_setting("smtp_user", user)
        set_setting("smtp_password", pwd)
        set_setting("smtp_use_tls", use_tls)

        messagebox.showinfo("Success", "Email Settings saved successfully.", parent=dialog)
        dialog.destroy()

    tb.Button(btn_container, text="⚡ TEST CONNECTION", bootstyle="warning-sm", command=test_connection).pack(side=LEFT, padx=5)
    tb.Button(btn_container, text="💾 SAVE", bootstyle="success-sm", command=save_settings).pack(side=RIGHT, padx=5)
    tb.Button(btn_container, text="❌ CANCEL", bootstyle="secondary-sm", command=dialog.destroy).pack(side=RIGHT, padx=5)

def update_dashboard():



    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*)
            FROM call_logs
            WHERE deleted = 0
            """)
        total = cur.fetchone()[0]

        cur.execute("""
        SELECT COUNT(*)
        FROM call_logs
        WHERE deleted = 0
        AND status IN ('Open', 'In Progress')
        """)
        open_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*)
            FROM call_logs
            WHERE deleted = 0 AND status='Resolved'
        """)
        resolved_count = cur.fetchone()[0]
    finally:
        conn.close()

    total_lbl.config(text=f"📋 TOTAL TICKETS: {total}")
    open_lbl.config(text=f"⚠ OPEN: {open_count}")
    resolved_lbl.config(text=f"✅ RESOLVED: {resolved_count}")

def load_data():

    tree.delete(*tree.get_children())

    search_text = search_entry.get().strip()
    status_filter = status_filter_combo.get()

    query = """
    SELECT
        ticket_no,
        employee_name,
        log_date,
        call_time,
        resolved_date,
        resolved_time,
        department,
        issue,
        issue_type,
        priority,
        status,
        engineer,
        remarks
    FROM call_logs
    WHERE deleted = 0
    """
    params = []

    if search_text:
        query += """
        AND (
            ticket_no LIKE ?
            OR employee_name LIKE ?
            OR engineer LIKE ?
            OR issue LIKE ?
            OR department LIKE ?
        )
        """
        like_str = f"%{search_text}%"
        params.extend([like_str, like_str, like_str, like_str, like_str])

    if status_filter and status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
    finally:
        conn.close()

    for row in rows:

        priority = row[9]
        status = row[10]

        tag = ""

        if priority == "Critical":
            tag = "Critical"

        elif priority == "High":
            tag = "High"

        elif status == "Open":
            tag = "Open"

        elif status == "Resolved":
            tag = "Resolved"

        tree.insert(
            "",
            END,
            values=row,
            tags=(tag,)
        )

    update_dashboard()

def edit_ticket():

    global selected_ticket

    selected = tree.selection()

    if not selected:

        messagebox.showwarning(
            "Warning",
            "Select a ticket first"
        )

        return

    ticket_no = tree.item(
        selected[0]
    )["values"][0]

    if load_ticket_to_form(ticket_no):
        messagebox.showinfo(
            "Edit Mode",
            f"Editing {selected_ticket}"
        )


def clear_form():
    global selected_ticket
    selected_ticket = None
    app.title("IT Helpdesk Call Logger")

    ticket_no_entry.config(state="normal")
    ticket_no_entry.delete(0, END)
    ticket_no_entry.insert(0, get_next_ticket())

    date_entry.entry.delete(0, END)
    date_entry.entry.insert(0, datetime.now().strftime(DATE_FORMAT))

    call_time_entry.delete(0, END)
    call_time_entry.insert(0, datetime.now().strftime(TIME_FORMAT))

    employee_entry.delete(0, END)
    engineer_entry.delete(0, END)

    issue_text.delete("1.0", END)
    remarks_text.delete("1.0", END)

    resolved_date_entry.entry.delete(0, END)
    resolved_time_entry.delete(0, END)
    employee_email_entry.delete(0, END)
    engineer_email_entry.delete(0, END)

    department_combo.current(0)

    issue_type_combo.current(0)
    status_combo.current(0)
    priority_combo.current(2)

    refresh_employee_list()


def validate_time_format(time_str):
    if not time_str:
        return True
    try:
        datetime.strptime(time_str, TIME_FORMAT)
        return True
    except ValueError:
        return False


def save_record():                                               

    ticket_no = ticket_no_entry.get().strip()
    if not ticket_no:
        messagebox.showwarning(
            "Warning",
            "Ticket Number cannot be empty"
        )
        return

    issue = issue_text.get(
        "1.0",
        "end-1c"
    )

    remarks = remarks_text.get(
        "1.0",
        "end-1c"
    )

    call_time = call_time_entry.get().strip()

    resolved_date = resolved_date_entry.entry.get().strip()
    resolved_time = resolved_time_entry.get().strip()
    status = status_combo.get()

    # Auto-adjust status if resolved date/time are populated manually
    if (resolved_date or resolved_time) and status not in ("Resolved", "Closed"):
        status = "Resolved"
        status_combo.set("Resolved")

    # Auto-populate resolved date and time if status is set to Resolved/Closed
    if status in ("Resolved", "Closed"):
        if not resolved_date:
            resolved_date = datetime.now().strftime(DATE_FORMAT)
            resolved_date_entry.entry.delete(0, END)
            resolved_date_entry.entry.insert(0, resolved_date)
        if not resolved_time:
            resolved_time = datetime.now().strftime(TIME_FORMAT)
            resolved_time_entry.delete(0, END)
            resolved_time_entry.insert(0, resolved_time)
    else:
        resolved_date = ""
        resolved_time = ""
        resolved_date_entry.entry.delete(0, END)
        resolved_time_entry.delete(0, END)

    # Validate time formats
    if not validate_time_format(call_time):
        messagebox.showerror(
            "Invalid Time",
            "Call Time must be in 12-hour format with AM/PM (e.g. 09:30 AM)."
        )
        return

    if resolved_time and not validate_time_format(resolved_time):
        messagebox.showerror(
            "Invalid Time",
            "Resolved Time must be in 12-hour format with AM/PM (e.g. 05:45 PM)."
        )
        return

    # Validate date formats
    log_date_str = date_entry.entry.get().strip()
    try:
        datetime.strptime(log_date_str, DATE_FORMAT)
    except ValueError:
        messagebox.showerror(
            "Invalid Date",
            "Date must be in the format DD-MM-YYYY (e.g. 25-12-2026)."
        )
        return

    if resolved_date:
        try:
            datetime.strptime(resolved_date, DATE_FORMAT)
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Resolved Date must be in the format DD-MM-YYYY (e.g. 25-12-2026)."
            )
            return

    if not employee_entry.get().strip():

        messagebox.showwarning(
            "Warning",
            "Employee Name cannot be empty"
        )
        return

    employee_email = employee_email_entry.get().strip()
    engineer_email = engineer_email_entry.get().strip()
    if employee_email and not validate_email(employee_email):
        messagebox.showerror(
            "Invalid Email",
            "Employee Email must be a valid email address (e.g. employee@company.com)."
        )
        return

    if engineer_email and not validate_email(engineer_email):
        messagebox.showerror(
            "Invalid Email",
            "Engineer Email must be a valid email address (e.g. engineer@company.com)."
        )
        return

    if not engineer_entry.get().strip():

        messagebox.showwarning(
            "Warning",
            "Engineer cannot be empty"
        )
        return

    if not issue.strip():

        messagebox.showwarning(
            "Warning",
            "Issue cannot be empty"
        )
        return

    conn = get_connection()
    try:
        cur = conn.cursor()

        global selected_ticket

        prev_status = None
        if selected_ticket:
            cur.execute("SELECT status FROM call_logs WHERE ticket_no = ?", (selected_ticket,))
            prev_row = cur.fetchone()
            if prev_row:
                prev_status = prev_row[0]

        # EDIT EXISTING TICKET
        if selected_ticket:

            cur.execute("""
            UPDATE call_logs
            SET
                log_date=?,
                call_time=?,
                employee_name=?,
                employee_email=?,
                department=?,
                issue_type=?,
                issue=?,
                priority=?,
                status=?,
                remarks=?,
                engineer=?,
                resolved_date=?,
                resolved_time=?,
                engineer_email=?
            WHERE ticket_no=?
            """,
            (
                date_entry.entry.get(),
                call_time,
                employee_entry.get(),
                employee_email,
                department_combo.get(),
                issue_type_combo.get(),
                issue,
                priority_combo.get(),
                status_combo.get(),
                remarks,
                engineer_entry.get(),
                resolved_date,
                resolved_time,
                engineer_email,
                selected_ticket
            ))

        # NEW TICKET
        else:

            cur.execute("""
            INSERT INTO call_logs
            (
                ticket_no,
                log_date,
                call_time,
                employee_name,
                employee_email,
                department,
                issue_type,
                issue,
                priority,
                status,
                remarks,
                engineer,
                resolved_date,
                resolved_time,
                engineer_email,
                resolved_email_sent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_no,
                date_entry.entry.get(),
                call_time,
                employee_entry.get(),
                employee_email,
                department_combo.get(),
                issue_type_combo.get(),
                issue,
                priority_combo.get(),
                status_combo.get(),
                remarks,
                engineer_entry.get(),
                resolved_date,
                resolved_time,
                engineer_email,
                1 if status in ("Resolved", "Closed") else 0
            ))

        # Upsert employee details to employees table
        emp_name = employee_entry.get().strip()
        if emp_name:
            cur.execute("SELECT id FROM employees WHERE name = ?", (emp_name,))
            emp_row = cur.fetchone()
            if emp_row:
                cur.execute("""
                    UPDATE employees
                    SET email = ?, department = ?
                    WHERE id = ?
                """, (employee_email, department_combo.get(), emp_row[0]))
            else:
                cur.execute("""
                    INSERT INTO employees (name, email, department)
                    VALUES (?, ?, ?)
                """, (emp_name, employee_email, department_combo.get()))

        conn.commit()

        # Trigger email notification asynchronously
        email_details = {
            "employee_name": employee_entry.get().strip(),
            "engineer_email": engineer_email,
            "employee_email": employee_email,
            "log_date": date_entry.entry.get().strip(),
            "call_time": call_time,
            "issue": issue,
            "priority": priority_combo.get(),
            "status": status,
            "resolved_date": resolved_date,
            "resolved_time": resolved_time,
            "engineer": engineer_entry.get().strip(),
            "remarks": remarks
        }

        if selected_ticket:
            # Send status notification if status changed to Resolved or Closed
            if status != prev_status:
                if status == "Resolved":
                    cur.execute("""
                    SELECT resolved_email_sent
                    FROM call_logs
                    WHERE ticket_no=?
                    """, (selected_ticket,))
                    row = cur.fetchone()
                    if row and row[0] == 0:
                        trigger_ticket_email(
                            selected_ticket,
                            status,
                            email_details
                        )
                        cur.execute("""
                        UPDATE call_logs
                        SET resolved_email_sent=1
                        WHERE ticket_no=?
                        """, (selected_ticket,))
                elif status == "Closed":
                    trigger_ticket_email(
                        selected_ticket,
                        status,
                        email_details
                    )
        else:
            # Always send status notification for a new ticket
            trigger_ticket_email(ticket_no, status, email_details)

    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            messagebox.showerror(
                "Database Error",
                "Ticket Number already exists! Please enter a unique Ticket Number."
            )
        else:
            messagebox.showerror(
                "Database Error",
                str(e)
            )
        return
    finally:
        conn.close()

    clear_form()

    load_data()

    messagebox.showinfo(
        "Success",
        "Ticket Saved Successfully"
    )

            
def delete_record():

    selected = tree.selection()

    if not selected:
        messagebox.showwarning(
            "Warning",
            "Select a ticket first"
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Delete selected ticket?"
    )

    if not confirm:
        return

    ticket = tree.item(
        selected[0]
    )["values"][0]

    conn = get_connection()
    try:
        cur = conn.cursor()

        # Fetch ticket details for the history report
        cur.execute("""
        SELECT
            ticket_no, log_date, call_time, employee_name, department,
            issue_type, issue, priority, status, remarks, engineer,
            resolved_date, resolved_time, employee_email
        FROM call_logs
        WHERE ticket_no = ?
        """, (ticket,))
        row = cur.fetchone()

        if row:
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

            # Load existing history if present, and append
            if os.path.exists(file_path):
                try:
                    existing_df = pd.read_excel(file_path)
                    df = pd.concat([existing_df, pd.DataFrame(ticket_data)], ignore_index=True)
                except Exception as ex:
                    messagebox.showerror(
                        "History Read Error",
                        f"Could not read the deleted history file: {str(ex)}\nTo prevent data loss, the delete operation has been cancelled."
                    )
                    return
            else:
                df = pd.DataFrame(ticket_data)

            try:
                df.to_excel(file_path, index=False)
            except PermissionError:
                messagebox.showerror(
                    "File Locked",
                    "Could not save deleted ticket because 'deleted_history.xlsx' is currently open in another program (like Excel). Please close the file and try deleting again."
                )
                return

        cur.execute(
            """
            UPDATE call_logs
            SET deleted = 1
            WHERE ticket_no = ?
            """,
            (ticket,)
        )

        conn.commit()

    except Exception as e:
        messagebox.showerror(
            "Database Error",
            str(e)
        )
        return
    finally:
        conn.close()

    load_data()

    # If we deleted the ticket currently loaded/being edited, clear the form
    global selected_ticket
    if selected_ticket == ticket:
        clear_form()

    messagebox.showinfo(
        "Success",
        f"{ticket} deleted successfully."
    )

def export_excel():

    try:

        os.makedirs(
            "exports",
            exist_ok=True
        )

        filename = datetime.now().strftime(
            "exports/call_logs_%Y%m%d_%H%M%S.xlsx"
        )

        conn = get_connection()
        try:
            df = pd.read_sql_query(
                """
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
                """,
                conn
            )
        finally:
            conn.close()

        df.to_excel(
            filename,
            index=False
        )

        messagebox.showinfo(
            "Success",
            f"Exported:\n{filename}"
        )

    except Exception as e:
        if isinstance(e, PermissionError) or "Permission denied" in str(e):
            messagebox.showerror(
                "Export Error",
                "Could not export call logs because the target file is locked or open in another program (like Excel). Please close Excel and try again."
            )
        else:
            messagebox.showerror(
                "Export Error",
                str(e)
            )

# ==========================
# EVENTS
# ==========================

app.bind(
    "<Return>",
    lambda e: save_record()
)

employee_entry.bind("<KeyRelease>", on_employee_keyrelease)
employee_entry.bind("<<ComboboxSelected>>", on_employee_select)
employee_entry.bind("<FocusOut>", on_employee_focus_out)
status_combo.bind("<<ComboboxSelected>>", on_status_change)

# ==========================
# BUTTONS
# ==========================

btn_frame = tb.Frame(form)

btn_frame.grid(
    row=0,
    column=6,
    rowspan=5,
    padx=15,
    pady=5,
    sticky="ns"
)

tb.Button(
    btn_frame,
    text="💾 SAVE TICKET",
    bootstyle="success-sm",
    command=save_record,
).pack(fill=X, pady=2)

tb.Button(
    btn_frame,
    text="🗑 DELETE TICKET",
    bootstyle="danger-sm",
    command=delete_record
).pack(fill=X, pady=2)

tb.Button(
    btn_frame,
    text="✏ EDIT TICKET",
    bootstyle="warning-sm",
    command=edit_ticket
).pack(fill=X, pady=2)

tb.Button(
    btn_frame,
    text="📊 EXPORT EXCEL",
    bootstyle="info-sm",
    command=export_excel
).pack(fill=X, pady=2)

tb.Button(
    btn_frame,
    text="🧹 CLEAR FORM",
    bootstyle="secondary-sm",
    command=clear_form
).pack(fill=X, pady=2)

tb.Button(
    btn_frame,
    text="⚙ EMAIL SETTINGS",
    bootstyle="dark-sm",
    command=open_settings_dialog
).pack(fill=X, pady=2)


# ==========================
# START
# ==========================

clear_form()
load_data()

app.mainloop()