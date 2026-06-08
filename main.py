import ttkbootstrap as tb
import shutil
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from datetime import datetime
import pandas as pd
import os
from database import *
BACKUP_DIR = "backup"


def backup_database():

    os.makedirs(BACKUP_DIR, exist_ok=True)

    if os.path.exists(DB_PATH):

        backup_name = datetime.now().strftime(
            "helpdesk_%Y%m%d_%H%M%S.db"
        )

        shutil.copy2(
            DB_PATH,
            os.path.join(BACKUP_DIR, backup_name)
        )

backup_database()        
init_db()
# ==========================
# WINDOW
# ==========================
app = tb.Window(themename="litera")
app.title("IT Helpdesk Call Logger")
app.geometry("1500x850")

app.configure(bg="#1E293B")

# ==========================
# TITLE
# ==========================

title = tb.Label(
    app,
    text="🖥 IT HELPDESK CALL LOGGER",
    font=("Segoe UI", 24, "bold"),
    foreground="#38BDF8"
)
title.pack(pady=10)

# ==========================
# DASHBOARD
# ==========================

dashboard = tb.Frame(app)
dashboard.pack(fill=X, padx=10)

total_lbl = tb.Label(
    dashboard,
    text="Total Tickets: 0",
    font=("Segoe UI", 11, "bold")
)

total_lbl.pack(side=LEFT, padx=20)

open_lbl = tb.Label(
    dashboard,
    text="Open: 0",
    font=("Segoe UI", 11, "bold")
)

open_lbl.pack(side=LEFT, padx=20)

resolved_lbl = tb.Label(
    dashboard,
    text="Resolved: 0",
    font=("Segoe UI", 11, "bold")
)

resolved_lbl.pack(side=LEFT, padx=20)

# ==========================
# FORM
# ==========================

form = tb.LabelFrame(
    app,
    text="New Ticket"
)

form.pack(
    fill="x",
    padx=10,
    pady=5
)

form.pack(fill=X, padx=10, pady=10)

for i in range(6):
    form.grid_columnconfigure(
        i,
        weight=1
    )

# Date

tb.Label(
    form,
    text="Date"
).grid(row=0, column=0, padx=5, pady=5)

date_entry = tb.Entry(form, width=15)
date_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=10,
    sticky="w"
)

date_entry.insert(
    0,
    datetime.now().strftime("%d-%m-%Y")
)

tb.Label(
    form,
    text="Call Time"
).grid(row=0, column=2)

call_time_entry = tb.Entry(
    form,
    width=15
)

call_time_entry.grid(
    row=0,
    column=3,
    padx=10,
    pady=10,
    sticky="w"
)

call_time_entry.insert(
    0,
    datetime.now().strftime("%I:%M %p")
)
# Priority

tb.Label(
    form,
    text="Priority"
).grid(row=0, column=2)

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
    row=0,
    column=3,
    padx=10,
    pady=10,
    sticky="w"
)
priority_combo.current(2)

# Status

tb.Label(
    form,
    text="Status"
).grid(row=0, column=4)

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
    row=0,
    column=5,
    padx=10,
    pady=10,
    sticky="w"
)
status_combo.current(0)

# Engineer
tb.Label(
    form,
    text="Department"
).grid(row=1, column=2)

department_combo = ttk.Combobox(
    form,
    values=[
        "sourcing",
        "HR",
        "accounts",
        "Sales",
        "IT",
    ],
    state="readonly",
    width=20
)

department_combo.grid(
    row=1,
    column=3,
    padx=10,
    pady=10,
    sticky="w"
)

department_combo.current(0)

tb.Label(
    form,
    text="Resolved Date"
).grid(row=2, column=4)

resolved_date_entry = tb.Entry(
    form,
    width=15
)

resolved_date_entry.grid(
    row=2,
    column=5,
    padx=10,
    pady=10,
    sticky="w"
)

tb.Label(
    form,
    text="Resolved Time"
).grid(row=3, column=4)

resolved_time_entry = tb.Entry(
    form,
    width=15
)

resolved_time_entry.grid(
    row=3,
    column=5,
    padx=10,
    pady=10,
    sticky="w"
)

# Employee

tb.Label(
    form,
    text="Employee"
).grid(row=1, column=0)

employee_entry = tb.Entry(
    form,
    width=40
)

employee_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=10,
    sticky="ew"
)

tb.Label(
    form,
    text="Engineer"
).grid(row=2, column=0)

engineer_entry = tb.Entry(
    form,
    width=40
)

engineer_entry.grid(
    row=2,
    column=1,
    padx=10,
    pady=10,
    sticky="ew"
)

# Issue Type

tb.Label(
    form,
    text="Issue Type"
).grid(
    row=2,
    column=2,
    padx=5,
    pady=5,
    sticky="e"
)

issue_type_combo = ttk.Combobox(
    form,
    values=[
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
    ],
    state="readonly",
    width=30
)

issue_type_combo.grid(
    row=2,
    column=3,
    padx=10,
    pady=10,
    sticky="w"
)

issue_type_combo.current(0)
# Issue

