"""Student dashboard for SS1 Placement Test — preferred department selection"""
import customtkinter as ctk
from tkinter import messagebox
import json

from database import (
    get_questions_by_department, save_attempt, get_student_attempts,
    DEPARTMENTS, get_exam_minutes
)

PASS_MARK = 50


class StudentDashboard(ctk.CTkFrame):
    def __init__(self, master, user, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.test_questions = []
        self.current_index = 0
        self.current_answers = {}
        self.test_department = None
        self.timer_remaining = 0
        self.timer_id = None

        self.show_home()

    def clear(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        for w in self.winfo_children():
            w.destroy()

    def show_home(self):
        self.clear()
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text=f"Welcome, {self.user['full_name']}",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(10, 5))

        ctk.CTkLabel(
            frame, text="Choose your preferred department",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 5))
        ctk.CTkLabel(
            frame, text="You will receive questions based on the department you select.",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(pady=(0, 20))

        mins = get_exam_minutes()
        ctk.CTkLabel(
            frame, text=f"Exam duration: {mins} minutes  |  Pass mark: {PASS_MARK}%",
            font=ctk.CTkFont(size=12), text_color="gray"
        ).pack(pady=(0, 15))

        for dept in DEPARTMENTS:
            questions = get_questions_by_department(dept)
            btn_text = f"{dept}  ({len(questions)} questions)"
            ctk.CTkButton(
                frame, text=btn_text, width=300, height=40,
                command=lambda d=dept: self.start_test(d)
            ).pack(pady=8)

        # Past attempts
        attempts = get_student_attempts(self.user["id"])
        if attempts:
            ctk.CTkLabel(frame, text="Your Previous Results", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(25, 8))
            for a in attempts[:5]:
                eligible = "✓ Eligible" if a["percentage"] >= PASS_MARK else "✗ Not eligible"
                ctk.CTkLabel(
                    frame,
                    text=f"{a['department']}: {a['score']}/{a['total_questions']} ({a['percentage']}%) — {eligible}",
                    font=ctk.CTkFont(size=13)
                ).pack()

        ctk.CTkButton(
            frame, text="Logout", fg_color="#c0392b", hover_color="#a93226",
            command=self.on_logout, width=200
        ).pack(pady=30)

    def start_test(self, department):
        questions = get_questions_by_department(department)
        if not questions:
            messagebox.showwarning("No Questions", f"No questions available for {department} yet.")
            return
        if not messagebox.askyesno(
            "Start Test",
            f"You chose {department} as your preferred department.\n\n"
            f"Start the placement test for {department}?\n\n"
            f"Questions: {len(questions)}\n"
            f"Time limit: {get_exam_minutes()} minutes\n"
            f"Pass mark: {PASS_MARK}%"
        ):
            return

        self.test_department = department
        self.test_questions = questions
        self.current_index = 0
        self.current_answers = {}
        self.timer_remaining = get_exam_minutes() * 60
        self.show_test_ui()
        self.tick_timer()

    def show_test_ui(self):
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Top bar
        top = ctk.CTkFrame(self, height=50)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            top, text=f"{self.test_department} Placement Test",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10)

        self.timer_label = ctk.CTkLabel(
            top, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="#e74c3c"
        )
        self.timer_label.grid(row=0, column=2, padx=15)

        # Question area
        self.q_frame = ctk.CTkFrame(self)
        self.q_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        self.q_frame.grid_columnconfigure(0, weight=1)

        # Navigation
        nav = ctk.CTkFrame(self, fg_color="transparent")
        nav.grid(row=2, column=0, sticky="ew", padx=15, pady=10)

        self.prev_btn = ctk.CTkButton(nav, text="← Previous", width=120, command=self.prev_question)
        self.prev_btn.pack(side="left", padx=5)

        self.next_btn = ctk.CTkButton(nav, text="Next →", width=120, command=self.next_question)
        self.next_btn.pack(side="left", padx=5)

        ctk.CTkButton(
            nav, text="Submit Test", fg_color="#27ae60", hover_color="#1e8449",
            width=140, command=self.submit_test
        ).pack(side="right", padx=5)

        self.render_question()

    def tick_timer(self):
        if self.timer_remaining <= 0:
            messagebox.showwarning("Time Up", "Time is up! Your test will be submitted automatically.")
            self.submit_test(auto=True)
            return
        mins, secs = divmod(self.timer_remaining, 60)
        self.timer_label.configure(text=f"⏱ {mins:02d}:{secs:02d}")
        self.timer_remaining -= 1
        self.timer_id = self.after(1000, self.tick_timer)

    def render_question(self):
        for w in self.q_frame.winfo_children():
            w.destroy()

        q = self.test_questions[self.current_index]
        total = len(self.test_questions)

        ctk.CTkLabel(
            self.q_frame,
            text=f"Question {self.current_index + 1} of {total}",
            font=ctk.CTkFont(size=13), text_color="gray"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            self.q_frame, text=q["question_text"],
            font=ctk.CTkFont(size=16), wraplength=700, justify="left"
        ).pack(anchor="w", padx=20, pady=(5, 20))

        self.selected_var = ctk.StringVar(value=self.current_answers.get(q["id"], ""))

        for letter, key in zip("ABCD", ["option_a", "option_b", "option_c", "option_d"]):
            text = f"{letter}.  {q[key]}"
            rb = ctk.CTkRadioButton(
                self.q_frame, text=text, variable=self.selected_var, value=letter,
                font=ctk.CTkFont(size=14)
            )
            rb.pack(anchor="w", padx=30, pady=6)

        is_first = self.current_index == 0
        is_last = self.current_index == total - 1
        self.prev_btn.configure(state="disabled" if is_first else "normal")
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

    def submit_test(self, auto=False):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        self.save_current_answer()
        unanswered = len(self.test_questions) - len(self.current_answers)
        if not auto and unanswered > 0:
            if not messagebox.askyesno(
                "Unanswered Questions",
                f"You have {unanswered} unanswered question(s).\nSubmit anyway?"
            ):
                self.tick_timer()
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

        # Show detailed results + corrections immediately
        self.show_results_review(score, total, percentage)

    def show_results_review(self, score, total, percentage):
        """Display score summary and full question-by-question corrections."""
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        eligible = percentage >= PASS_MARK

        # ---- Summary header ----
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header, text="Test Completed — Results & Corrections",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        summary_color = "#27ae60" if eligible else "#c0392b"
        summary_text = (
            f"Department: {self.test_department}   |   "
            f"Score: {score} / {total}   |   "
            f"{percentage}%   |   "
            f"{'ELIGIBLE' if eligible else 'NOT ELIGIBLE'}"
        )
        ctk.CTkLabel(
            header, text=summary_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=summary_color
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # ---- Scrollable corrections ----
        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        scroll.grid_columnconfigure(0, weight=1)

        option_keys = {"A": "option_a", "B": "option_b", "C": "option_c", "D": "option_d"}

        for i, q in enumerate(self.test_questions, start=1):
            student_ans = self.current_answers.get(q["id"])  # may be None
            correct = q["correct_option"]
            is_correct = student_ans == correct

            card = ctk.CTkFrame(scroll, corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)
            card.grid_columnconfigure(0, weight=1)

            # Status badge
            if student_ans is None:
                status = "○ Not answered"
                status_color = "#7f8c8d"
            elif is_correct:
                status = "✓ Correct"
                status_color = "#27ae60"
            else:
                status = "✗ Wrong"
                status_color = "#c0392b"

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=12, pady=(10, 2))

            ctk.CTkLabel(
                top_row, text=f"Q{i}. {q['question_text']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                wraplength=650, justify="left"
            ).pack(side="left", anchor="w")

            ctk.CTkLabel(
                top_row, text=status,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=status_color
            ).pack(side="right", padx=8)

            # Show all options with highlighting
            for letter in "ABCD":
                opt_text = q[option_keys[letter]]
                prefix = f"{letter}. {opt_text}"

                if letter == correct and letter == student_ans:
                    # Student got it right
                    label_color = "#27ae60"
                    prefix = f"✓ {prefix}  (your answer — correct)"
                elif letter == correct:
                    # Correct answer (student missed it)
                    label_color = "#27ae60"
                    prefix = f"→ {prefix}  (correct answer)"
                elif letter == student_ans:
                    # Student's wrong choice
                    label_color = "#c0392b"
                    prefix = f"✗ {prefix}  (your answer)"
                else:
                    label_color = None
                    # normal option

                lbl = ctk.CTkLabel(
                    card, text=prefix,
                    font=ctk.CTkFont(size=13),
                    text_color=label_color,
                    wraplength=650, justify="left"
                )
                lbl.pack(anchor="w", padx=20, pady=1)

            # Spacer at bottom of card
            ctk.CTkLabel(card, text="", height=6).pack()

        # ---- Bottom button ----
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkButton(
            bottom, text="Back to Home",
            width=200, height=40,
            command=self.show_home
        ).pack()
