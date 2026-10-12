"""Student dashboard for SS1 Placement Test — preferred department selection"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import json
from datetime import datetime

from database import (
    get_questions_by_department, save_attempt, get_student_attempts,
    DEPARTMENTS, get_exam_minutes
)

PASS_MARK = 50
SCHOOL_NAME = "Lagos State Senior Model College Ojo"

# HOD remarks shown after a student finishes a department exam
HOD_REMARKS = {
    "Science": {
        "title": "HOD of Science",
        "eligible": (
            "Congratulations! You have met the requirements for the Science department. "
            "We look forward to nurturing your analytical and scientific skills. "
            "Welcome to the Science stream — work hard, stay curious, and aim high."
        ),
        "not_eligible": (
            "Thank you for attempting the Science placement test. Your score did not meet "
            "the minimum requirement this time. Please review the corrections, practice more, "
            "and you may retake the test. The Science department remains open to dedicated students."
        ),
    },
    "Art": {
        "title": "HOD of Humanities",
        "eligible": (
            "Well done! You have qualified for the Humanities (Art) department. "
            "We celebrate your interest in literature, history, and the arts. "
            "Welcome to the Humanities stream — express yourself, think critically, and thrive."
        ),
        "not_eligible": (
            "Thank you for sitting the Humanities placement test. You did not reach the pass mark "
            "on this attempt. Study the corrections carefully and consider retaking the exam. "
            "The Humanities department welcomes students who are ready to improve and grow."
        ),
    },
    "Commercial": {
        "title": "HOD of Business",
        "eligible": (
            "Excellent performance! You have been cleared for the Business (Commercial) department. "
            "We are excited to develop your skills in commerce, accounting, and entrepreneurship. "
            "Welcome to the Business stream — think strategically and build your future."
        ),
        "not_eligible": (
            "Thank you for taking the Business placement test. Your score is below the required "
            "pass mark. Review the corrections, strengthen your weak areas, and you may retry. "
            "The Business department encourages persistence and continuous improvement."
        ),
    },
}


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
        self.last_score = 0
        self.last_total = 0
        self.last_percentage = 0.0

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

        self.q_frame = ctk.CTkFrame(self)
        self.q_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        self.q_frame.grid_columnconfigure(0, weight=1)

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

        self.last_score = score
        self.last_total = total
        self.last_percentage = percentage
        self.show_results_review(score, total, percentage)

    def show_results_review(self, score, total, percentage):
        self.clear()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        eligible = percentage >= PASS_MARK

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
        ).pack(anchor="w", padx=10, pady=(0, 5))

        hod = HOD_REMARKS.get(self.test_department, {})
        if hod:
            remark_text = hod["eligible"] if eligible else hod["not_eligible"]
            hod_frame = ctk.CTkFrame(header, corner_radius=8, fg_color=("#e8f5e9" if eligible else "#fce4ec"))
            hod_frame.pack(fill="x", padx=10, pady=(5, 10))
            ctk.CTkLabel(
                hod_frame, text=f"📌 Remark from the {hod['title']}",
                font=ctk.CTkFont(size=13, weight="bold")
            ).pack(anchor="w", padx=12, pady=(8, 2))
            ctk.CTkLabel(
                hod_frame, text=remark_text,
                font=ctk.CTkFont(size=12),
                wraplength=700, justify="left"
            ).pack(anchor="w", padx=12, pady=(0, 10))

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=5)
        scroll.grid_columnconfigure(0, weight=1)

        option_keys = {"A": "option_a", "B": "option_b", "C": "option_c", "D": "option_d"}

        for i, q in enumerate(self.test_questions, start=1):
            student_ans = self.current_answers.get(q["id"])
            correct = q["correct_option"]
            is_correct = student_ans == correct

            card = ctk.CTkFrame(scroll, corner_radius=8)
            card.pack(fill="x", pady=6, padx=5)

            if student_ans is None:
                status, status_color = "○ Not answered", "#7f8c8d"
            elif is_correct:
                status, status_color = "✓ Correct", "#27ae60"
            else:
                status, status_color = "✗ Wrong", "#c0392b"

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

            for letter in "ABCD":
                opt_text = q[option_keys[letter]]
                prefix = f"{letter}. {opt_text}"
                if letter == correct and letter == student_ans:
                    label_color = "#27ae60"
                    prefix = f"✓ {prefix}  (your answer — correct)"
                elif letter == correct:
                    label_color = "#27ae60"
                    prefix = f"→ {prefix}  (correct answer)"
                elif letter == student_ans:
                    label_color = "#c0392b"
                    prefix = f"✗ {prefix}  (your answer)"
                else:
                    label_color = None
                ctk.CTkLabel(
                    card, text=prefix, font=ctk.CTkFont(size=13),
                    text_color=label_color, wraplength=650, justify="left"
                ).pack(anchor="w", padx=20, pady=1)

            ctk.CTkLabel(card, text="", height=6).pack()

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=15, pady=15)

        ctk.CTkButton(
            bottom, text="🔄 Retry Exam", width=160, height=40,
            fg_color="#2980b9", hover_color="#1f6dad", command=self.retry_exam
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            bottom, text="🖨 Print / Save Results", width=180, height=40,
            fg_color="#8e44ad", hover_color="#7d3c98", command=self.print_results
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            bottom, text="Back to Home", width=160, height=40, command=self.show_home
        ).pack(side="right", padx=5)

    def retry_exam(self):
        dept = self.test_department
        if not dept:
            self.show_home()
            return
        if messagebox.askyesno(
            "Retry Exam",
            f"Retake the {dept} placement test?\n\n"
            "Your previous attempt is already saved.\n"
            "A new attempt will be recorded when you finish."
        ):
            self.start_test(dept)

    def print_results(self):
        score = self.last_score
        total = self.last_total
        percentage = self.last_percentage
        eligible = percentage >= PASS_MARK
        option_keys = {"A": "option_a", "B": "option_b", "C": "option_c", "D": "option_d"}

        lines = []
        lines.append("=" * 60)
        lines.append(f"  {SCHOOL_NAME}")
        lines.append("  SS1 Placement Test — Results & Corrections")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Student Name : {self.user.get('full_name', '')}")
        lines.append(f"Admission No : {self.user.get('admission_no') or 'N/A'}")
        lines.append(f"Department   : {self.test_department}")
        lines.append(f"Date         : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("")
        lines.append(f"Score        : {score} / {total}")
        lines.append(f"Percentage   : {percentage}%")
        lines.append(f"Pass Mark    : {PASS_MARK}%")
        lines.append(f"Result       : {'ELIGIBLE' if eligible else 'NOT ELIGIBLE'}")
        lines.append("")
        hod = HOD_REMARKS.get(self.test_department, {})
        if hod:
            remark_text = hod["eligible"] if eligible else hod["not_eligible"]
            lines.append("-" * 60)
            lines.append(f"REMARK FROM THE {hod['title'].upper()}")
            lines.append("-" * 60)
            lines.append(remark_text)
            lines.append("")
        lines.append("-" * 60)
        lines.append("QUESTION REVIEW")
        lines.append("-" * 60)

        for i, q in enumerate(self.test_questions, start=1):
            student_ans = self.current_answers.get(q["id"])
            correct = q["correct_option"]
            if student_ans is None:
                status = "NOT ANSWERED"
            elif student_ans == correct:
                status = "CORRECT"
            else:
                status = "WRONG"

            lines.append("")
            lines.append(f"Q{i}. {q['question_text']}")
            lines.append(f"    Status: {status}")
            for letter in "ABCD":
                opt = q[option_keys[letter]]
                mark = ""
                if letter == correct:
                    mark = "  ← CORRECT ANSWER"
                if letter == student_ans:
                    mark += "  ← YOUR ANSWER"
                lines.append(f"    {letter}. {opt}{mark}")

        lines.append("")
        lines.append("=" * 60)
        report = "\n".join(lines)

        win = ctk.CTkToplevel(self)
        win.title("Print / Save Results")
        win.geometry("640x520")
        win.transient(self.winfo_toplevel())

        ctk.CTkLabel(
            win, text="Results Report (ready to print or save)",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(pady=(12, 6))

        text = ctk.CTkTextbox(win, width=600, height=380, font=ctk.CTkFont(family="Courier", size=12))
        text.pack(padx=15, pady=5)
        text.insert("1.0", report)
        text.configure(state="disabled")

        def do_save():
            path = filedialog.asksaveasfilename(
                title="Save Results Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"result_{self.user.get('admission_no') or self.user['id']}_{self.test_department}.txt"
            )
            if path:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(report)
                messagebox.showinfo("Saved", f"Report saved to:\n{path}\n\nYou can open it and print from any text editor.")

        btn_row = ctk.CTkFrame(win, fg_color="transparent")
        btn_row.pack(pady=10)
        ctk.CTkButton(btn_row, text="Save as File (then print)", width=200, command=do_save).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="Close", width=100, command=win.destroy).pack(side="left", padx=8)
