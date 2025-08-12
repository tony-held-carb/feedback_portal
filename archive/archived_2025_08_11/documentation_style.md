# Docstring Style: Args, Returns, and Attributes Sections

## Overview
This document summarizes best practices for using `Args:`, `Returns:`, and `Attributes:` sections in Python docstrings, with a focus on clarity, codebase uniformity, and compatibility with documentation tools (such as mkdocstrings/Griffe).

---

## 1. Functions/Methods with No Args/Returns
- **Omit the `Args:` and `Returns:` sections entirely.**
  - This is the convention in Google, NumPy, and Sphinx docstring styles.
  - Most tools (including IDEs and doc generators) expect these sections to be present only when there is something to document.
  - Including `Args: None` or `Returns: None` is not standard and can confuse doc parsers (e.g., Griffe issues warnings like `Failed to get 'name: description' pair from 'None'`).

## 2. Functions/Methods with Args/Returns
- Always include the section, and document each parameter and return value.

## 3. For Uniformity
- Strive for **clarity and usefulness** over mechanical uniformity.
- Uniformity is good, but not if it means adding unnecessary or even misleading boilerplate.

---

## Summary Table
| Situation                | Recommended Practice                |
|--------------------------|-------------------------------------|
| No parameters            | Omit `Args:` section                |
| No return value          | Omit `Returns:` section             |
| Has parameters/returns   | Include and document them           |

---

## Why This Is Best
- **Reduces noise**: Less clutter in your codebase.
- **Avoids parser warnings**: Tools like Griffe, Sphinx, and IDEs expect this.
- **Improves readability**: Developers can focus on meaningful documentation.

---

## Conclusion
- **Do not add `Args: None` or `Returns: None` for the sake of uniformity.**
- Only include these sections when there is something to document.
- It’s better to have a mix of docstrings with and without these sections, depending on the function, than to have unnecessary boilerplate everywhere.

---

*This guidance is based on experience with mkdocstrings/Griffe, Sphinx, and common Python documentation standards. Following these recommendations will keep your codebase clean, readable, and compatible with modern documentation tools.* 