# SS1 Department Placement Test System

**Lagos State Senior Model College, Ojo**

Offline-first placement examination app for Science, Art, and Commercial departments. The desktop app uses the supplied HTML interface in Electron and stores application data locally in the browser's IndexedDB.

## Features

- Teacher and student portals, question banks, examinations, results, reports, backup/restore, and dark mode
- Timed examinations with a persisted deadline, answer autosave, resume support, and automatic submission on expiry
- First-run teacher account setup; there is no built-in default admin password
- Passwords hashed with PBKDF2-HMAC-SHA-256, a random per-account salt, and 310,000 iterations; legacy 100,000-iteration hashes remain verifiable
- Student CSV exports and full backups do not include plaintext passwords

## Run for development

Requirements: Node.js 20+ and npm.

```bash
npm ci
npm start
```

## Build the Windows installer

```bash
npm ci
npm run dist
```

The installer is written to `dist/SS1_Placement_Test_Setup.exe`. GitHub Actions runs the same `npm run dist` command on Windows when manually dispatched or when a `v*` tag is pushed.

`run.bat` and `build_exe.bat` are Windows convenience wrappers for these npm commands. `installer.iss` and the Python/CustomTkinter source files are retained as historical legacy files; they are not part of the supported app or release build.

## Data and migration notes

App data is stored locally per Windows user in Electron/Chromium IndexedDB. Back up data from the app before changing devices or clearing app data. Existing accounts in this app retain their current passwords; old PBKDF2 records without iteration metadata are checked using 100,000 iterations. On startup, any legacy `passwordPlain` fields are removed from local IndexedDB. Student CSV exports no longer include a password column; set or reset student passwords in the app.

The older Python application used a separate SQLite database and is not automatically imported into the Electron app. Keep a copy of any existing `placement_test.db` before moving to this version.
