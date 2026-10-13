"""Teacher dashboard — create and manage students."""
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import csv
from datetime import datetime

from database import (
    add_student, update_student, delete_student,
    get_all_students, get_student_by_id, get_all_attempts,
    bulk_add_students, change_password, get_analytics,
    get_question_count_by_dept, DEPARTMENTS, PASS_MARK
)

SCHOOL_NAME = "Lagos State Senior Model College Ojo"
SEX_OPTIONS = ["Male", "Female"]


class TeacherDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            sidebar, text="TEACHER PANEL",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, pady=(25, 5), padx=12)

        ctk.CTkLabel(
            sidebar, text=user["full_name"], font=ctk.CTkFont(size=12)
        ).grid(row=1, column=0, pady=(0, 20), padx=12)

        for i, (text, cmd) in enumerate([
            ("Dashboard", self.show_dashboard),
            ("Manage Students", self.show_students),
            ("View All Results", self.show_results),
            ("Change Password", self.show_change_password),
        ], start=2):
            ctk.CTkButton(sidebar, text=text, command=cmd, width=170, anchor="w").grid(
                row=i, column=0, padx=12, pady=5
            )

        ctk.CTkButton(
            sidebar, text="Logout", fg_color="#c0392b", hover_color="#a93226",
            command=self.on_logout, width=170
        ).grid(row=9, column=0, padx=12, pady=20)

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
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
            frame, text="Teacher Dashboard",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(10, 15), sticky="w")

        analytics = get_analytics()
        counts = get_question_count_by_dept()

        cards = [
            ("Total Students", str(analytics["total_students"]), "#3498db"),
            ("Science Questions", str(counts.get("Science", 0)), "#27ae60"),
            ("Art Questions", str(counts.get("Art", 0)), "#9b59b6"),
            ("Commercial Questions", str(counts.get("Commercial", 0)), "#e67e22"),
            ("Tests Taken", str(analytics["total_attempts"]), "#1abc9c"),
        ]
        for i, (title, value, color) in enumerate(cards):
            card = ctk.CTkFrame(frame, fg_color=color, corner_radius=12)
            card.grid(row=1 + i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=30, weight="bold"),
                         text_color="white").pack(pady=(18, 4))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13),
                         text_color="white").pack(pady=(0, 18))

        ctk.CTkLabel(
            frame, text="You manage student records. HODs set the exam questions.",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).grid(row=3, column=0, columnspan=3, pady=20, sticky="w")

    def show_students(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="Manage Students", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Import CSV", command=self.import_csv).pack(side="right", padx=5)
        ctk.CTkButton(top, text="+ Add Student", command=self.open_add_student).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "admission_no", "full_name", "sex", "state", "lga", "username")
        self.student_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=15)
        for col, h, w in zip(cols,
                             ["ID", "Admission No", "Full Name", "Sex", "State", "LGA", "Username"],
                             [40, 110, 160, 60, 90, 90, 100]):
            self.student_tree.heading(col, text=h)
            self.student_tree.column(col, width=w)
        self.student_tree.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

        btn = ctk.CTkFrame(frame, fg_color="transparent")
        btn.grid(row=2, column=0, sticky="ew", pady=10)
        ctk.CTkButton(btn, text="Edit Selected", command=self.edit_student).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="Delete Selected", fg_color="#c0392b", hover_color="#a93226",
                      command=self.delete_selected).pack(side="left", padx=5)
        ctk.CTkButton(btn, text="Refresh", command=self.refresh_students).pack(side="left", padx=5)

        self.refresh_students()

    def refresh_students(self):
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        for s in get_all_students():
            self.student_tree.insert("", "end", values=(
                s["id"], s["admission_no"] or "", s["full_name"],
                s.get("sex") or "", s.get("state") or "", s.get("lga") or "",
                s["username"]
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

    def delete_selected(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student first.")
            return
        vals = self.student_tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm Delete", f"Delete student {vals[2]}?\nThis also removes their test records."):
            delete_student(vals[0])
            self.refresh_students()
            messagebox.showinfo("Deleted", "Student deleted.")

    def import_csv(self):
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
                headers = {h.lower() for h in (reader.fieldnames or [])}
                if not required.issubset(headers):
                    messagebox.showerror(
                        "Invalid CSV",
                        "CSV must have at least: username, password, full_name, admission_no\n"
                        "Optional: state, lga, date_of_birth, sex, parents_number"
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
        win.geometry("460x640")
        win.transient(self.winfo_toplevel())
        win.grab_set()

        fields = {}

        def field(label, key, show=None, width=380):
            ctk.CTkLabel(win, text=label).pack(pady=(10, 0), padx=30, anchor="w")
            e = ctk.CTkEntry(win, width=width, show=show)
            e.pack(padx=30)
            fields[key] = e
            return e

        field("Full Name *", "full_name")
        field("Admission Number *", "admission_no")
        field("Username (for login) *", "username")
        field("Password *" if student is None else "Password (leave blank to keep)", "password", show="•")
        field("State", "state")
        field("LGA", "lga")
        field("Date of Birth (YYYY-MM-DD)", "date_of_birth")

        ctk.CTkLabel(win, text="Sex").pack(pady=(10, 0), padx=30, anchor="w")
        sex_cb = ctk.CTkComboBox(win, values=["", "Male", "Female"], width=380)
        sex_cb.pack(padx=30)
        sex_cb.set("")
        fields["sex"] = sex_cb

        field("Parents' Phone Number", "parents_number")

        if student:
            fields["full_name"].insert(0, student["full_name"])
            fields["admission_no"].insert(0, student["admission_no"] or "")
            fields["username"].insert(0, student["username"])
            fields["username"].configure(state="disabled")
            fields["state"].insert(0, student.get("state") or "")
            fields["lga"].insert(0, student.get("lga") or "")
            fields["date_of_birth"].insert(0, student.get("date_of_birth") or "")
            sex_cb.set(student.get("sex") or "")
            fields["parents_number"].insert(0, student.get("parents_number") or "")

        def save():
            full_name = fields["full_name"].get().strip()
            adm = fields["admission_no"].get().strip()
            username = fields["username"].get().strip()
            password = fields["password"].get()
            state = fields["state"].get().strip()
            lga = fields["lga"].get().strip()
            dob = fields["date_of_birth"].get().strip()
            sex = sex_cb.get().strip()
            parents = fields["parents_number"].get().strip()

            if not full_name or not adm or not username:
                messagebox.showwarning("Missing", "Full name, admission number and username are required.")
                return

            if student is None:
                if not password:
                    messagebox.showwarning("Missing", "Password is required for new students.")
                    return
                ok, msg = add_student(
                    username, password, full_name, adm,
                    state, lga, dob, sex, parents
                )
            else:
                ok, msg = update_student(
                    student["id"], full_name, adm,
                    password if password else None,
                    state, lga, dob, sex, parents
                )
            if ok:
                messagebox.showinfo("Success", msg)
                win.destroy()
                self.refresh_students()
            else:
                messagebox.showerror("Error", msg)

        ctk.CTkButton(win, text="Save", width=380, command=save).pack(pady=20)

    def show_results(self):
        self.clear_content()
        frame = ctk.CTkFrame(self.content)
        frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(top, text="All Test Results", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left")
        ctk.CTkButton(top, text="Export CSV", command=self.export_results).pack(side="right", padx=5)

        tree_frame = ctk.CTkFrame(frame)
        tree_frame.grid(row=1, column=0, sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        cols = ("id", "student", "admission", "department", "score", "pct", "date")
        self.results_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=16)
        for col, h, w in zip(cols,
                             ["ID", "Student", "Admission No", "Department", "Score", "%", "Date"],
                             [40, 160, 110, 100, 70, 55, 130]):
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
        for a in get_all_attempts():
            self.results_tree.insert("", "end", values=(
                a["id"], a["full_name"], a["admission_no"] or "",
                a["department"], f"{a['score']}/{a['total_questions']}",
                f"{a['percentage']}%",
                a["taken_at"][:16] if a["taken_at"] else ""
            ))

    def export_results(self):
        path = filedialog.asksaveasfilename(
            title="Export Results", defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"all_results_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not path:
            return
        attempts = get_all_attempts()
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
