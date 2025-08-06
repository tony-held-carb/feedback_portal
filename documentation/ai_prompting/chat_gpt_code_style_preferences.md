# chat_gpt_code_style_preferences.md

## Code Formatting Rules

These reflect the user's preferred style for all Python source code, refactor tasks, and generated examples.

### Indentation

- Always use **2 spaces** for indentation (code, docstrings, examples).
- Never use tabs.

### Docstrings

- All functions, methods, classes, and modules **must include Google-style docstrings**.
- Docstrings must document:
    - **Args**: All parameters, with correct type hints.
    - **Returns**: If the function returns a value, include type and description.
    - **Raises**: If relevant, document exceptions raised.
- **Examples must not use `>>>`** (to avoid confusing IDE syntax checkers). Use plain code blocks.

### Type Hinting

- Provide type hints in **both** function signatures **and** docstrings.
- Always use modern `X | None` syntax instead of `Optional[X]`.
- Do not use `typing.` prefix (e.g., use `list[str]`, not `typing.List[str]`).

### Additional Notes

- Use full module docstrings.
- Maintain user's naming conventions and file structure.
- Never rewrite function signatures unless explicitly instructed.
