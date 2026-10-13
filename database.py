"""
Database module — Lagos State Senior Model College Ojo
SS1 Placement Test

Roles:
  hod_science      — HOD of Science (sets Science questions)
  hod_humanities   — HOD of Humanities / Art (sets Art questions)
  hod_business     — HOD of Business / Commercial (sets Commercial questions)
  teacher          — manages students
  student          — takes placement tests
"""
import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placement_test.db")

DEPARTMENTS = ["Science", "Art", "Commercial"]

# Map role → department the HOD controls
HOD_DEPARTMENT = {
    "hod_science": "Science",
    "hod_humanities": "Art",
    "hod_business": "Commercial",
}

ROLE_LABELS = {
    "hod_science": "HOD of Science",
    "hod_humanities": "HOD of Humanities",
    "hod_business": "HOD of Business",
    "teacher": "Teacher",
    "student": "Student",
}

DEFAULT_EXAM_MINUTES = 30
PASS_MARK = 50

# Default accounts created on first run
DEFAULT_ACCOUNTS = [
    ("hod_science", "science123", "HOD of Science", "hod_science"),
    ("hod_humanities", "humanities123", "HOD of Humanities", "hod_humanities"),
    ("hod_business", "business123", "HOD of Business", "hod_business"),
    ("teacher", "teacher123", "Class Teacher", "teacher"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN (
                'hod_science', 'hod_humanities', 'hod_business', 'teacher', 'student'
            )),
            admission_no TEXT UNIQUE,
            class TEXT DEFAULT 'SS1',
            state TEXT,
            lga TEXT,
            date_of_birth TEXT,
            sex TEXT,
            parents_number TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Migrate older DBs that may lack the new student columns
    for col, typedef in [
        ("state", "TEXT"),
        ("lga", "TEXT"),
        ("date_of_birth", "TEXT"),
        ("sex", "TEXT"),
        ("parents_number", "TEXT"),
    ]:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col} {typedef}")
        except sqlite3.OperationalError:
            pass

    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            department TEXT NOT NULL CHECK(department IN ('Science', 'Art', 'Commercial')),
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL CHECK(correct_option IN ('A', 'B', 'C', 'D')),
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            department TEXT NOT NULL,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            answers_json TEXT,
            taken_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM settings WHERE key = 'exam_minutes'")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("exam_minutes", str(DEFAULT_EXAM_MINUTES))
        )
        conn.commit()

    # Seed default staff accounts if none exist
    cur.execute(
        "SELECT COUNT(*) FROM users WHERE role IN "
        "('hod_science','hod_humanities','hod_business','teacher')"
    )
    if cur.fetchone()[0] == 0:
        for username, password, full_name, role in DEFAULT_ACCOUNTS:
            cur.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, hash_password(password), full_name, role)
            )
        conn.commit()

    conn.close()


def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, str(value))
    )
    conn.commit()
    conn.close()


def get_exam_minutes() -> int:
    try:
        return int(get_setting("exam_minutes", str(DEFAULT_EXAM_MINUTES)))
    except ValueError:
        return DEFAULT_EXAM_MINUTES


def authenticate(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE username = ? AND password_hash = ?",
        (username.strip(), hash_password(password))
    )
    user = cur.fetchone()
    conn.close()
    return dict(user) if user else None


