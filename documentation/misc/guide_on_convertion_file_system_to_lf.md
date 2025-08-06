# convert\_to\_lf.md

# ✅ Overview: Converting the Entire Repository to Use LF Line Endings

This guide documents the process of standardizing **all text files in your repository** to use **LF (Unix-style) line
endings** across all platforms and tools. This is particularly important for projects that:

- Run on **WSL**, **Linux (EC2)**, and **Windows**
- Involve Bash scripts (`.sh`), Python (`.py`), Markdown (`.md`), YAML, and other text formats
- Must avoid interpreter errors caused by CRLF endings (e.g., `/bin/bash^M: bad interpreter`)

---

## 🛠️ Step 1: Configure `.gitattributes` to Enforce LF in Git

Create or update a file named `.gitattributes` in the root of your repository with the following contents:

```gitattributes
# .gitattributes
# ----------------------------------------
# This file instructs Git to normalize all text files to LF on commit
# and ensures consistent behavior across platforms.
#
# `text=auto` lets Git detect text files automatically.
# `eol=lf` enforces LF line endings on commit.
# ----------------------------------------

* text=auto eol=lf
```

This ensures:

- All text files are stored with **LF** endings in the Git repo.
- Platform-specific line ending conversions are disabled.

---

## ⚙️ Step 2: Set Git Behavior on All Machines

Run this command on **every development machine**, regardless of OS:

```bash
git config --global core.autocrlf input
```

### 📘 What this does:

- ``: Git will convert CRLF to LF **on commit**, but will **not alter line endings on checkout**.
- Ensures that all files remain LF on disk and in Git, even on Windows.

> ❗ Do **not** use `core.autocrlf=true`, as it would reintroduce CRLF on Windows checkouts.

---

## 🧾 Step 3: Create an `.editorconfig` File

Create a file named `.editorconfig` in your project root:

```ini
# .editorconfig
# ----------------------------------------
# EditorConfig helps maintain consistent line endings
# and file formatting across editors that support it.
# ----------------------------------------

root = true

[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
trim_trailing_whitespace = true
```

This ensures that every editor you use (VS Code, PyCharm, Cursor, Sublime, etc.) enforces LF and other formatting rules.

> Most modern IDEs automatically recognize `.editorconfig` without any plugins.

---

## 🧠 Step 4: Editor Configurations (LF Defaults)

### ✅ VS Code (`settings.json`)

Open your settings via `Ctrl + Shift + P` → `Preferences: Open Settings (JSON)` and add:

```json
{
  // Use LF line endings for all new files
  "files.eol": "\n"
}
```

### ✅ PyCharm / IntelliJ

1. Go to **Settings → Editor → Code Style**
2. Set **Line separator**: `Unix and macOS (\n)`
3. Apply the setting project-wide

Then trigger the reformat action:

- Right-click your project folder → **Reformat Code**
- Check **Include subdirectories**

### ✅ Cursor (VS Code-based)

Cursor inherits VS Code settings. Use the same `"files.eol": "\n"` in `settings.json`.

### ✅ Sublime Text

Open **Preferences → Settings**, and add:

```json
{
  // Use LF as default line endings
  "default_line_ending": "unix"
}
```

---

## 🔁 Step 5: Normalize Existing Files (Optional Cleanup)

To convert any existing files from CRLF to LF on disk, run the following from WSL or Linux:

```bash
# Recursively convert all text files to LF using dos2unix
sudo apt install dos2unix
find . -type f \( -name "*.sh" -o -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.yml" \) -exec dos2unix {} +

Tony ran the following with success to convert all text files to LF:
find . -type f -not -path "./.git/*" -not -path "./.idea/*" \( -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name "*.json" -o -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.sh" -o -name "*.yml" -o -name "*.yaml" -o -name "*.xml" -o -name "*.sql" -o -name "*.ini" -o -name "*.cfg" -o -name "*.conf" \) -exec dos2unix {} \;

```

Or use `sed` if `dos2unix` is unavailable:

```bash
# Remove carriage returns from all text files
find . -type f -exec sed -i 's/\r$//' {} +
```

Then re-commit any changed files.

---

## ✅ Summary

| Step                      | Purpose                          |
|---------------------------|----------------------------------|
| `.gitattributes`          | Normalize line endings in Git    |
| `core.autocrlf=input`     | Prevent CRLF pollution           |
| `.editorconfig`           | Enforce LF in all editors        |
| Editor settings           | Ensure new files use LF          |
| Optional conversion tools | Normalize existing files on disk |

By following these steps, you will have a clean, consistent LF-only development environment across Windows, WSL, and
Linux.

Let me know if you'd like to add a validation script that checks for CRLF files during CI or pre-commit.

## Checklist