tb.Label(
    form,
    text="Issue"
).grid(
    row=3,
    column=0,
    padx=5,
    pady=5
)

issue_text = tb.Text(
    form,
    height=3,
    width=80
)

issue_text.grid(
    row=3,
    column=1,
    columnspan=2,
    padx=10,
    pady=10,
    sticky="ew"
)

# Remarks

tb.Label(
    form,
    text="Remarks"
).grid(row=3, column=3, padx=5, pady=5)

remarks_text = tb.Text(
    form,
    height=2,
    width=80
)

remarks_text.grid(
    row=3,
    column=4,
    columnspan=2,
    padx=10,
    pady=10,
    sticky="ew"
)

search_frame = tb.Frame(app)
search_frame.pack(fill=X,padx=10)

search_entry = tb.Entry(
    search_frame,
    width=50
)

search_entry.pack(
    side=LEFT,
    padx=5
)

tb.Button(
    search_frame,
    text="Search",
    command=lambda: load_data(
        search_entry.get()
    )
).pack(side=LEFT)

selected_ticket = None

def load_selected_ticket(event):

    global selected_ticket

    selected = tree.selection()

    if not selected:
        return

    ticket_no = tree.item(
        selected[0]
    )["values"][0]

    conn = get_connection()
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
        engineer,
        remarks,
        resolved_date,
        resolved_time
    FROM call_logs
    WHERE ticket_no = ?
    """,
    (ticket_no,))

    row = cur.fetchone()

    conn.close()

    if not row:
        return

    selected_ticket = row[0]

    # Date

    date_entry.delete(0, END)
    date_entry.insert(0, row[1])

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

    # Engineer

    engineer_entry.delete(0, END)
    engineer_entry.insert(0, row[9])

    # Remarks

    remarks_text.delete("1.0", END)
    remarks_text.insert("1.0", row[10])

    # Resolved Date

    resolved_date_entry.delete(0, END)

    if row[11]:
        resolved_date_entry.insert(0, row[11])

    # Resolved Time

    resolved_time_entry.delete(0, END)

    if row[12]:
        resolved_time_entry.insert(0, row[12])

    app.title(
        f"Editing Ticket : {selected_ticket}"
    )
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
    "Date",
    "Time",
    "Employee",
    "Department",
    "Issue Type",
    "Issue",
    "Priority",
    "Status",
    "Engineer",
    "Remarks",
    "Resolved Date",
    "Resolved Time"
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
tree.column("Date", width=120)
tree.column("Time", width=120)
tree.column("Employee", width=120)
tree.column("Department", width=120)
tree.column("Issue Type", width=130)
tree.column("Issue", width=200)
tree.column("Priority", width=90)
tree.column("Status", width=100)
tree.column("Engineer", width=100)
tree.column("Remarks", width=200)
tree.column("Resolved Date", width=120)
tree.column("Resolved Time", width=120)

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
    background="#ffcccc"
)

tree.tag_configure(
    "High",
    background="#fff2cc"
)

tree.tag_configure(
    "Open",
    background="#cce5ff"
)

tree.tag_configure(
    "Resolved",
    background="#d4edda"
)

style = ttk.Style()

style.configure(
    "Treeview",
    font=("Segoe UI", 10),
    rowheight=28
)

style.configure(
    "Treeview.Heading",
    font=("Segoe UI", 11, "bold")
)

style.map(
    "Treeview",
    background=[("selected", "#2563EB")],
    foreground=[("selected", "white")]
)
# ==========================
# FUNCTIONS
# ==========================
def update_dashboard():

    conn = get_connection()
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
    AND status='Open'
    """)
    open_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*)
        FROM call_logs
        WHERE deleted = 0 AND status='Resolved'
    """)
    resolved_count = cur.fetchone()[0]

    conn.close()

    total_lbl.config(text=f"📋 Total: {total}")
    open_lbl.config(text=f"⚠ Open: {open_count}")
    resolved_lbl.config(text=f"✅ Resolved: {resolved_count}")

def load_data(search_text=""):

    tree.delete(*tree.get_children())

    conn = get_connection()
    cur = conn.cursor()

    if search_text:

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
            engineer,
            remarks,
            resolved_date,
            resolved_time
        FROM call_logs
        WHERE deleted = 0
        AND (
            ticket_no LIKE ?
            OR employee_name LIKE ?
            OR engineer LIKE ?
            OR issue LIKE ?
            OR department LIKE ?
        )
        """,
        (
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%",
            f"%{search_text}%"
        ))

    else:

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
            engineer,
            remarks,
            resolved_date,
            resolved_time
        FROM call_logs
        WHERE deleted = 0
        ORDER BY id DESC
        """)

    rows = cur.fetchall()

    for row in rows:

        priority = row[7]
        status = row[8]

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

    conn.close()

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

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT *
    FROM call_logs
    WHERE ticket_no = ?
    """,
    (ticket_no,))

    row = cur.fetchone()

    conn.close()

    if not row:
        return

    selected_ticket = row[1]

    date_entry.delete(0, END)
    date_entry.insert(0, row[2])

    call_time_entry.delete(0, END)
    call_time_entry.insert(0, row[3])

    employee_entry.delete(0, END)
    employee_entry.insert(0, row[4])

    department_combo.set(row[5])

    issue_type_combo.set(row[6])

    issue_text.delete("1.0", END)
    issue_text.insert("1.0", row[7])

    priority_combo.set(row[8])

    status_combo.set(row[9])

    remarks_text.delete("1.0", END)
    remarks_text.insert("1.0", row[10])

    engineer_entry.delete(0, END)
    engineer_entry.insert(0, row[11])

    resolved_date_entry.delete(0, END)

    if row[12]:
        resolved_date_entry.insert(0, row[12])

    resolved_time_entry.delete(0, END)

    if row[13]:
        resolved_time_entry.insert(0, row[13])

    messagebox.showinfo(
        "Edit Mode",
        f"Editing {selected_ticket}"
    )


