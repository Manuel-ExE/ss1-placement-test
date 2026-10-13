"""
Lagos State Senior Model College Ojo
SS1 Placement Test Application

Roles: HOD Science | HOD Humanities | HOD Business | Teacher | Student
"""
import customtkinter as ctk
from tkinter import messagebox

from database import init_db, authenticate, ROLE_LABELS, HOD_DEPARTMENT
from hod_dashboard import HODDashboard
from teacher_dashboard import TeacherDashboard
from student_dashboard import StudentDashboard

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

SCHOOL_NAME = "Lagos State Senior Model College Ojo"
APP_TITLE = f"{SCHOOL_NAME} — SS1 Placement Test"

STAFF_ROLES = set(HOD_DEPARTMENT.keys()) | {"teacher"}


class LoginFrame(ctk.CTkFrame):
    """Login with Staff (HOD / Teacher) and Student modes."""

    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.login_mode = "staff"
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self, text=SCHOOL_NAME, font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, pady=(30, 5), padx=20)

        ctk.CTkLabel(
            self, text="SS1 Placement Test System", font=ctk.CTkFont(size=16)
        ).grid(row=1, column=0, pady=(0, 15))

        mode_row = ctk.CTkFrame(self, fg_color="transparent")
        mode_row.grid(row=2, column=0, pady=(0, 10))

        self.staff_btn = ctk.CTkButton(
            mode_row, text="HOD / Teacher Login", width=180, height=36,
            command=lambda: self.set_mode("staff")
        )
        self.staff_btn.pack(side="left", padx=6)

        self.student_btn = ctk.CTkButton(
            mode_row, text="Student Login", width=180, height=36,
            fg_color="gray", hover_color="#555555",
            command=lambda: self.set_mode("student")
        )
        self.student_btn.pack(side="left", padx=6)

        self.card = ctk.CTkFrame(self)
        self.card.grid(row=3, column=0, padx=40, pady=10, sticky="ew")
        self.card.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.card, text="Staff Login (HOD / Teacher)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(20, 15))

        ctk.CTkLabel(self.card, text="Username").grid(row=1, column=0, sticky="w", padx=30)
        self.username_entry = ctk.CTkEntry(self.card, width=300, placeholder_text="Enter username")
        self.username_entry.grid(row=2, column=0, padx=30, pady=(0, 10))

        ctk.CTkLabel(self.card, text="Password").grid(row=3, column=0, sticky="w", padx=30)
        self.password_entry = ctk.CTkEntry(
            self.card, width=300, show="•", placeholder_text="Enter password"
        )
        self.password_entry.grid(row=4, column=0, padx=30, pady=(0, 15))

        ctk.CTkButton(
            self.card, text="Login", width=300, height=36, command=self.do_login
        ).grid(row=5, column=0, padx=30, pady=(0, 20))

        self.password_entry.bind("<Return>", lambda e: self.do_login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        self.hint_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=11), text_color="gray", justify="left",
        )
        self.hint_label.grid(row=4, column=0, pady=(10, 20))

        self.set_mode("staff")

    def set_mode(self, mode: str):
        self.login_mode = mode
        if mode == "staff":
            self.title_label.configure(text="Staff Login (HOD / Teacher)")
            self.staff_btn.configure(fg_color=["#3a7ebf", "#1f538d"])
            self.student_btn.configure(fg_color="gray", hover_color="#555555")
            self.hint_label.configure(text=(
                "HOD Science → hod_science / science123\n"
                "HOD Humanities → hod_humanities / humanities123\n"
                "HOD Business → hod_business / business123\n"
                "Teacher → teacher / teacher123\n"
                "(Change password after first login)"
            ))
        else:
            self.title_label.configure(text="Student Login")
            self.student_btn.configure(fg_color=["#3a7ebf", "#1f538d"])
            self.staff_btn.configure(fg_color="gray", hover_color="#555555")
            self.hint_label.configure(text=(
                "Use the username and password given to you by your Teacher.\n"
                "After login you will choose your preferred department."
            ))
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.username_entry.focus()

    def do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return
        user = authenticate(username, password)
        if not user:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        role = user["role"]
        if self.login_mode == "staff":
            if role not in STAFF_ROLES:
                messagebox.showerror(
                    "Wrong Login Page",
                    "This is the Staff login.\nStudents should use the Student Login button."
                )
                return
        else:
            if role != "student":
                messagebox.showerror(
                    "Wrong Login Page",
                    "This is the Student login.\nHODs and Teachers should use Staff Login."
                )
                return

        self.on_login_success(user)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1000x680")
        self.minsize(860, 580)

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
        role = user["role"]

        if role in HOD_DEPARTMENT:
            dash = HODDashboard(self, user, self.show_login)
        elif role == "teacher":
            dash = TeacherDashboard(self, user, self.show_login)
        elif role == "student":
            dash = StudentDashboard(self, user, self.show_login)
        else:
            messagebox.showerror("Unknown Role", f"Unsupported role: {role}")
            self.show_login()
            return

        dash.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
