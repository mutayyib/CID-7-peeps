import sqlite3

conn = sqlite3.connect("ems_full.db")  # Connects to your database in the same folder
c = conn.cursor()

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import date

# ---------------- Database Setup ----------------
conn = sqlite3.connect("ems_full.db")
c = conn.cursor()

# Users table
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'employee'
)""")

# Employees table
c.execute("""CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    department TEXT,
    branch_id INTEGER,
    position TEXT,
    salary REAL,
    hire_date TEXT
)""")

# Attendance table
c.execute("""CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date TEXT,
    status TEXT DEFAULT 'Present'
)""")

# Leaves table
c.execute("""CREATE TABLE IF NOT EXISTS leaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    leave_type TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT DEFAULT 'Pending',
    reason TEXT
)""")

# Performance table
c.execute("""CREATE TABLE IF NOT EXISTS performance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    review_date TEXT,
    rating INTEGER,
    comments TEXT
)""")

# Departments table
c.execute("""CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    manager TEXT
)""")

# Branches table
c.execute("""CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    location TEXT,
    manager TEXT
)""")

# Default admin user
c.execute("SELECT * FROM users WHERE email='admin@ems.com'")
if not c.fetchone():
    c.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
              ('Admin', 'admin@ems.com', 'admin', 'admin'))
conn.commit()


# ---------------- Main Application ----------------
class EMS:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System")
        self.root.geometry("1000x600")
        self.BG = "#f0f2f5"
        self.PRIMARY = "#667eea"
        self.session_user = None

        self.frames = {}
        self.create_frames()
        self.show_frame("home")

    # ---------------- Frames ----------------
    def create_frames(self):
        for name in ["home", "login", "employees", "attendance", "leaves", "performance", "departments", "branches",
                     "payroll"]:
            frame = tk.Frame(self.root, bg=self.BG)
            frame.pack(fill="both", expand=True)
            self.frames[name] = frame
        self.create_home()
        self.create_login()
        self.create_employees()
        self.create_attendance()
        self.create_leaves()
        self.create_performance()
        self.create_departments()
        self.create_branches()
        self.create_payroll()

    def show_frame(self, name):
        for f in self.frames.values():
            f.place_forget()
        self.frames[name].place(x=0, y=0, relwidth=1, relheight=1)

    # ---------------- Home ----------------
    def create_home(self):
        home = self.frames["home"]
        tk.Label(home, text="Employee Management System", font=("Segoe UI", 20, "bold"), fg=self.PRIMARY,
                 bg=self.BG).pack(pady=20)
        buttons = [
            ("Login", "login"),
            ("Employees", "employees"),
            ("Attendance", "attendance"),
            ("Leaves", "leaves"),
            ("Performance", "performance"),
            ("Departments", "departments"),
            ("Branches", "branches"),
            ("Payroll", "payroll")
        ]
        for text, frame in buttons:
            tk.Button(home, text=text, width=20, font=("Segoe UI", 12, "bold"),
                      command=lambda f=frame: self.show_frame(f), bg=self.PRIMARY, fg="white").pack(pady=5)

    # ---------------- Login ----------------
    def create_login(self):
        login = self.frames["login"]
        tk.Label(login, text="Login", font=("Segoe UI", 16, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=10)
        self.email_var = tk.StringVar()
        self.pw_var = tk.StringVar()
        tk.Entry(login, textvariable=self.email_var, width=30).pack(pady=5)
        tk.Entry(login, textvariable=self.pw_var, width=30, show="•").pack(pady=5)
        tk.Button(login, text="Login", bg=self.PRIMARY, fg="white", width=15, command=self.do_login).pack(pady=5)
        tk.Button(login, text="Back", command=lambda: self.show_frame("home")).pack(pady=5)

    def do_login(self):
        email = self.email_var.get().strip()
        pw = self.pw_var.get().strip()
        if not email or not pw:
            messagebox.showerror("Error", "Enter credentials")
            return
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, pw))
        user = c.fetchone()
        if user:
            self.session_user = user
            messagebox.showinfo("Success", "Login successful")
            self.show_frame("home")
        else:
            messagebox.showerror("Error", "Invalid credentials")

    # ---------------- Employees ----------------
    def create_employees(self):
        frame = self.frames["employees"]
        tk.Label(frame, text="Employees", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.emp_tree = ttk.Treeview(frame,
                                     columns=("ID", "Name", "Email", "Phone", "Dept", "Branch", "Position", "Salary",
                                              "Hire"), show="headings")
        for col in self.emp_tree["columns"]:
            self.emp_tree.heading(col, text=col)
            self.emp_tree.column(col, width=100)
        self.emp_tree.pack(fill="both", expand=True, pady=5)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_employees).pack(pady=2)
        tk.Button(frame, text="Add Employee", command=self.add_employee).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_employees()

    def load_employees(self):
        for row in self.emp_tree.get_children():
            self.emp_tree.delete(row)
        c.execute("""SELECT e.id,e.name,e.email,e.phone,e.department,b.name,e.position,e.salary,e.hire_date 
                     FROM employees e LEFT JOIN branches b ON e.branch_id=b.id ORDER BY e.id DESC""")
        rows = c.fetchall()
        for r in rows:
            self.emp_tree.insert("", "end", values=r)

    def add_employee(self):
        fields = ["Name", "Email", "Phone", "Department", "Branch ID", "Position", "Salary", "Hire Date YYYY-MM-DD"]
        vals = [simpledialog.askstring("Input", f) for f in fields]
        if not all(vals): return
        try:
            c.execute("""INSERT INTO employees (name,email,phone,department,branch_id,position,salary,hire_date)
                         VALUES (?,?,?,?,?,?,?,?)""",
                      (vals[0], vals[1], vals[2], vals[3], int(vals[4]), vals[5], float(vals[6]), vals[7]))
            conn.commit()
            messagebox.showinfo("Success", "Employee added")
            self.load_employees()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- Attendance ----------------
    def create_attendance(self):
        frame = self.frames["attendance"]
        tk.Label(frame, text="Attendance", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.att_tree = ttk.Treeview(frame, columns=("ID", "Employee", "Date", "Status"), show="headings")
        for col in self.att_tree["columns"]:
            self.att_tree.heading(col, text=col)
            self.att_tree.column(col, width=150)
        self.att_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_attendance).pack(pady=2)
        tk.Button(frame, text="Mark Attendance", command=self.mark_attendance).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_attendance()

    def load_attendance(self):
        for row in self.att_tree.get_children():
            self.att_tree.delete(row)
        c.execute("""SELECT a.id,e.name,a.date,a.status FROM attendance a 
                     JOIN employees e ON a.employee_id=e.id ORDER BY a.date DESC""")
        rows = c.fetchall()
        for r in rows:
            self.att_tree.insert("", "end", values=r)

    def mark_attendance(self):
        eid = simpledialog.askinteger("Input", "Employee ID")
        status = simpledialog.askstring("Input", "Status (Present/Absent/Leave)")
        if not eid or not status: return
        c.execute("INSERT INTO attendance (employee_id,date,status) VALUES (?,?,?)", (eid, str(date.today()), status))
        conn.commit()
        messagebox.showinfo("Success", "Attendance marked")
        self.load_attendance()

    # ---------------- Leaves ----------------
    def create_leaves(self):
        frame = self.frames["leaves"]
        tk.Label(frame, text="Leaves", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.leave_tree = ttk.Treeview(frame, columns=("ID", "Employee", "Type", "Start", "End", "Status"),
                                       show="headings")
        for col in self.leave_tree["columns"]:
            self.leave_tree.heading(col, text=col)
            self.leave_tree.column(col, width=150)
        self.leave_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_leaves).pack(pady=2)
        tk.Button(frame, text="Apply Leave", command=self.apply_leave).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_leaves()

    def load_leaves(self):
        for row in self.leave_tree.get_children():
            self.leave_tree.delete(row)
        c.execute("""SELECT l.id,e.name,l.leave_type,l.start_date,l.end_date,l.status FROM leaves l 
                     JOIN employees e ON l.employee_id=e.id ORDER BY l.id DESC""")
        rows = c.fetchall()
        for r in rows:
            self.leave_tree.insert("", "end", values=r)

    def apply_leave(self):
        eid = simpledialog.askinteger("Input", "Employee ID")
        ltype = simpledialog.askstring("Input", "Leave Type")
        sdate = simpledialog.askstring("Input", "Start Date YYYY-MM-DD")
        edate = simpledialog.askstring("Input", "End Date YYYY-MM-DD")
        reason = simpledialog.askstring("Input", "Reason")
        if not eid or not ltype or not sdate or not edate: return
        c.execute("""INSERT INTO leaves (employee_id,leave_type,start_date,end_date,reason)
                     VALUES (?,?,?,?,?)""", (eid, ltype, sdate, edate, reason))
        conn.commit()
        messagebox.showinfo("Success", "Leave applied")
        self.load_leaves()

    # ---------------- Performance ----------------
    def create_performance(self):
        frame = self.frames["performance"]
        tk.Label(frame, text="Performance", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.perf_tree = ttk.Treeview(frame, columns=("ID", "Employee", "Date", "Rating", "Comments"), show="headings")
        for col in self.perf_tree["columns"]:
            self.perf_tree.heading(col, text=col)
            self.perf_tree.column(col, width=150)
        self.perf_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_performance).pack(pady=2)
        tk.Button(frame, text="Add Performance", command=self.add_performance).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_performance()

    def load_performance(self):
        for row in self.perf_tree.get_children():
            self.perf_tree.delete(row)
        c.execute("""SELECT p.id,e.name,p.review_date,p.rating,p.comments FROM performance p
                     JOIN employees e ON p.employee_id=e.id ORDER BY p.id DESC""")
        rows = c.fetchall()
        for r in rows:
            self.perf_tree.insert("", "end", values=r)

    def add_performance(self):
        eid = simpledialog.askinteger("Input", "Employee ID")
        rating = simpledialog.askinteger("Input", "Rating 1-5")
        comments = simpledialog.askstring("Input", "Comments")
        if not eid or not rating: return
        c.execute("""INSERT INTO performance (employee_id,review_date,rating,comments)
                     VALUES (?,?,?,?)""", (eid, str(date.today()), rating, comments))
        conn.commit()
        messagebox.showinfo("Success", "Performance added")
        self.load_performance()

    # ---------------- Departments ----------------
    def create_departments(self):
        frame = self.frames["departments"]
        tk.Label(frame, text="Departments", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.dept_tree = ttk.Treeview(frame, columns=("ID", "Name", "Manager"), show="headings")
        for col in self.dept_tree["columns"]:
            self.dept_tree.heading(col, text=col)
            self.dept_tree.column(col, width=200)
        self.dept_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_departments).pack(pady=2)
        tk.Button(frame, text="Add Department", command=self.add_department).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_departments()

    def load_departments(self):
        for row in self.dept_tree.get_children():
            self.dept_tree.delete(row)
        c.execute("SELECT * FROM departments ORDER BY id DESC")
        rows = c.fetchall()
        for r in rows:
            self.dept_tree.insert("", "end", values=r)

    def add_department(self):
        name = simpledialog.askstring("Input", "Department Name")
        mgr = simpledialog.askstring("Input", "Manager Name")
        if not name: return
        c.execute("INSERT INTO departments (name,manager) VALUES (?,?)", (name, mgr))
        conn.commit()
        messagebox.showinfo("Success", "Department added")
        self.load_departments()

    # ---------------- Branches ----------------
    def create_branches(self):
        frame = self.frames["branches"]
        tk.Label(frame, text="Branches", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.branch_tree = ttk.Treeview(frame, columns=("ID", "Name", "Location", "Manager"), show="headings")
        for col in self.branch_tree["columns"]:
            self.branch_tree.heading(col, text=col)
            self.branch_tree.column(col, width=200)
        self.branch_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_branches).pack(pady=2)
        tk.Button(frame, text="Add Branch", command=self.add_branch).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_branches()

    def load_branches(self):
        for row in self.branch_tree.get_children():
            self.branch_tree.delete(row)
        c.execute("SELECT * FROM branches ORDER BY id DESC")
        rows = c.fetchall()
        for r in rows:
            self.branch_tree.insert("", "end", values=r)

    def add_branch(self):
        name = simpledialog.askstring("Input", "Branch Name")
        location = simpledialog.askstring("Input", "Location")
        manager = simpledialog.askstring("Input", "Manager Name")
        if not name or not location: return
        c.execute("INSERT INTO branches (name,location,manager) VALUES (?,?,?)", (name, location, manager))
        conn.commit()
        messagebox.showinfo("Success", "Branch added")
        self.load_branches()

    # ---------------- Payroll ----------------
    def create_payroll(self):
        frame = self.frames["payroll"]
        tk.Label(frame, text="Payroll", font=("Segoe UI", 14, "bold"), fg=self.PRIMARY, bg=self.BG).pack(pady=6)
        self.pay_tree = ttk.Treeview(frame, columns=("ID", "Name", "Branch", "Salary"), show="headings")
        for col in self.pay_tree["columns"]:
            self.pay_tree.heading(col, text=col)
            self.pay_tree.column(col, width=200)
        self.pay_tree.pack(fill="both", expand=True)
        tk.Button(frame, text="Refresh", bg=self.PRIMARY, fg="white", command=self.load_payroll).pack(pady=2)
        tk.Button(frame, text="Back", command=lambda: self.show_frame("home")).pack(pady=2)
        self.load_payroll()

    def load_payroll(self):
        for row in self.pay_tree.get_children():
            self.pay_tree.delete(row)
        c.execute("""SELECT e.id,e.name,b.name,e.salary FROM employees e
                     LEFT JOIN branches b ON e.branch_id=b.id ORDER BY e.id DESC""")
        rows = c.fetchall()
        for r in rows:
            self.pay_tree.insert("", "end", values=r)


# ---------------- Start Application ----------------
root = tk.Tk()
app = EMS(root)
root.mainloop()

