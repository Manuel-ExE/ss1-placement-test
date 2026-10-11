# Lagos State Senior Model College Ojo  
## SS1 Placement Test Application

A Windows desktop application for placing SS1 students into **Science**, **Art**, or **Commercial** departments.

---

### Features

**Teachers (Admin)**
- Secure login
- Add / edit / delete student accounts
- Create multiple-choice questions separately for each department
- View all placement test results
- Change admin password

**Students**
- Login with credentials provided by teachers
- Choose which department test to take
- Answer questions one-by-one
- Instant result with score and eligibility (default pass mark: 50%)
- View previous attempts

---

### Default Admin Account
- **Username:** `admin`  
- **Password:** `admin123`  

**Please change the password after first login.**

---

## Option 1: Run with Python (for development)

1. Install Python 3.10+ from https://www.python.org (tick “Add to PATH”)
2. Open Command Prompt in this folder and run:

```bash
pip install -r requirements.txt
python app.py
```

---

## Option 2: Create a Standalone Windows EXE (Recommended)

This creates a single `.exe` file that works on any Windows computer **without installing Python**.

### Method A – Build on your own Windows computer

1. Make sure Python is installed.
2. Double-click **`build_exe.bat`**
3. Wait 1–3 minutes.
4. Your executable will appear here:  
   `dist\SS1_Placement_Test.exe`

You can copy this `.exe` to any computer and run it.

### Method B – Automatic build with GitHub (Recommended)

1. On GitHub, go to the **Actions** tab.
2. Click **Build Windows EXE** → **Run workflow** → **Run workflow**.
3. When it finishes, download the EXE from the **Artifacts** section.

**Even better – Create a public download link:**

1. Go to **Releases** → **Create a new release**
2. Tag version: `v1.0`
3. Title: `SS1 Placement Test v1.0`
4. Click **Publish release**
5. GitHub Actions will automatically build the EXE and attach it to the release.

---

### Important Notes

- The database file (`placement_test.db`) is created automatically the first time the app runs.
- Each computer will have its own separate database.
- If you want all computers to share the same data, put the `.exe` and the `.db` file on a shared network folder.

---

### Files Overview

| File | Purpose |
|------|---------|
| `app.py` | Main application |
| `database.py` | Database logic |
| `build_exe.bat` | Builds the Windows EXE |
| `run.bat` | Runs the app with Python |
| `.github/workflows/build-windows.yml` | Automatic GitHub build |
| `requirements.txt` | Python packages |
