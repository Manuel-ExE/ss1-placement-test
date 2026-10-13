# SS1 Placement Test — Lagos State Senior Model College Ojo

Desktop placement test for SS1 students. Students choose a preferred department and take questions set by the department HOD.

## Roles

| Role | Username (default) | Password | Responsibility |
|------|--------------------|----------|----------------|
| HOD of Science | `hod_science` | `science123` | Set Science questions |
| HOD of Humanities | `hod_humanities` | `humanities123` | Set Art / Humanities questions |
| HOD of Business | `hod_business` | `business123` | Set Commercial / Business questions |
| Teacher | `teacher` | `teacher123` | Create & manage students |
| Student | (created by teacher) | (set by teacher) | Choose department & take test |

**Change default passwords after first login.**

## Question format (HODs)

```
What is photosynthesis
A  Plants make their food using sunlight
B  Car
C  Sun
D  Moon
Answer: A
```

## Student fields (Teacher)

- Full name, admission number, username, password  
- State, LGA, date of birth, sex, parents’ phone number  

## Run

```bash
pip install -r requirements.txt
python app.py
```

If you previously used an older version of this app, delete `placement_test.db` once so the new roles and columns are created cleanly.

## Build Windows EXE

```bat
pip install pyinstaller customtkinter
pyinstaller --noconfirm --onefile --windowed --name SS1_Placement_Test app.py
```

Then use Inno Setup with `installer.iss` for a Setup installer.
