# System Configuration Summary

This document consolidates configuration details and diagnostics for development tools across two machines:

- **Home machine**
- **Work machine**

Diagnostics were extracted from batch script outputs, VS Code settings, PyCharm settings, Git Bash profiles, and Miniconda configurations.

---

## 1. PyCharm

### 1.1 Key Config/Settings Files
- `%APPDATA%\JetBrains\PyCharm2025.1\options\ide.general.xml`
- `%APPDATA%\JetBrains\PyCharm2025.1\options\editor.xml`
- `%APPDATA%\JetBrains\PyCharm2025.1\options\project.default.xml`
- `%APPDATA%\JetBrains\PyCharm2025.1\options\other.xml`
- `%APPDATA%\JetBrains\PyCharm2025.1\codestyles\Default.xml`

### 1.2 Application Executable Paths
- Example executable: `pycharm64.exe`

### 1.3 Configuration by Machine

#### 🏠 Home
- PyCharm Version: `2025.1.1.1`
- Executable Path: `C:\tony_apps\PyCharm_2025\bin\pycharm64.exe`
- Config Path: `C:\Users\tonyh\AppData\Roaming\JetBrains\PyCharm2025.1\`

#### 🏢 Work
- PyCharm Version: `2025.1.3.1`
- Executable Path: Not on PATH (no `where pycharm` output)
- Config Path: `C:\Users\theld\AppData\Roaming\JetBrains\PyCharm2025.1\`

---

## 2. Visual Studio Code

### 2.1 Key Config/Settings Files
- `%APPDATA%\Code\User\settings.json`
- `%APPDATA%\Code\User\snippets\`

### 2.2 Application Executable Paths
- Example: `Code.exe`

### 2.3 Configuration by Machine

#### 🏠 Home
- VS Code Version: `1.102.1 (user setup)`
- Executable Path: `C:\Users\tonyh\AppData\Local\Programs\Microsoft VS Code\Code.exe`
- Config Path: `C:\Users\tonyh\AppData\Roaming\Code\User\`

#### 🏢 Work
- VS Code Version: `1.100.2 (system setup)`
- Executable Path: Not on PATH (likely system install)
- Config Path: `C:\Users\theld\AppData\Roaming\Code\User\`

---

## 3. Cursor IDE

### 3.1 Key Config/Settings Files
- Reuses VS Code settings in `%APPDATA%\Code\User\`

### 3.2 Application Executable Paths
- Example: `Cursor.exe`

### 3.3 Configuration by Machine

#### 🏠 Home
- Cursor Version: `1.2.4 (user setup)`
- Executable Path: `C:\Users\tonyh\AppData\Local\Programs\cursor\Cursor.exe`

#### 🏢 Work
- Cursor Version: Not directly reported in diagnostics
- Executable Path: `C:\Users\theld\AppData\Local\Programs\cursor\resources\app\bin\cursor`

---

## 4. Miniconda (Conda Environment)

### 4.1 Key Config/Settings Files
- `%USERPROFILE%\.condarc`
- `%USERPROFILE%\miniconda3\envs\<env>\...`

### 4.2 Environment Commands Captured
- `conda info`
- `conda list`
- `conda env list`

### 4.3 Configuration by Machine

#### 🏠 Home
- Active Env: `mini_conda_02`
- `.condarc` found and dumped
- `where python` and `conda list` confirmed working

#### 🏢 Work
- Active Env: `mini_conda_02`
- `.condarc` file exists and was captured

---

## 5. Git Bash

### 5.1 Key Config/Settings Files
- `.bashrc`, `.bash_profile`, `.inputrc`, `.gitconfig`, `.minttyrc`, `.condarc`

### 5.2 Configuration by Machine

#### 🏠 Home
- Files found:
  - `.bashrc`
  - `.bash_profile`
  - `.inputrc`
  - `.gitconfig`
  - `.minttyrc`
  - `.condarc`

#### 🏢 Work
- Same list of files as home
- Contents were captured in `gitbash_work_profile_dump.txt`

---

## 6. Git + Extensions

### 6.1 Key Diagnostic Outputs
- `where git`
- `git --version`
- `git config --list`
- VS Code Extensions: via `code --list-extensions`

### 6.2 Configuration by Machine

#### 🏠 Home
- Git version confirmed in diagnostics
- Extensions captured in `dump_git_vscode_info_home.txt`

#### 🏢 Work
- Git installed and active
- Extensions captured

---

## Notes

- Paths and versions were verified using script-based diagnostics. No assumptions were made.
- Paths like `%APPDATA%`, `%USERPROFILE%`, etc., resolve differently on each machine.
- Most tools rely on Roaming profiles for persistent configuration across sessions.
