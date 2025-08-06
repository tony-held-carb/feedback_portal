# Data Ingestion & Persistence Refactor Strategy – July 2025 (Updated)

## Overview
This document outlines a proposed strategy and phased plan for refactoring the data ingestion and persistence flow in the ARB Feedback Portal. The goal is to improve clarity, robustness, maintainability, and testability while minimizing risk.

**Last Updated:** January 2025  
**Current Status:** Significant improvements have been made since the original analysis. The system is now more robust with centralized datetime handling, staged upload workflow, and enhanced logging.

---

## Current State Assessment

### ✅ Completed Improvements
1. **Datetime Handling Refactor (PR #22)**: Centralized all datetime operations in `utils/date_and_time.py` with strict contract compliance
2. **Staged Upload Workflow (PR #21, #26)**: Implemented upload → stage → review → confirm → apply workflow
3. **Logging Standardization (PR #21)**: Replaced custom logger with standard Python logging
4. **Enhanced Error Handling**: Improved user feedback and debugging throughout the ingestion flow
5. **Comprehensive Test Coverage**: Added extensive tests for all main functions and edge cases

### 🔄 Current Strengths
- **Centralized datetime handling** with clear contracts
- **Robust staged upload workflow** with user control
- **Comprehensive logging and diagnostics**
- **Good test coverage** for critical paths
- **Enhanced error reporting** and user feedback

### ⚠️ Remaining Challenges
- **Deep nesting** in the ingestion flow (though improved)
- **Tight coupling** between JSON and DB column handling
- **Complex function responsibilities** (some functions still do too much)
- **Legacy field handling** (`id_incidence` contamination prevention)

---

## Refactor Strategy: Updated Principles

1. **Incremental, Test-Driven Refactor:**
   - Make small, well-tested changes in each step.
   - Maintain a working codebase at all times (no "big bang" rewrite).
   - **Leverage existing test coverage** to ensure no regressions.

2. **Separation of Concerns:**
   - Decouple DB column handling from JSON/misc_json handling.
   - Separate form logic from persistence logic.
   - Isolate serialization/deserialization from business logic.
   - **Build on existing datetime utilities** and staged workflow.

3. **Explicit Data Contracts:**
   - Define clear interfaces for each function (input/output types, responsibilities).
   - Use type hints and docstrings everywhere.
   - **Extend the existing datetime contract** to other data types.

4. **Comprehensive Testing:**
   - **Expand existing test coverage** to include new refactored components.
   - Use test coverage tools to ensure all critical paths are exercised.
   - **Maintain integration tests** for the staged upload workflow.

5. **Documentation and Migration:**
   - Update documentation as you go.
   - Plan for data migrations if you change the structure of persisted data.
   - **Preserve the staged upload workflow** as it provides good user control.

---

## Updated Phased Refactor Plan

### Phase 1: Assessment and Baseline (✅ Mostly Complete)
- ✅ Inventory all entry points (routes, CLI, batch jobs) that use the ingestion/persistence flow.
- ✅ Write/expand tests for all current behaviors (including edge cases and error handling).
- ✅ Add logging to all key functions to trace data flow and catch regressions early.
- **🔄 Remaining**: Document current usage patterns and identify specific pain points.

### Phase 2: Decouple JSON and DB Column Logic (🔄 In Progress)
- **🔄 Current State**: `id_incidence` handling is improved but still complex
- **Next Steps**:
  - Refactor payload handling so that DB columns and `misc_json` are populated/updated separately.
  - Remove legacy fields (like `id_incidence`) from `misc_json` at the ingestion boundary.
  - Introduce clear data models (e.g., Pydantic or dataclasses) for payloads, forms, and DB rows.
  - **Preserve staged upload workflow** while simplifying the underlying logic.

### Phase 3: Modularize Serialization/Deserialization (✅ Mostly Complete)
- ✅ Centralize all serialization/deserialization logic (datetimes, decimals, etc.) in utility modules.
- ✅ Replace ad-hoc type coercion with explicit, tested functions.
- ✅ Ensure all data written to the DB is contract-compliant at the boundary.
- **🔄 Remaining**: Extend the datetime contract pattern to other data types (decimals, enums, etc.).

### Phase 4: Simplify and Clarify Function Responsibilities (🔄 Priority)
- **Current Focus**: Split monolithic functions (like `dict_to_database`) into smaller, single-responsibility functions:
  - e.g., `parse_payload`, `validate_payload`, `persist_row`, `update_json_column`, `log_change`
- Make data flow explicit: pass only what's needed at each step, avoid passing giant dicts everywhere.
- **Preserve the staged upload workflow** while simplifying the underlying functions.

### Phase 5: Improve Form/Model Mapping (✅ Mostly Complete)
- ✅ Refactor WTForm <-> model mapping to be explicit and testable.
- ✅ Remove deprecated/legacy helpers (like `get_payloads`).
- ✅ Document mapping rules (e.g., which fields go where, how types are handled).
- **🔄 Remaining**: Further simplify the mapping logic and reduce coupling.

### Phase 6: Integration and Regression Testing (🔄 Ongoing)
- ✅ Run full integration tests after each major step.
- ✅ Use feature flags or branch-based development to avoid breaking production.
- ✅ Solicit user feedback (if possible) on any UI/UX changes.
- **🔄 Remaining**: Expand integration tests to cover new refactored components.

### Phase 7: Documentation and Training (🔄 Ongoing)
- ✅ Update all developer docs to reflect the new flow.
- ✅ Provide migration notes for any breaking changes.
- ✅ Train team members on the new architecture and best practices.
- **🔄 Remaining**: Update this refactor strategy document as progress is made.

---

## Example: What the New Flow Might Look Like (Updated)

### Current State (Improved)
- **Ingestion boundary:** Parse and validate input (form, Excel, JSON) → produce a well-typed payload object.
- **Persistence layer:** Map payload to DB columns and JSON column explicitly. Use utility functions for all serialization/deserialization. Log and audit changes in a single, well-defined place.
- **Staged workflow:** Upload → Stage → Review → Confirm → Apply with user control at each step.
- **Testing:** Each function/unit is covered by tests (including error and edge cases). Integration tests cover end-to-end flows.

### Target State (After Phase 4)
- **Clear separation:** Ingestion → Validation → Persistence → Audit
- **Explicit contracts:** Each function has clear input/output types and responsibilities
- **Reduced coupling:** JSON handling and DB column handling are separate concerns
- **Preserved UX:** Staged upload workflow remains intact with simplified backend

---

## Risk Mitigation (Updated)

- ✅ Work in feature branches; merge only when tests pass.
- ✅ Keep old and new flows side-by-side (if needed) during migration.
- ✅ Automate as much as possible (tests, linting, type checks).
- ✅ Communicate changes to all stakeholders early and often.
- **🔄 New**: Preserve the staged upload workflow as it provides good user control and safety.

---

## Updated Summary Table: Refactor Steps

| Phase   | Goal                                 | Key Actions                                  | Status |
|---------|--------------------------------------|----------------------------------------------|---------|
| 1       | Baseline & Test Coverage             | Inventory, add/expand tests, add logging     | ✅ Complete |
| 2       | Decouple JSON/DB logic               | Separate payload handling, remove legacy     | 🔄 In Progress |
| 3       | Modularize serialization             | Centralize, test, and document utilities     | ✅ Complete |
| 4       | Clarify function responsibilities    | Split/rename functions, explicit data flow   | 🔄 Priority |
| 5       | Improve form/model mapping           | Refactor mapping, remove deprecated helpers  | ✅ Complete |
| 6       | Integration & regression testing     | Full tests, feature flags, user feedback     | 🔄 Ongoing |
| 7       | Documentation & training             | Update docs, migration notes, team training  | 🔄 Ongoing |

---

## Immediate Next Steps (Phase 4 Focus)

### High Priority
1. **Split `dict_to_database`** into smaller, focused functions:
   - `parse_and_validate_payload(data_dict)`
   - `resolve_or_create_row(db, base, table_name, primary_key, id_)`
   - `update_model_json_column(model, payload, json_field)`
   - `commit_and_log_changes(db, model, comment)`

2. **Simplify `update_model_with_payload`**:
   - Separate JSON preparation from model updating
   - Make the function more focused on its core responsibility

3. **Enhance `apply_json_patch_and_log`**:
   - Simplify the change detection logic
   - Make the logging more explicit and testable

### Medium Priority
1. **Extend datetime contract pattern** to other data types
2. **Improve error handling** in the staged upload workflow
3. **Add more integration tests** for the refactored components

### Low Priority
1. **Consider Pydantic models** for payload validation
2. **Explore async/await patterns** for better performance
3. **Add performance monitoring** to the ingestion flow

---

## Note for Future Work

This refactor strategy has been updated to reflect the significant improvements made since the original analysis. The current state is much more robust and maintainable than initially assessed. 

**Key Recommendations:**
1. **Focus on Phase 4** (function responsibility clarification) as the next major step
2. **Preserve the staged upload workflow** as it provides excellent user control
3. **Build on the existing datetime utilities** and extend the contract pattern
4. **Maintain the comprehensive test coverage** that has been established
5. **Continue incremental improvements** rather than attempting a major rewrite

When you are ready to resume, review this updated documentation and the related analysis docs, and proceed incrementally. The AI assistant can help you review, plan, and execute each phase safely. 