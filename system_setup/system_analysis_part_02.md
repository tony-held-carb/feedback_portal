# 🖥️ System Setups: Home, Work, and EC2 Machines

This document standardizes environment, IDE, and configuration setups across three systems:

- **Home** (Windows, Admin Access)
- **Work** (Windows, No Admin Access)
- **EC2** (Linux, No Admin Access)

---

## 🧭 IDE Versions & Paths

| IDE         | Home                                                                                   | Work                                                                                     | EC2  |
|-------------|------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|-------|
| **PyCharm** | ✅ `C:\tony_apps\PyCharm_2025\bin\pycharm64.exe`<br>**Version:** 2025.1.1.1<br>**Build:** PY-251.25410.159<br>**Built:** 2025-05-14 | ✅ Installed (location not exact)<br>**Version:** 2025.1.3.1<br>**Build:** PY-251.26927.90<br>**Built:** 2025-07-10 | N/A   |
| **VS Code** | ✅ `C:\Users\tonyh\AppData\Local\Programs\Microsoft VS Code\Code.exe`<br>**Version:** 1.102.1 (user setup) | ✅ `C:\Users\theld\AppData\Local\Programs\Microsoft VS Code\Code.exe`<br>**Version:** 1.100.2 (system setup) | N/A   |
| **Cursor**  | ✅ `C:\Users\tonyh\AppData\Local\Programs\cursor\Cursor.exe`<br>**Version:** 1.2.4<br>**VSCode Core:** 1.99.3 | ✅ `C:\Users\theld\AppData\Local\Programs\cursor\Cursor.exe`<br>**Version:** 1.2.4<br>**VSCode Core:** 1.99.3 | N/A   |

---

## 🗂️ Key Configuration Files

### PyCharm Settings Extracted

| File                  | Exists | Machine | Path                                                                                       |
|-----------------------|--------|---------|--------------------------------------------------------------------------------------------|
| `ide.general.xml`     | ✅     | Work    | `%APPDATA%\JetBrains\PyCharm2025.1\options\ide.general.xml`                             |
| `editor.xml`          | ✅     | Work    | `%APPDATA%\JetBrains\PyCharm2025.1\options\editor.xml`                                  |
| `project.default.xml` | ✅     | Work    | `%APPDATA%\JetBrains\PyCharm2025.1\options\project.default.xml`                         |
| `other.xml`           | ✅     | Work    | `%APPDATA%\JetBrains\PyCharm2025.1\options\other.xml`                                   |
| `Default.xml`         | ✅     | Work    | `%APPDATA%\JetBrains\PyCharm2025.1\codestyles\Default.xml`                              |

### VS Code & Cursor

| File/Directory             | Exists | Machine | Path                                                                                      |
|---------------------------|--------|---------|-------------------------------------------------------------------------------------------|
| `settings.json`           | ✅     | Work    | `%APPDATA%\Code\User\settings.json` (basic config)                                      |
| `snippets/`               | ✅     | Work    | `%APPDATA%\Code\User\snippets\` (empty)                                                 |
| `workspaceStorage/`       | ✅     | Work    | `%APPDATA%\Code\User\workspaceStorage\` (used)                                          |
| Cursor binary             | ✅     | Work    | `C:\Users\theld\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd`       |
| VS Code binary            | ✅     | Work    | `C:\Users\theld\AppData\Local\Programs\Microsoft VS Code\Code.exe`                  |
| Cursor config root        | ✅     | Work    | `%APPDATA%\Cursor\`                                                                       |

---

## ⚙️ Git Bash Dotfiles (Work)

| File           | Present | Notes                     |
|----------------|---------|---------------------------|
| `.bashrc`      | ❌      | Not found                 |
| `.bash_profile`| ❌      | Not found                 |
| `.profile`     | ❌      | Not found                 |
| `.inputrc`     | ❌      | Not found                 |
| `.gitconfig`   | ✅      | Present and populated     |

---

## 🐍 Miniconda

### Common Setup
- Both systems use **Miniconda** only.
- Primary environment: `mini_conda_02`

### .condarc

| Machine | Exists | Path                      | Notes                          |
|---------|--------|---------------------------|---------------------------------|
| Work    | ✅     | `%USERPROFILE%\.condarc`  | Customized                     |
| Home    | ✅     | `%USERPROFILE%\.condarc`  | Customized                     |

### Conda Environments
Both systems have these environments:
- `base`
- `mini_conda_01`
- `mini_conda_02` *(active)*

---

## 📦 VS Code Extensions Summary (Home & Work)

- Shared extensions detected via `code --list-extensions`
- Full lists stored in `dump_git_vscode_info_home.txt` and `..._work.txt`
- Common tools: GitHub Copilot, Python, Jupyter, SQLite, Bash

---

## 📁 Output Diagnostics Collected

Diagnostic scripts used:
- `collect_env_diagnostics_v5.bat`
- `dump_gitbash_profile.sh`
- `dump_git_vscode_info.bat`
- `dump_conda_config.bat`

Diagnostics from each machine stored in:
- `*_home.txt`
- `*_work.txt`

---

## ✅ Next Steps
- Sync environments or plugins as needed.
- Generate diff summaries across files.
- Add EC2 system analysis once diagnostics are available.

Let me know if you'd like a markdown export with frontmatter for MkDocs or GitHub publishing.