def save_record():

    issue = issue_text.get(
        "1.0",
        "end-1c"
    )

    remarks = remarks_text.get(
        "1.0",
        "end-1c"
    )

    call_time = call_time_entry.get().strip()

    resolved_date = resolved_date_entry.get().strip()
    resolved_time = resolved_time_entry.get().strip()

    if not employee_entry.get().strip():

        messagebox.showwarning(
            "Warning",
            "Employee Name cannot be empty"
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

    try:

        conn = get_connection()
        cur = conn.cursor()

        global selected_ticket

        # EDIT EXISTING TICKET
        if selected_ticket:

            cur.execute("""
            UPDATE call_logs
            SET
                log_date=?,
                call_time=?,
                employee_name=?,
                department=?,
                issue_type=?,
                issue=?,
                priority=?,
                status=?,
                remarks=?,
                engineer=?,
                resolved_date=?,
                resolved_time=?
            WHERE ticket_no=?
            """,
            (
                date_entry.get(),
                call_time,
                employee_entry.get(),
                department_combo.get(),
                issue_type_combo.get(),
                issue,
                priority_combo.get(),
                status_combo.get(),
                remarks,
                engineer_entry.get(),
                resolved_date,
                resolved_time,
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
                department,
                issue_type,
                issue,
                priority,
                status,
                remarks,
                engineer,
                resolved_date,
                resolved_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                get_next_ticket(),
                date_entry.get(),
                call_time,
                employee_entry.get(),
                department_combo.get(),
                issue_type_combo.get(),
                issue,
                priority_combo.get(),
                status_combo.get(),
                remarks,
                engineer_entry.get(),
                resolved_date,
                resolved_time
            ))

        conn.commit()
        conn.close()

        selected_ticket = None

        app.title(
            "IT Helpdesk Call Logger"
        )

        employee_entry.delete(0, END)
        engineer_entry.delete(0, END)

        issue_text.delete(
            "1.0",
            END
        )

        remarks_text.delete(
            "1.0",
            END
        )

        resolved_date_entry.delete(
            0,
            END
        )

        resolved_time_entry.delete(
            0,
            END
        )

        department_combo.current(0)
        issue_type_combo.current(0)
        status_combo.current(0)
        priority_combo.current(2)

        load_data()

        messagebox.showinfo(
            "Success",
            "Ticket Saved Successfully"
        )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
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

    try:

        ticket = tree.item(
            selected[0]
        )["values"][0]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
        """
        UPDATE call_logs
        SET deleted = 1
        WHERE ticket_no = ?
        """,
        (ticket,)
    )

        conn.commit()
        conn.close()

        load_data()

        messagebox.showinfo(
            "Success",
            f"{ticket} deleted successfully"
        )

    except Exception as e:

        messagebox.showerror(
            "Database Error",
            str(e)
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

        df = pd.read_sql_query(
            """
            SELECT *
            FROM call_logs
            WHERE deleted = 0
            """,
            conn
        )

        df.to_excel(
            filename,
            index=False
        )

        conn.close()

        messagebox.showinfo(
            "Success",
            f"Exported:\n{filename}"
        )

    except Exception as e:

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

# ==========================
# BUTTONS
# ==========================

btn_frame = tb.Frame(form)

btn_frame.grid(
    row=5,
    column=1,
    columnspan=3,
    sticky="w",
    pady=10
)

tb.Button(
    btn_frame,
    text="💾 Save Ticket",
    bootstyle="success-outline",
    command=save_record,
).pack(side=LEFT, padx=5)

tb.Button(
    btn_frame,
    text="🗑 Delete Ticket",
    bootstyle="danger-outline",
    command=delete_record
).pack(side=LEFT, padx=5)

tb.Button(
    btn_frame,
    text="✏ Edit Ticket",
    bootstyle="warning-outline",
    command=edit_ticket
).pack(side=LEFT, padx=5)

tb.Button(
    btn_frame,
    text="📊 Export Excel",
    bootstyle="info-outline",
    command=export_excel
).pack(side=LEFT, padx=5)


# ==========================
# START
# ==========================

load_data()

app.mainloop()