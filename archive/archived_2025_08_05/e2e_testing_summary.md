# E2E Testing Summary

## Directory Structure

```
feedback_forms/testing_versions/
├── standard/      # Main "good" and "bad" test files for each sector and scenario
├── edge_cases/    # Files designed to trigger edge-case or error handling
├── generated/     # Programmatically generated files for schema/logic/validation testing
├── old/           # Legacy or previous-version test files
```

---

## Test File Purposes

### **standard/**
- **Purpose:** Canonical "good" and "bad" data files for each sector (dairy, landfill, oil & gas, energy, generic).
- **Expected:** Should pass all upload and backend validation tests, except for known edge cases (e.g., blank files).

### **edge_cases/**
- **Purpose:** Files intentionally malformed, incomplete, or designed to trigger error handling.
- **Expected:** Should be rejected by the app, with appropriate error messages and no DB update.

### **generated/**
- **Purpose:** Files generated to test schema logic, conditional fields, missing/extra fields, invalid types, and large file handling.
- **Expected:** Some may pass upload but fail backend or staged validation. Good candidates for moving to `edge_cases/` if meant to test negative scenarios.

### **old/**
- **Purpose:** Legacy test files from previous versions, retained for regression and compatibility testing.

---

## How to Use This Summary

- Use the directory structure and file purposes to organize and maintain your test data.
- Files in `generated/` that consistently fail backend or staged validation are strong candidates to move to `edge_cases/`.
- Files in `standard/` should always pass all tests (except for known edge cases).
- Use this summary to decide which files to reclassify or further investigate.

---

*This summary is a companion to the main E2E README, focusing on test data organization and expectations. For test running instructions and coverage, see the main README.* 