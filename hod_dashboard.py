"""HOD dashboard — manage questions for one department only."""
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import csv
from datetime import datetime

from database import (
    add_question, update_question, delete_question,
    get_questions_by_department, get_attempts_by_department,
    change_password, HOD_DEPARTMENT, ROLE_LABELS,
    get_exam_minutes, set_setting, PASS_MARK
)

SCHOOL_NAME = "Lagos State Senior Model College Ojo"


class HODDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.department = HOD_DEPARTMENT[user["role"]]
        self.role_label = ROLE_LABELS.get(user["role"], user["role"])

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            sidebar, text=self.role_label,
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, pady=(25, 2), padx=12)

        ctk.CTkLabel(
            sidebar, text=f"Dept: {self.department}",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).grid(row=1, column=0, pady=(0, 15), padx=12)

        ctk.CTkLabel(
            sidebar, text=user["full_name"],
            font=ctk.CTkFont(size=12)
        ).grid(row=2, column=0, pady=(0, 20), padx=12)

        for i, (text, cmd) in enumerate([
            ("My Questions", self.show_questions),
            ("Department Results", self.show_results),
            ("Settings", self.show_settings),
            ("Change Password", self.show_change_password),
        ], start=3):
            ctk.CTkButton(sidebar, text=text, command=cmd, width=180, anchor="w").grid(
                row=i, column=0, padx=12, pady=5
            )

        ctk.CTkButton(
            sidebar, text="Logout", fg_color="#c0392b", hover_color="#a93226",
            command=self.on_logout, width=180
        ).grid(row=9, column=0, padx=12, pady=20)

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.show_questions()

    def clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def show_questions(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            top, text=f"{self.department} Questions",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(top, text="+ Add Question", command=self.open_add_question).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "question", "correct")
        self.q_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=16)
        self.q_tree.heading("id", text="ID")
        self.q_tree.heading("question", text="Question")
        self.q_tree.heading("correct", text="Answer")
        self.q_tree.column("id", width=50)
        self.q_tree.column("question", width=520)
        self.q_tree.column("correct", width=60)
        self.q_tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.q_tree.yview)
        self.q_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        btn = ctk.CTkFrame(frame, fg_color="transparent")
        btn.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn, text="Edit Selected", command=self.edit_question).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="Delete Selected", fg_color="#c0392b", hover_color="#a93226",
                      command=self.delete_question).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="Refresh", command=self.refresh_questions).pack(side="left", padx=5)

        self.refresh_questions()

    def refresh_questions(self):
        for item in self.q_tree.get_children():
            self.q_tree.delete(item)
        for q in get_questions_by_department(self.department):
            preview = q["question_text"][:90] + ("..." if len(q["question_text"]) > 90 else "")
            self.q_tree.insert("", "end", values=(q["id"], preview, q["correct_option"]))

    def open_add_question(self):
        self._question_form()

    def edit_question(self):
        sel = self.q_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a question first.")
            return
        qid = self.q_tree.item(sel[0])["values"][0]
        questions = get_questions_by_department(self.department)
        question = next((q for q in questions if q["id"] == qid), None)
        if question:
            self._question_form(question)

    def delete_question(self):
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
        win.geometry("540x560")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        ctk.CTkLabel(
            win, text=f"Department: {self.department} (fixed)",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(15, 5), padx=30, anchor="w")

        ctk.CTkLabel(win, text="Question Text").pack(pady=(8, 0), padx=30, anchor="w")
        q_text = ctk.CTkTextbox(win, width=460, height=80)
        q_text.pack(padx=30)
        if question:
            q_text.insert("1.0", question["question_text"])

        opts = {}
        for letter in "ABCD":
            ctk.CTkLabel(win, text=f"Option {letter}").pack(pady=(8, 0), padx=30, anchor="w")
            e = ctk.CTkEntry(win, width=460)
            e.pack(padx=30)
            opts[letter] = e
            if question:
                e.insert(0, question[f"option_{letter.lower()}"])

        ctk.CTkLabel(win, text="Correct Answer").pack(pady=(10, 0), padx=30, anchor="w")
        correct_cb = ctk.CTkComboBox(win, values=["A", "B", "C", "D"], width=100)
        correct_cb.pack(padx=30, anchor="w")
        if question:
            correct_cb.set(question["correct_option"])
        else:
            correct_cb.set("A")

        def save():
            text = q_text.get("1.0", "end").strip()
            a = opts["A"].get().strip()
            b = opts["B"].get().strip()
            c = opts["C"].get().strip()
            d = opts["D"].get().strip()
            if not text or not a or not b or not c or not d:
                messagebox.showwarning("Missing", "All fields are required.")
                return
            if question is None:
                add_question(
                    self.department, text, a, b, c, d,
                    correct_cb.get(), self.user["id"]
                )
            else:
                update_question(
                    question["id"], self.department, text, a, b, c, d,
                    correct_cb.get()
                )
            messagebox.showinfo("Saved", "Question saved successfully.")
            win.destroy()
            self.refresh_questions()

        ctk.CTkButton(win, text="Save", width=460, command=save).pack(pady=20)

    def show_results(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(
            top, text=f"{self.department} Results",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        ctk.CTkButton(top, text="Export CSV", command=self.export_results).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "student", "admission", "score", "pct", "date")
        self.results_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=16)
        for col, h, w in zip(cols,
                             ["ID", "Student", "Admission No", "Score", "%", "Date"],
                             [50, 180, 120, 80, 60, 140]):
            self.results_tree.heading(col, text=h)
            self.results_tree.column(col, width=w)
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        self.refresh_results()

    def refresh_results(self):
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for a in get_attempts_by_department(self.department):
            self.results_tree.insert("", "end", values=(
                a["id"], a["full_name"], a["admission_no"] or "",
                f"{a['score']}/{a['total_questions']}",
                f"{a['percentage']}%",
                a["taken_at"][:16] if a["taken_at"] else ""
            ))

    def export_results(self):
        path = filedialog.asksaveasfilename(
            title="Export Results", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{self.department}_results_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not path:
            return
        attempts = get_attempts_by_department(self.department)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "student_name", "admission_no", "score", "total", "percentage", "taken_at"])
            for a in attempts:
                writer.writerow([
                    a["id"], a["full_name"], a["admission_no"] or "",
                    a["score"], a["total_questions"], a["percentage"], a["taken_at"]
                ])
        messagebox.showinfo("Exported", f"Saved {len(attempts)} results to:\n{path}")

    def show_settings(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=30)

        ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", pady=(10, 20))
        ctk.CTkLabel(frame, text="Exam Duration (minutes)", font=ctk.CTkFont(size=14)).pack(anchor="w")
        minutes_var = ctk.StringVar(value=str(get_exam_minutes()))
        ctk.CTkEntry(frame, width=120, textvariable=minutes_var).pack(anchor="w", pady=(5, 15))

        def save():
            try:
                m = int(minutes_var.get().strip())
                if m < 1 or m > 180:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Invalid", "Enter a number between 1 and 180.")
                return
            set_setting("exam_minutes", str(m))
            messagebox.showinfo("Saved", f"Exam duration set to {m} minutes.")

        ctk.CTkButton(frame, text="Save Settings", command=save).pack(anchor="w", pady=10)

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
