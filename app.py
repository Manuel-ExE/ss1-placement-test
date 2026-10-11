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
