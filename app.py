"""
Lagos State Senior Model College Ojo
SS1 Placement Test Application
Science | Art | Commercial
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import json
from database import (
    init_db, authenticate, add_student, update_student, delete_student,
    get_all_students, get_student_by_id, add_question, update_question,
    delete_question, get_questions_by_department, get_all_questions,
    save_attempt, get_student_attempts, get_all_attempts, change_password,
    get_question_count_by_dept, DEPARTMENTS
)

# Appearance
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

SCHOOL_NAME = "Lagos State Senior Model College Ojo"
APP_TITLE = f"{SCHOOL_NAME} — SS1 Placement Test"
PASS_MARK = 50  # percentage needed to be considered eligible for the stream


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkLabel(
            self, text=SCHOOL_NAME,
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.grid(row=0, column=0, pady=(40, 5), padx=20)

        sub = ctk.CTkLabel(
            self, text="SS1 Placement Test System",
            font=ctk.CTkFont(size=16)
        )
        sub.grid(row=1, column=0, pady=(0, 30))

        card = ctk.CTkFrame(self)
        card.grid(row=2, column=0, padx=40, pady=10, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Login", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, pady=(20, 15)
        )

        ctk.CTkLabel(card, text="Username").grid(row=1, column=0, sticky="w", padx=30)
        self.username_entry = ctk.CTkEntry(card, width=280, placeholder_text="Enter username")
        self.username_entry.grid(row=2, column=0, padx=30, pady=(0, 10))

        ctk.CTkLabel(card, text="Password").grid(row=3, column=0, sticky="w", padx=30)
        self.password_entry = ctk.CTkEntry(card, width=280, show="•", placeholder_text="Enter password")
        self.password_entry.grid(row=4, column=0, padx=30, pady=(0, 15))

        self.login_btn = ctk.CTkButton(card, text="Login", width=280, command=self.do_login)
        self.login_btn.grid(row=5, column=0, padx=30, pady=(0, 25))

        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        note = ctk.CTkLabel(
            self,
            text="Default Admin → username: admin  |  password: admin123\nPlease change the password after first login.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        note.grid(row=3, column=0, pady=20)

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return
        user = authenticate(username, password)
        if user:
            self.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            sidebar, text="ADMIN PANEL",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, pady=(25, 5), padx=15)

        ctk.CTkLabel(
            sidebar, text=user["full_name"],
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, pady=(0, 20), padx=15)

        buttons = [
            ("Dashboard", self.show_dashboard),
            ("Manage Students", self.show_students),
            ("Manage Questions", self.show_questions),
            ("View Results", self.show_results),
            ("Change Password", self.show_change_password),
        ]
        for i, (text, cmd) in enumerate(buttons, start=2):
            btn = ctk.CTkButton(sidebar, text=text, command=cmd, width=170, anchor="w")
            btn.grid(row=i, column=0, padx=15, pady=5)

        ctk.CTkButton(
            sidebar, text="Logout", fg_color="#c0392b", hover_color="#a93226",
            command=self.on_logout, width=170
        ).grid(row=9, column=0, padx=15, pady=20)

        # Content area
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_dashboard()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_dashboard(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            frame, text="Welcome, Administrator",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(10, 25), sticky="w")

        students = get_all_students()
        counts = get_question_count_by_dept()
        attempts = get_all_attempts()

        cards_data = [
            ("Total Students", str(len(students)), "#3498db"),
            ("Science Questions", str(counts.get("Science", 0)), "#27ae60"),
            ("Art Questions", str(counts.get("Art", 0)), "#9b59b6"),
            ("Commercial Questions", str(counts.get("Commercial", 0)), "#e67e22"),
            ("Tests Taken", str(len(attempts)), "#1abc9c"),
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = ctk.CTkFrame(frame, fg_color=color, corner_radius=12)
            card.grid(row=1 + i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"),
                         text_color="white").pack(pady=(20, 5))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14),
                         text_color="white").pack(pady=(0, 20))

        note = ctk.CTkLabel(
            frame,
            text="Use the sidebar to manage students, create department-specific questions,\nand view placement test results.",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        note.grid(row=3, column=0, columnspan=3, pady=30, sticky="w")

    # ---------- Students ----------
    def show_students(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="Manage Students", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="+ Add Student", command=self.open_add_student).pack(side="right", padx=5)

        # Treeview for list
        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "admission_no", "full_name", "username", "class")
        self.student_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        for col, heading in zip(columns, ["ID", "Admission No", "Full Name", "Username", "Class"]):
            self.student_tree.heading(col, text=heading)
            self.student_tree.column(col, width=120 if col != "full_name" else 200)
        self.student_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn_frame, text="Edit Selected", command=self.edit_student).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="#c0392b",
                      hover_color="#a93226", command=self.delete_selected_student).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_students).pack(side="left", padx=5)

        self.refresh_students()

    def refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in get_all_students():
            self.student_tree.insert("", "end", values=(
                s["id"], s["admission_no"] or "", s["full_name"], s["username"], s["class"]
            ))

    def open_add_student(self):
        self._student_form()

    def edit_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student first.")
            return
        vals = self.student_tree.item(sel[0])["values"]
        student = get_student_by_id(vals[0])
        if student:
            self._student_form(student)

    def delete_selected_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student first.")
            return
        vals = self.student_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm Delete", f"Delete student {vals[2]}?\nThis also removes their test records."):
            delete_student(vals[0])
            self.refresh_students()
            messagebox.showinfo("Deleted", "Student deleted.")

    def _student_form(self, student=None):
        win = ctk.CTkToplevel(self)
        win.title("Add Student" if student is None else "Edit Student")
        win.geometry("420x420")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        ctk.CTkLabel(win, text="Full Name").pack(pady=(20, 0), padx=30, anchor="w")
        name_e = ctk.CTkEntry(win, width=340)
        name_e.pack(padx=30)
        if student:
            name_e.insert(0, student["full_name"])

        ctk.CTkLabel(win, text="Admission Number").pack(pady=(12, 0), padx=30, anchor="w")
        adm_e = ctk.CTkEntry(win, width=340)
        adm_e.pack(padx=30)
        if student:
            adm_e.insert(0, student["admission_no"] or "")

        ctk.CTkLabel(win, text="Username (for login)").pack(pady=(12, 0), padx=30, anchor="w")
        user_e = ctk.CTkEntry(win, width=340)
        user_e.pack(padx=30)
        if student:
            user_e.insert(0, student["username"])
            user_e.configure(state="disabled")

        ctk.CTkLabel(win, text="Password" + (" (leave blank to keep current)" if student else "")).pack(
            pady=(12, 0), padx=30, anchor="w"
        )
        pass_e = ctk.CTkEntry(win, width=340, show="•")
        pass_e.pack(padx=30)

        def save():
            full_name = name_e.get().strip()
            adm = adm_e.get().strip()
            username = user_e.get().strip()
            password = pass_e.get()
            if not full_name or not adm or not username:
                messagebox.showwarning("Missing", "Full name, admission number and username are required.")
                return
            if student is None:
                if not password:
                    messagebox.showwarning("Missing", "Password is required for new students.")
                    return
                ok, msg = add_student(username, password, full_name, adm)
            else:
                ok, msg = update_student(student["id"], full_name, adm, password if password else None)
            if ok:
                messagebox.showinfo("Success", msg)
                win.destroy()
                self.refresh_students()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(win, text="Save", width=340, command=save).pack(pady=25)

    # ---------- Questions ----------
    def show_questions(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="Manage Questions (by Department)",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")

        self.dept_filter = ctk.CTkComboBox(top, values=["All"] + DEPARTMENTS, width=140,
                                           command=lambda _: self.refresh_questions())
        self.dept_filter.set("All")
        self.dept_filter.pack(side="right", padx=5)
        ctk.CTkButton(top, text="+ Add Question", command=self.open_add_question).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "department", "question", "correct")
        self.q_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        self.q_tree.heading("id", text="ID")
        self.q_tree.heading("department", text="Department")
        self.q_tree.heading("question", text="Question")
        self.q_tree.heading("correct", text="Answer")
        self.q_tree.column("id", width=50)
        self.q_tree.column("department", width=100)
        self.q_tree.column("question", width=450)
        self.q_tree.column("correct", width=60)
        self.q_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.q_tree.yview)
        self.q_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn_frame, text="Edit Selected", command=self.edit_question).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Delete Selected", fg_color="#c0392b",
                      hover_color="#a93226", command=self.delete_selected_question).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_questions).pack(side="left", padx=5)

        self.refresh_questions()

    def refresh_questions(self):
        for item in self.q_tree.get_children():
            self.q_tree.delete(item)
        dept = self.dept_filter.get()
        questions = get_all_questions() if dept == "All" else get_questions_by_department(dept)
        for q in questions:
            preview = q["question_text"][:80] + ("..." if len(q["question_text"]) > 80 else "")
            self.q_tree.insert("", "end", values=(q["id"], q["department"], preview, q["correct_option"]))

    def open_add_question(self):
        self._question_form()

    def edit_question(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a question first.")
            return
        qid = self.q_tree.item(sel[0])["values"][0]
        all_q = get_all_questions()
        question = next((q for q in all_q if q["id"] == qid), None)
        if question:
            self._question_form(question)

    def delete_selected_question(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a question first.")
            return
        qid = self.q_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", "Delete this question?"):
            delete_question(qid)
            self.refresh_questions()

    def _question_form(self, question=None):
        win = ctk.CTkToplevel(self)
        win.title("Add Question" if question is None else "Edit Question")
        win.geometry("520x580")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        ctk.CTkLabel(win, text="Department").pack(pady=(15, 0), padx=30, anchor="w")
        dept_cb = ctk.CTkComboBox(win, values=DEPARTMENTS, width=440)
        dept_cb.pack(padx=30)
        if question:
            dept_cb.set(question["department"])
        else:
            dept_cb.set("Science")

        ctk.CTkLabel(win, text="Question Text").pack(pady=(10, 0), padx=30, anchor="w")
        q_text = ctk.CTkTextbox(win, width=440, height=80)
        q_text.pack(padx=30)
        if question:
            q_text.insert("1.0", question["question_text"])

        opts = {}
        for letter in "ABCD":
            ctk.CTkLabel(win, text=f"Option {letter}").pack(pady=(8, 0), padx=30, anchor="w")
            e = ctk.CTkEntry(win, width=440)
            e.pack(padx=30)
            opts[letter] = e
            if question:
                e.insert(0, question[f"option_{letter.lower()}"])

        ctk.CTkLabel(win, text="Correct Option").pack(pady=(10, 0), padx=30, anchor="w")
        correct_cb = ctk.CTkComboBox(win, values=["A", "B", "C", "D"], width=100)
        correct_cb.pack(padx=30, anchor="w")
        if question:
            correct_cb.set(question["correct_option"])
        else:
            correct_cb.set("A")

        def save():
            text = q_text.get("1.0", "end").strip()
            a, b, c, d = opts["A"].get().strip(), opts["B"].get().strip(), opts["C"].get().strip(), opts["D"].get().strip()
            if not text or not a or not b or not c or not d:
                messagebox.showwarning("Missing", "All fields are required.")
                return
            if question is None:
                add_question(dept_cb.get(), text, a, b, c, d, correct_cb.get(), self.user["id"])
                messagebox.showinfo("Success", "Question added.")
            else:
                update_question(question["id"], dept_cb.get(), text, a, b, c, d, correct_cb.get())
                messagebox.showinfo("Success", "Question updated.")
            win.destroy()
            self.refresh_questions()

        ctk.CTkButton(win, text="Save Question", width=440, command=save).pack(pady=20)

    # ---------- Results ----------
    def show_results(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="All Placement Test Results",
                     font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("name", "adm", "dept", "score", "total", "pct", "date")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=18)
        headings = ["Student Name", "Admission No", "Department", "Score", "Total", "%", "Date"]
        widths = [180, 110, 100, 60, 60, 60, 140]
        for col, h, w in zip(columns, headings, widths):
            tree.heading(col, text=h)
            tree.column(col, width=w)
        tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        for a in get_all_attempts():
            tree.insert("", "end", values=(
                a["full_name"], a["admission_no"] or "", a["department"],
                a["score"], a["total_questions"], f"{a['percentage']}%",
                a["taken_at"][:19] if a["taken_at"] else ""
            ))

    # ---------- Change Password ----------
    def show_change_password(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Change Password",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 20), anchor="w", padx=30)

        ctk.CTkLabel(frame, text="New Password").pack(anchor="w", padx=30)
        new_p = ctk.CTkEntry(frame, width=300, show="•")
        new_p.pack(padx=30, pady=(0, 10))

        ctk.CTkLabel(frame, text="Confirm New Password").pack(anchor="w", padx=30)
        conf_p = ctk.CTkEntry(frame, width=300, show="•")
        conf_p.pack(padx=30, pady=(0, 15))

        def save():
            if not new_p.get() or new_p.get() != conf_p.get():
                messagebox.showwarning("Mismatch", "Passwords do not match or are empty.")
                return
            if len(new_p.get()) < 4:
                messagebox.showwarning("Weak", "Password should be at least 4 characters.")
                return
            change_password(self.user["id"], new_p.get())
            messagebox.showinfo("Success", "Password changed successfully.")
            new_p.delete(0, "end")
            conf_p.delete(0, "end")

        ctk.CTkButton(frame, text="Update Password", width=300, command=save).pack(padx=30, pady=10)


class StudentDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text=f"Welcome, {user['full_name']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15)

        ctk.CTkButton(header, text="Logout", width=100, fg_color="#c0392b",
                      hover_color="#a93226", command=self.on_logout).grid(row=0, column=2, padx=20)

        self.content = ctk.CTkFrame(self)
        self.content.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_home()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            frame, text="Choose a Department Placement Test",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(20, 10))

        ctk.CTkLabel(
            frame,
            text="Select the department you wish to be placed into.\nYou will answer the questions set for that department.",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=3, pady=(0, 25))

        colors = {"Science": "#27ae60", "Art": "#9b59b6", "Commercial": "#e67e22"}
        for i, dept in enumerate(DEPARTMENTS):
            count = len(get_questions_by_department(dept))
            card = ctk.CTkFrame(frame, fg_color=colors[dept], corner_radius=15)
            card.grid(row=2, column=i, padx=15, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=dept, font=ctk.CTkFont(size=22, weight="bold"),
                         text_color="white").pack(pady=(25, 5))
            ctk.CTkLabel(card, text=f"{count} question(s)", text_color="white").pack()
            ctk.CTkButton(
                card, text="Start Test", width=140,
                fg_color="white", text_color=colors[dept], hover_color="#ecf0f1",
                command=lambda d=dept: self.start_test(d)
            ).pack(pady=20)

        # Previous results
        ctk.CTkLabel(frame, text="Your Previous Results",
                     font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=3, column=0, columnspan=3, pady=(40, 10), sticky="w", padx=10
        )

        attempts = get_student_attempts(self.user["id"])
        if not attempts:
            ctk.CTkLabel(frame, text="No tests taken yet.", text_color="gray").grid(
                row=4, column=0, columnspan=3, sticky="w", padx=10
            )
        else:
            for i, a in enumerate(attempts[:5]):
                eligible = "Eligible" if a["percentage"] >= PASS_MARK else "Not yet eligible"
                color = "#27ae60" if a["percentage"] >= PASS_MARK else "#e74c3c"
                txt = f"{a['department']}: {a['score']}/{a['total_questions']} ({a['percentage']}%) — {eligible}  |  {a['taken_at'][:16]}"
                ctk.CTkLabel(frame, text=txt, text_color=color).grid(
                    row=4 + i, column=0, columnspan=3, sticky="w", padx=10, pady=2
                )

    def start_test(self, department: str):
        questions = get_questions_by_department(department)
        if not questions:
            messagebox.showwarning(
                "No Questions",
                f"There are currently no questions for the {department} department.\nPlease contact a teacher."
            )
            return
        if messagebox.askyesno(
            "Start Test",
            f"You are about to start the {department} placement test.\n"
            f"There are {len(questions)} questions.\n\nReady to begin?"
        ):
            self.take_test(department, questions)

    def take_test(self, department: str, questions: list):
        self.clear_content()
        self.current_answers = {}  # qid -> selected letter
        self.test_questions = questions
        self.test_department = department
        self.current_index = 0

        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        self.progress_label = ctk.CTkLabel(
            frame, text="", font=ctk.CTkFont(size=14)
        )
        self.progress_label.grid(row=0, column=0, pady=(15, 5), sticky="w", padx=20)

        self.q_frame = ctk.CTkFrame(frame)
        self.q_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.q_frame.grid_columnconfigure(0, weight=1)

        nav = ctk.CTkFrame(frame, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        self.prev_btn = ctk.CTkButton(nav, text="← Previous", width=120, command=self.prev_question)
        self.prev_btn.pack(side="left")
        self.next_btn = ctk.CTkButton(nav, text="Next →", width=120, command=self.next_question)
        self.next_btn.pack(side="right")
        self.submit_btn = ctk.CTkButton(
            nav, text="Submit Test", width=140, fg_color="#27ae60", hover_color="#1e8449",
            command=self.submit_test
        )
        self.submit_btn.pack(side="right", padx=15)

        self.render_question()

    def render_question(self):
        for w in self.q_frame.winfo_children():
            w.destroy()

        q = self.test_questions[self.current_index]
        total = len(self.test_questions)
        self.progress_label.configure(
            text=f"{self.test_department} Test  —  Question {self.current_index + 1} of {total}"
        )

        ctk.CTkLabel(
            self.q_frame, text=q["question_text"],
            font=ctk.CTkFont(size=16), wraplength=700, justify="left"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 25))

        self.selected_var = ctk.StringVar(value=self.current_answers.get(q["id"], ""))

        for i, letter in enumerate("ABCD"):
            text = q[f"option_{letter.lower()}"]
            rb = ctk.CTkRadioButton(
                self.q_frame, text=f"{letter}.  {text}",
                variable=self.selected_var, value=letter,
                font=ctk.CTkFont(size=14)
            )
            rb.grid(row=1 + i, column=0, sticky="w", padx=30, pady=8)

        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        is_last = self.current_index == total - 1
        self.next_btn.configure(state="disabled" if is_last else "normal")

    def save_current_answer(self):
        q = self.test_questions[self.current_index]
        val = self.selected_var.get()
        if val:
            self.current_answers[q["id"]] = val

    def prev_question(self):
        self.save_current_answer()
        if self.current_index > 0:
            self.current_index -= 1
            self.render_question()

    def next_question(self):
        self.save_current_answer()
        if self.current_index < len(self.test_questions) - 1:
            self.current_index += 1
            self.render_question()

    def submit_test(self):
        self.save_current_answer()
        unanswered = len(self.test_questions) - len(self.current_answers)
        if unanswered > 0:
            if not messagebox.askyesno(
                "Unanswered Questions",
                f"You have {unanswered} unanswered question(s).\nSubmit anyway?"
            ):
                return

        score = 0
        for q in self.test_questions:
            if self.current_answers.get(q["id"]) == q["correct_option"]:
                score += 1

        total = len(self.test_questions)
        answers_json = json.dumps(self.current_answers)
        _, percentage = save_attempt(
            self.user["id"], self.test_department, score, total, answers_json
        )

        eligible = percentage >= PASS_MARK
        msg = (
            f"Test Completed!\n\n"
            f"Department: {self.test_department}\n"
            f"Score: {score} / {total}\n"
            f"Percentage: {percentage}%\n\n"
        )
        if eligible:
            msg += f"Result: You are ELIGIBLE for the {self.test_department} department.\n(Pass mark: {PASS_MARK}%)"
        else:
            msg += f"Result: You did not reach the pass mark of {PASS_MARK}%.\nYou may retake the test later or try another department."

        messagebox.showinfo("Test Result", msg)
        self.show_home()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("960x640")
        self.minsize(800, 560)

        init_db()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_user = None
        self.show_login()

    def clear(self):
        for w in self.winfo_children():
            w.destroy()

    def show_login(self):
        self.clear()
        self.current_user = None
        login = LoginFrame(self, self.on_login_success)
        login.grid(row=0, column=0, sticky="nsew")

    def on_login_success(self, user):
        self.current_user = user
        self.clear()
        if user["role"] == "admin":
            dash = AdminDashboard(self, user, self.show_login)
        else:
            dash = StudentDashboard(self, user, self.show_login)
        dash.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
