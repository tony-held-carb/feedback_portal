# Google Python Style Guide Summary

This document provides a comprehensive overview of the **Google Python Style Guide**, focusing on recommended file
structure, naming conventions, and detailed docstring section headings. It is suitable for both library development and
application codebases.

---

## 📌 Purpose

The Google Python Style Guide promotes:

- **Readable**, consistent, and maintainable Python code.
- Clear and structured **documentation** through well-defined **docstrings**.
- Standardized formatting, naming, and imports for large teams.

---

## 🧱 Typical Python File Structure

Below is the recommended order of sections in a Python file:

1. **Module-level docstring**
2. **Import statements**
3. **Module-level constants**
4. **Global variables or configuration** (rare)
5. **Class definitions**
6. **Function and method definitions**
7. **`if __name__ == "__main__":` block** (for executable scripts)

---

## 🔠 Import Grouping

Imports should be grouped and separated by blank lines in this order:

```python
import os
import sys

import numpy as np

from my_project import helper
```

---

## 🏷️ Naming Conventions

| Element        | Convention                                   |
|----------------|----------------------------------------------|
| Variable       | `lower_case_with_underscores`                |
| Function       | `lower_case_with_underscores`                |
| Class          | `CapWords` (PascalCase)                      |
| Constant       | `ALL_CAPS_WITH_UNDERSCORES`                  |
| Module/package | `lowercase` or `lower_case_with_underscores` |
| Private name   | `_single_leading_underscore`                 |

---

## 🧾 Google-Style Docstrings

All public modules, functions, classes, and methods should have **Google-style docstrings**.

### 📄 Structure

```python
"""Summary line.

Extended description (optional).

Args:
  arg1 (int): Description of arg1.
  arg2 (str): Description of arg2.

Returns:
  bool: Description of return value.

Raises:
  ValueError: If some condition occurs.
"""
```

### 📚 Common Docstring Section Headings

| Heading            | Purpose                                                            |
|--------------------|--------------------------------------------------------------------|
| `Args`             | Describes each function argument, its type, and purpose.           |
| `Returns`          | Describes the return value and its type.                           |
| `Yields`           | Used instead of `Returns` for generators that yield values.        |
| `Raises`           | Lists exceptions the function may raise and under what conditions. |
| `Attributes`       | Documents instance attributes in classes.                          |
| `Class Attributes` | Documents class-level (shared) attributes.                         |
| `Properties`       | Documents `@property`-decorated attributes.                        |
| `Methods`          | Documents methods defined within a class (rare).                   |
| `Examples`         | Provides usage examples or sample code.                            |
| `Notes`            | Adds clarifying information, design notes, or caveats.             |
| `Warnings`         | Highlights cautionary details that users must consider.            |
| `Deprecated`       | Marks the function/class as deprecated.                            |
| `See Also`         | Cross-references related functions or modules.                     |
| `Todo`             | Indicates planned improvements or unimplemented features.          |

---

### ✅ Example Using Multiple Sections

```python
def analyze_signal(data: list[float], threshold: float) -> bool:
  """Analyzes a signal and returns whether it exceeds a given threshold.

  This function performs a simple statistical analysis and flags signals
  with anomalies based on configurable thresholds.

  Args:
    data (list of float): The input signal data.
    threshold (float): The threshold to flag anomalies.

  Returns:
    bool: True if the signal is anomalous, False otherwise.

  Raises:
    ValueError: If the input list is empty.

  Notes:
    This method uses a simple average; for advanced use cases,
    consider using `scipy.stats`.

  Examples:
    analyze_signal([1.2, 3.4, 2.8], 3.0)
    False

  See Also:
    normalize_signal, compute_snr

  Todo:
    - Add support for time-weighted thresholds
    - Handle missing/null values
  """
```

---

## 🧼 Additional Best Practices

- **Line length**: Limit to 80 characters (or 100 if justified)
- **Indentation**: 2 spaces per level; never use tabs
- **Avoid**: `from module import *`
- Use `is` for `None` comparison (`if var is None`)
- Prefer **list comprehensions** over `map()` or `filter()` when clearer
- Include **type hints** (PEP 484) wherever practical

---

## 📎 Summary Table of Python File Sections

| Section          | Purpose                            |
|------------------|------------------------------------|
| Module docstring | Describe module purpose and usage  |
| Imports          | Organize dependencies              |
| Constants        | Define reusable, immutable values  |
| Classes          | Define OOP structure and logic     |
| Functions        | Encapsulate logic; well-documented |
| `__main__` block | Allow script-style execution       |

---

This document can be used as a quick reference for writing Google-compliant Python code and documentation.
