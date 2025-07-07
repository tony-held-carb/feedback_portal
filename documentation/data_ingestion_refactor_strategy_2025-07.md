# Data Ingestion & Persistence Refactor Strategy – July 2025

## Overview
This document outlines a proposed strategy and phased plan for refactoring the data ingestion and persistence flow in the ARB Feedback Portal. The goal is to improve clarity, robustness, maintainability, and testability while minimizing risk.

---

## Refactor Strategy: Principles

1. **Incremental, Test-Driven Refactor:**
   - Make small, well-tested changes in each step.
   - Maintain a working codebase at all times (no "big bang" rewrite).

2. **Separation of Concerns:**
   - Decouple DB column handling from JSON/misc_json handling.
   - Separate form logic from persistence logic.
   - Isolate serialization/deserialization from business logic.

3. **Explicit Data Contracts:**
   - Define clear interfaces for each function (input/output types, responsibilities).
   - Use type hints and docstrings everywhere.

4. **Comprehensive Testing:**
   - Add/expand unit and integration tests before and during refactor.
   - Use test coverage tools to ensure all critical paths are exercised.

5. **Documentation and Migration:**
   - Update documentation as you go.
   - Plan for data migrations if you change the structure of persisted data.

---

## Phased Refactor Plan

### Phase 1: Baseline and Test Coverage
- Inventory all entry points (routes, CLI, batch jobs) that use the ingestion/persistence flow.
- Write/expand tests for all current behaviors (including edge cases and error handling).
- Add logging to all key functions to trace data flow and catch regressions early.

### Phase 2: Decouple JSON and DB Column Logic
- Refactor payload handling so that DB columns and `misc_json` are populated/updated separately.
- Remove legacy fields (like `id_incidence`) from `misc_json` at the ingestion boundary.
- Introduce clear data models (e.g., Pydantic or dataclasses) for payloads, forms, and DB rows.

### Phase 3: Modularize Serialization/Deserialization
- Centralize all serialization/deserialization logic (datetimes, decimals, etc.) in utility modules.
- Replace ad-hoc type coercion with explicit, tested functions.
- Ensure all data written to the DB is contract-compliant at the boundary.

### Phase 4: Simplify and Clarify Function Responsibilities
- Split monolithic functions (like `dict_to_database`) into smaller, single-responsibility functions:
  - e.g., `parse_payload`, `validate_payload`, `persist_row`, `update_json_column`, `log_change`
- Make data flow explicit: pass only what's needed at each step, avoid passing giant dicts everywhere.

### Phase 5: Improve Form/Model Mapping
- Refactor WTForm <-> model mapping to be explicit and testable.
- Remove deprecated/legacy helpers (like `get_payloads`).
- Document mapping rules (e.g., which fields go where, how types are handled).

### Phase 6: Integration and Regression Testing
- Run full integration tests after each major step.
- Use feature flags or branch-based development to avoid breaking production.
- Solicit user feedback (if possible) on any UI/UX changes.

### Phase 7: Documentation and Training
- Update all developer docs to reflect the new flow.
- Provide migration notes for any breaking changes.
- Train team members on the new architecture and best practices.

---

## Example: What the New Flow Might Look Like
- **Ingestion boundary:** Parse and validate input (form, Excel, JSON) → produce a well-typed payload object.
- **Persistence layer:** Map payload to DB columns and JSON column explicitly. Use utility functions for all serialization/deserialization. Log and audit changes in a single, well-defined place.
- **Testing:** Each function/unit is covered by tests (including error and edge cases). Integration tests cover end-to-end flows.

---

## Risk Mitigation
- Work in feature branches; merge only when tests pass.
- Keep old and new flows side-by-side (if needed) during migration.
- Automate as much as possible (tests, linting, type checks).
- Communicate changes to all stakeholders early and often.

---

## Summary Table: Refactor Steps

| Phase   | Goal                                 | Key Actions                                  |
|---------|--------------------------------------|----------------------------------------------|
| 1       | Baseline & Test Coverage             | Inventory, add/expand tests, add logging     |
| 2       | Decouple JSON/DB logic               | Separate payload handling, remove legacy     |
| 3       | Modularize serialization             | Centralize, test, and document utilities     |
| 4       | Clarify function responsibilities    | Split/rename functions, explicit data flow   |
| 5       | Improve form/model mapping           | Refactor mapping, remove deprecated helpers  |
| 6       | Integration & regression testing     | Full tests, feature flags, user feedback     |
| 7       | Documentation & training             | Update docs, migration notes, team training  |

---

## Note for Future Work
This refactor is a major undertaking and should be scheduled when time and resources allow. When you are ready to resume, review this documentation and the related analysis docs, and proceed incrementally. The AI assistant can help you review, plan, and execute each phase safely. 