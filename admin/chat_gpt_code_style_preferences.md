# Code Style and Documentation Preferences

This document defines the preferred code and documentation style for all Python files in the project. It is intended both as a human-readable reference and as a checklist for automated or manual review.

## ✅ Indentation and Formatting

- Use **two-space indentation** for all code and docstrings.
- No tabs or 4-space indents.
- Docstrings must also follow two-space indentation.
- Keep lines ≤ 88 characters when practical.
- Avoid excessive vertical spacing unless it improves clarity.

## 📚 Docstring Style: Google Format (Required)

- All modules and functions must use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).

### 🔹 Module-Level Docstrings

- Provide a clear summary of the module's purpose.
- Include version, usage context, and optional Notes or Example section.

### 🔹 Function/Method Docstrings

Each function must:

- Include **type hints in the signature AND in the docstring**.
- Use `Args`, `Returns`, `Raises`, and `Examples` sections as needed.
- Avoid vague types (`object`, `dict`, etc.) when more precise types are known.
- Examples must:
  - **Not use **``** prompts** (use plain blocks instead).
  - Be copy-paste ready for IDEs like PyCharm.

Example:

```python
Example:
  Input: {"a": 1, "b": 2}
  Output: {"sum": 3}
```

## 🚫 Avoided Patterns

- ❌ No `>>>` in examples.
- ❌ No unused imports, comments, or boilerplate.
- ❌ No unverified or outdated file references.
- ❌ Do not change function names/signatures unless explicitly approved.

## 🧪 Examples and Edge Case Requirements

- Required for functions involving JSON, forms, validators, file I/O, and time parsing.
- Must clearly show input and expected output without ambiguity.

## 🛡️ Type Hinting Standards

- Always use **Python 3.10+** modern type hints:
  - `str | None`, not `Optional[str]`
  - `list[str]`, not `List[str]`
- SQLAlchemy:
  - Use `DeclarativeMeta` or `AutomapBase` for base/model references.
  - Avoid `object` unless absolutely necessary.
- Flask/WTForms:
  - Use `FlaskForm` and validator types (`InputRequired`, `Optional`, etc.) explicitly.
- JSON:
  - Use `dict[str, Any]`, `str | None`, etc.
- File Paths:
  - Use `Path`, not `str`

## 🗂️ Project Organization Rules

- Apply changes **file-by-file** in **alphabetical order**.
- Always operate on the **latest verified version** of each file.
- Do not assume missing functions—only refactor based on current sources.
- Routes, forms, and utilities must be **self-contained and documented**.

## ✅ Checklist Summary

| Area              | Required Practice                                         |
| ----------------- | --------------------------------------------------------- |
| Indentation       | Two-space indent for code and docs                        |
| Docstrings        | Google-style with full sections                           |
| Type Hints        | In signature **and** docstring                            |
| Examples          | No `>>>`; use formatted block style                       |
| JSON I/O          | Use wrappers like `read_json_file` and `save_json_safely` |
| SQLAlchemy        | Use accurate model base types (`DeclarativeMeta`)         |
| Logging           | Use `pp_log()` and structured logging                     |
| File Paths        | Use `Path`, not `str`                                     |
| Signature Changes | Do not modify unless discussed                            |
| Source Basis      | Use current verified files only                           |

---

This document is to be treated as the **source of truth** for code formatting and review within the project.