def add_student(username, password, full_name, admission_no,
                state="", lga="", date_of_birth="", sex="", parents_number=""):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO users
               (username, password_hash, full_name, role, admission_no,
                state, lga, date_of_birth, sex, parents_number)
               VALUES (?, ?, ?, 'student', ?, ?, ?, ?, ?, ?)""",
            (username.strip(), hash_password(password), full_name.strip(),
             admission_no.strip(), state.strip(), lga.strip(),
             date_of_birth.strip(), sex.strip(), parents_number.strip())
        )
        conn.commit()
        return True, "Student added successfully"
    except sqlite3.IntegrityError:
        return False, "Error: username or admission number already exists"
    finally:
        conn.close()


def update_student(student_id, full_name, admission_no, password=None,
                   state="", lga="", date_of_birth="", sex="", parents_number=""):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if password:
            cur.execute(
                """UPDATE users SET full_name=?, admission_no=?, password_hash=?,
                   state=?, lga=?, date_of_birth=?, sex=?, parents_number=?
                   WHERE id=? AND role='student'""",
                (full_name.strip(), admission_no.strip(), hash_password(password),
                 state.strip(), lga.strip(), date_of_birth.strip(),
                 sex.strip(), parents_number.strip(), student_id)
            )
        else:
            cur.execute(
                """UPDATE users SET full_name=?, admission_no=?,
                   state=?, lga=?, date_of_birth=?, sex=?, parents_number=?
                   WHERE id=? AND role='student'""",
                (full_name.strip(), admission_no.strip(),
                 state.strip(), lga.strip(), date_of_birth.strip(),
                 sex.strip(), parents_number.strip(), student_id)
            )
        conn.commit()
        return True, "Student updated"
    except sqlite3.IntegrityError:
        return False, "Admission number already exists"
    finally:
        conn.close()


def delete_student(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM attempts WHERE student_id = ?", (student_id,))
    cur.execute("DELETE FROM users WHERE id = ? AND role = 'student'", (student_id,))
    conn.commit()
    conn.close()
    return True


def get_all_students():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, username, full_name, admission_no, class,
                  state, lga, date_of_birth, sex, parents_number, created_at
           FROM users WHERE role='student' ORDER BY full_name"""
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_student_by_id(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=? AND role='student'", (student_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def bulk_add_students(rows: list) -> tuple:
    ok = fail = 0
    errors = []
    for i, row in enumerate(rows, start=1):
        success, msg = add_student(
            row.get("username", ""),
            row.get("password", ""),
            row.get("full_name", ""),
            row.get("admission_no", ""),
            row.get("state", ""),
            row.get("lga", ""),
            row.get("date_of_birth", ""),
            row.get("sex", ""),
            row.get("parents_number", ""),
        )
        if success:
            ok += 1
        else:
            fail += 1
            errors.append(f"Row {i}: {msg}")
    return ok, fail, errors


def add_question(department, question_text, option_a, option_b,
                 option_c, option_d, correct_option, created_by):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO questions
           (department, question_text, option_a, option_b, option_c, option_d,
            correct_option, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (department, question_text.strip(), option_a.strip(), option_b.strip(),
         option_c.strip(), option_d.strip(), correct_option.upper(), created_by)
    )
    conn.commit()
    qid = cur.lastrowid
    conn.close()
    return qid


def update_question(qid, department, question_text, option_a, option_b,
                    option_c, option_d, correct_option):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE questions SET department=?, question_text=?, option_a=?, option_b=?,
           option_c=?, option_d=?, correct_option=? WHERE id=?""",
        (department, question_text.strip(), option_a.strip(), option_b.strip(),
         option_c.strip(), option_d.strip(), correct_option.upper(), qid)
    )
    conn.commit()
    conn.close()


def delete_question(qid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id=?", (qid,))
    conn.commit()
    conn.close()


def get_questions_by_department(department: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM questions WHERE department=? ORDER BY id", (department,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_all_questions():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM questions ORDER BY department, id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_question_count_by_dept():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT department, COUNT(*) as cnt FROM questions GROUP BY department")
    result = {r["department"]: r["cnt"] for r in cur.fetchall()}
    conn.close()
    return result


def save_attempt(student_id, department, score, total, answers_json):
    percentage = round((score / total) * 100, 2) if total > 0 else 0
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO attempts
           (student_id, department, score, total_questions, percentage, answers_json)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (student_id, department, score, total, percentage, answers_json)
    )
    conn.commit()
    aid = cur.lastrowid
    conn.close()
    return aid, percentage


def get_student_attempts(student_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM attempts WHERE student_id=? ORDER BY taken_at DESC",
        (student_id,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_all_attempts():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT a.*, u.full_name, u.admission_no
           FROM attempts a JOIN users u ON a.student_id = u.id
           ORDER BY a.taken_at DESC"""
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_attempts_by_department(department: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT a.*, u.full_name, u.admission_no
           FROM attempts a JOIN users u ON a.student_id = u.id
           WHERE a.department=? ORDER BY a.taken_at DESC""",
        (department,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def change_password(user_id: int, new_password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET password_hash=? WHERE id=?",
        (hash_password(new_password), user_id)
    )
    conn.commit()
    conn.close()


def get_analytics():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE role='student'")
    total_students = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM attempts")
    total_attempts = cur.fetchone()[0]
    dept_stats = {}
    for dept in DEPARTMENTS:
        cur.execute(
            """SELECT COUNT(*), AVG(percentage),
                      SUM(CASE WHEN percentage >= 50 THEN 1 ELSE 0 END)
               FROM attempts WHERE department = ?""",
            (dept,)
        )
        row = cur.fetchone()
        count = row[0] or 0
        avg = round(row[1], 1) if row[1] is not None else 0
        passed = row[2] or 0
        pass_rate = round((passed / count) * 100, 1) if count > 0 else 0
        dept_stats[dept] = {
            "attempts": count, "average": avg,
            "passed": passed, "pass_rate": pass_rate,
        }
    conn.close()
    return {
        "total_students": total_students,
        "total_attempts": total_attempts,
        "departments": dept_stats,
    }
