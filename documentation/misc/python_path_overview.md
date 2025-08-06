# PYTHONPATH Overview for feedback_portal

This document summarizes best practices and key points for setting and managing the `PYTHONPATH` environment variable
for the CalSMP Operator Feedback Portal project.

---

## What is PYTHONPATH?

- `PYTHONPATH` is an environment variable that tells Python where to look for modules/packages when importing.
- It should include the root directory of your top-level package(s).

---

## Recommended Value for This Project

- **Best value:**
  ```
  D:\local\cursor\feedback_portal\source\production
  ```
  This is the directory containing the `arb` package and main source code.

---

## How to Set PYTHONPATH

### Temporary (Current Session, CMD)

- **Overwrite:**
  ```cmd
  set PYTHONPATH=D:\local\cursor\feedback_portal\source\production
  ```
- **Prepend (recommended if you have other paths):**
  ```cmd
  set PYTHONPATH=D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
  ```
- **Append:**
  ```cmd
  set PYTHONPATH=%PYTHONPATH%;D:\local\cursor\feedback_portal\source\production
  ```

### Permanent (Windows GUI)

1. Open **System Properties** → **Environment Variables**.
2. Under **User variables**, find or create `PYTHONPATH`.
3. Set the value to:
    - To prepend:
      ```
      D:\local\cursor\feedback_portal\source\production;%PYTHONPATH%
      ```
    - To append:
      ```
      %PYTHONPATH%;D:\local\cursor\feedback_portal\source\production
      ```
    - If not set previously, just use your project path.
4. Click OK and restart your terminal/IDE.

### Permanent (Command Line)

- Overwrite:
  ```cmd
  setx PYTHONPATH "D:\local\cursor\feedback_portal\source\production"
  ```
- To append, check the current value first:
  ```cmd
  echo %PYTHONPATH%
  setx PYTHONPATH "D:\local\cursor\feedback_portal\source\production;[old value]"
  ```

---

## Key Points & Troubleshooting

- **Order matters:** Prepending makes your project take precedence.
- **Trailing semicolon (`;`):** Harmless, but can be removed for tidiness.
- **Multiple set/appends in one session:** Avoid, as it can duplicate paths.
- **If `PYTHONPATH` is not set:** Using `%PYTHONPATH%` expands to nothing, which is fine.
- **Check what Python sees:**
  ```cmd
  python -c "import sys; print('\\n'.join(sys.path))"
  ```
  You should see your project directory at or near the top.
- **Restart required:** Always restart your terminal or IDE after changing environment variables.

---

## Example Use Cases

| Where you run from                | Command example                            | PYTHONPATH needed?                                     |
|-----------------------------------|--------------------------------------------|--------------------------------------------------------|
| feedback_portal/                  | python -m source.production.arb.utils.json | No                                                     |
| feedback_portal/source/production | python -m arb.utils.json                   | Yes: D:\local\cursor\feedback_portal\source\production |
| feedback_portal/source/production | flask --app arb/wsgi run                   | Yes: D:\local\cursor\feedback_portal\source\production |

---

## Best Practices

- Use a single, clean path if you only work on this project.
- Prepend if you have other projects or tools that rely on `PYTHONPATH`.
- For permanent changes, use the Windows GUI for user-specific settings.
- Always verify with `echo %PYTHONPATH%` and by checking `sys.path` in Python.

---

*Last updated: 2025-07-09*
