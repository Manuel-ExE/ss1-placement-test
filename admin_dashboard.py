"""Admin dashboard for SS1 Placement Test"""
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import csv
from datetime import datetime

from database import (
    add_student, update_student, delete_student,
    get_all_students, get_student_by_id, add_question, update_question,
    delete_question, get_questions_by_department, get_all_questions,
    get_all_attempts, change_password,
    get_question_count_by_dept, DEPARTMENTS,
    bulk_add_students, get_analytics, get_exam_minutes, set_setting
)

SCHOOL_NAME = "Lagos State Senior Model College Ojo"
PASS_MARK = 50


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(10, weight=1)

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
            ("Settings", self.show_settings),
            ("Change Password", self.show_change_password),
        ]
        for i, (text, cmd) in enumerate(buttons, start=2):
            btn = ctk.CTkButton(sidebar, text=text, command=cmd, width=170, anchor="w")
            btn.grid(row=i, column=0, padx=15, pady=5)

        ctk.CTkButton(
            sidebar, text="Logout", fg_color="#c0392b", hover_color="#a93226",
            command=self.on_logout, width=170
        ).grid(row=11, column=0, padx=15, pady=20)

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
        ).grid(row=0, column=0, columnspan=3, pady=(10, 15), sticky="w")

        analytics = get_analytics()
        counts = get_question_count_by_dept()

        cards_data = [
            ("Total Students", str(analytics["total_students"]), "#3498db"),
            ("Science Questions", str(counts.get("Science", 0)), "#27ae60"),
            ("Art Questions", str(counts.get("Art", 0)), "#9b59b6"),
            ("Commercial Questions", str(counts.get("Commercial", 0)), "#e67e22"),
            ("Tests Taken", str(analytics["total_attempts"]), "#1abc9c"),
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = ctk.CTkFrame(frame, fg_color=color, corner_radius=12)
            card.grid(row=1 + i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"),
                         text_color="white").pack(pady=(20, 5))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14),
                         text_color="white").pack(pady=(0, 20))

        ctk.CTkLabel(
            frame, text="Department Performance",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=3, column=0, columnspan=3, pady=(25, 10), sticky="w")

        for i, dept in enumerate(DEPARTMENTS):
            stats = analytics["departments"].get(dept, {})
            card = ctk.CTkFrame(frame, corner_radius=10)
            card.grid(row=4, column=i, padx=8, pady=5, sticky="nsew")
            ctk.CTkLabel(card, text=dept, font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(12, 4))
            ctk.CTkLabel(card, text=f"Attempts: {stats.get('attempts', 0)}",
                         font=ctk.CTkFont(size=12)).pack()
            ctk.CTkLabel(card, text=f"Average: {stats.get('average', 0)}%",
                         font=ctk.CTkFont(size=12)).pack()
            ctk.CTkLabel(card, text=f"Pass Rate: {stats.get('pass_rate', 0)}%",
                         font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 12))

    def show_students(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="Manage Students", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Import CSV", command=self.import_students_csv).pack(side="right", padx=5)
        ctk.CTkButton(top, text="+ Add Student", command=self.open_add_student).pack(side="right", padx=5)

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

    def import_students_csv(self):
        path = filedialog.askopenfilename(
            title="Import Students from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not path:
            return
        rows = []
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                required = {"username", "password", "full_name", "admission_no"}
                if not required.issubset(set(h.lower() for h in (reader.fieldnames or []))):
                    messagebox.showerror(
                        "Invalid CSV",
                        "CSV must have columns: username, password, full_name, admission_no"
                    )
                    return
                for raw in reader:
                    row = {k.lower().strip(): (v or "").strip() for k, v in raw.items()}
                    rows.append(row)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read CSV:\n{e}")
            return

        if not rows:
            messagebox.showwarning("Empty", "No rows found in the CSV.")
            return

        ok, fail, errors = bulk_add_students(rows)
        msg = f"Import finished.\n\nSuccessful: {ok}\nFailed: {fail}"
        if errors:
            msg += "\n\nFirst few errors:\n" + "\n".join(errors[:5])
        messagebox.showinfo("Import Result", msg)
        self.refresh_students()

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
        ctk.CTkButton(top, text="Export CSV", command=self.export_questions_csv).pack(side="right", padx=5)
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

    def export_questions_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Questions",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"questions_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not path:
            return
        questions = get_all_questions()
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "department", "question_text", "option_a", "option_b",
                                 "option_c", "option_d", "correct_option"])
                for q in questions:
                    writer.writerow([
                        q["id"], q["department"], q["question_text"],
                        q["option_a"], q["option_b"], q["option_c"], q["option_d"],
                        q["correct_option"]
                    ])
            messagebox.showinfo("Exported", f"Saved {len(questions)} questions to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
            else:
                update_question(question["id"], dept_cb.get(), text, a, b, c, d, correct_cb.get())
            messagebox.showinfo("Saved", "Question saved successfully.")
            win.destroy()
            self.refresh_questions()

        ctk.CTkButton(win, text="Save", width=440, command=save).pack(pady=20)

    def show_results(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="Test Results", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Export CSV", command=self.export_results_csv).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = ("id", "student", "admission", "department", "score", "pct", "date")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=16)
        headings = ["ID", "Student", "Admission No", "Department", "Score", "%", "Date"]
        widths = [50, 180, 110, 100, 80, 60, 140]
        for col, h, w in zip(columns, headings, widths):
            self.results_tree.heading(col, text=h)
            self.results_tree.column(col, width=w)
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn_frame, text="View / Print Report", command=self.print_result_report).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Refresh", command=self.refresh_results).pack(side="left", padx=5)

        self.refresh_results()

    def refresh_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for a in get_all_attempts():
            self.results_tree.insert("", "end", values=(
                a["id"], a["full_name"], a["admission_no"] or "",
                a["department"], f"{a['score']}/{a['total_questions']}",
                f"{a['percentage']}%", a["taken_at"][:16] if a["taken_at"] else ""
            ))

    def export_results_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"results_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not path:
            return
        attempts = get_all_attempts()
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "student_name", "admission_no", "department",
                                 "score", "total", "percentage", "taken_at"])
                for a in attempts:
                    writer.writerow([
                        a["id"], a["full_name"], a["admission_no"] or "",
                        a["department"], a["score"], a["total_questions"],
                        a["percentage"], a["taken_at"]
                    ])
            messagebox.showinfo("Exported", f"Saved {len(attempts)} results to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def print_result_report(self):
        sel = self.results_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a result first.")
            return
        vals = self.results_tree.item(sel[0])["values"]
        attempt_id = vals[0]

        attempts = get_all_attempts()
        attempt = next((a for a in attempts if a["id"] == attempt_id), None)
        if not attempt:
            return

        eligible = attempt["percentage"] >= PASS_MARK
        report = (
            f"{'='*50}\n"
            f"  {SCHOOL_NAME}\n"
            f"  SS1 Placement Test Result\n"
            f"{'='*50}\n\n"
            f"Student Name : {attempt['full_name']}\n"
            f"Admission No : {attempt['admission_no'] or 'N/A'}\n"
            f"Department   : {attempt['department']}\n"
            f"Date Taken   : {attempt['taken_at']}\n\n"
            f"Score        : {attempt['score']} / {attempt['total_questions']}\n"
            f"Percentage   : {attempt['percentage']}%\n"
            f"Pass Mark    : {PASS_MARK}%\n\n"
            f"Result       : {'ELIGIBLE for ' + attempt['department'] if eligible else 'NOT ELIGIBLE'}\n"
            f"{'='*50}\n"
        )

        win = ctk.CTkToplevel(self)
        win.title("Result Report")
        win.geometry("480x420")
        win.transient(self.winfo_toplevel())

        text = ctk.CTkTextbox(win, width=440, height=320, font=ctk.CTkFont(family="Courier", size=13))
        text.pack(padx=20, pady=15)
        text.insert("1.0", report)
        text.configure(state="disabled")

        def save_report():
            path = filedialog.asksaveasfilename(
                title="Save Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=f"result_{attempt['admission_no'] or attempt['id']}.txt"
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                messagebox.showinfo("Saved", f"Report saved to:\n{path}")

        ctk.CTkButton(win, text="Save as Text File", command=save_report).pack(pady=5)

    def show_settings(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

        ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(10, 20))

        ctk.CTkLabel(frame, text="Exam Duration (minutes)", font=ctk.CTkFont(size=14)).pack(anchor="w")
        minutes_var = ctk.StringVar(value=str(get_exam_minutes()))
        minutes_entry = ctk.CTkEntry(frame, width=120, textvariable=minutes_var)
        minutes_entry.pack(anchor="w", pady=(5, 15))

        def save_settings():
            try:
                m = int(minutes_var.get().strip())
                if m < 1 or m > 180:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Please enter a number between 1 and 180.")
                return
            set_setting("exam_minutes", str(m))
            messagebox.showinfo("Saved", f"Exam duration set to {m} minutes.")

        ctk.CTkButton(frame, text="Save Settings", command=save_settings).pack(anchor="w", pady=10)

        ctk.CTkLabel(
            frame,
            text="Note: The countdown timer will use this value for every new test.",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(anchor="w", pady=10)

    def show_change_password(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

        ctk.CTkLabel(frame, text="Change Password", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(10, 20))

        ctk.CTkLabel(frame, text="New Password").pack(anchor="w")
        new_e = ctk.CTkEntry(frame, width=280, show="•")
        new_e.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(frame, text="Confirm Password").pack(anchor="w")
        conf_e = ctk.CTkEntry(frame, width=280, show="•")
        conf_e.pack(anchor="w", pady=(0, 15))

        def save():
            p1, p2 = new_e.get(), conf_e.get()
            if not p1 or len(p1) < 4:
                messagebox.showwarning("Weak", "Password must be at least 4 characters.")
                return
            if p1 != p2:
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            change_password(self.user["id"], p1)
            messagebox.showinfo("Done", "Password changed successfully.")
            new_e.delete(0, "end")
            conf_e.delete(0, "end")

        ctk.CTkButton(frame, text="Update Password", command=save).pack(anchor="w")
