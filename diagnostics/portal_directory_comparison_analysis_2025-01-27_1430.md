# Portal Directory Comparison Analysis - 2025-01-27 14:30

## Overview
Fresh analysis of differences between main and refactor_20 branches for the portal directory (`feedback_portal/source/production/arb/portal`), focusing on `.py`, `.html`, and `.jinja` files.

## Analysis Summary

### **File Counts:**
- **Files in Main but NOT in Refactor:** 0
- **Files in Refactor but NOT in Main:** 6 (new staging/AI features)
- **Files in Common:** ~50 files
- **Files that Differ:** 15 files

### **Files in Refactor but NOT in Main (New Files):**
1. `routes_old.py` - Backup routes file ✅ **MOVED TO ARCHIVE**
2. `templates/review_staged.html` - New staging review template
3. `templates/review_staged_old.html` - Backup staging review template ✅ **MOVED TO ARCHIVE**
4. `templates/upload_staged.html` - New staging upload template
5. `utils/github_and_ai.py` - New GitHub/AI utility
6. `utils/github_and_ai_old.py` - Backup GitHub/AI utility ✅ **MOVED TO ARCHIVE**

### **Files that Differ Between Branches (15 files):**

#### **Core Portal Files (Should be identical after cleanup):**
1. `startup/flask.py` - Development improvements (reviewed & safe)
2. `utils/sector_util.py` - ✅ **FIXED - Now identical to main**

#### **New/Modified Functionality:**
3. `json_update_util.py` - New JSON update functionality
4. `routes.py` - Modified routes (new staging features)
5. `routes_old.py` - New backup routes file ✅ **MOVED TO ARCHIVE**
6. `templates/review_staged.html` - New staging review UI
7. `templates/review_staged_old.html` - New backup staging review UI ✅ **MOVED TO ARCHIVE**
8. `templates/upload_staged.html` - New staging upload UI
9. `utils/db_ingest_util.py` - New database ingest functionality
10. `utils/db_introspection_util.py` - New database introspection
11. `utils/file_upload_util.py` - Modified file upload functionality
12. `utils/github_and_ai.py` - New GitHub/AI functionality
13. `utils/github_and_ai_old.py` - New backup GitHub/AI file ✅ **MOVED TO ARCHIVE**
14. `wtf_landfill.py` - New landfill forms
15. `wtf_oil_and_gas.py` - New oil & gas forms

## Context
This analysis was performed after cleaning up core portal files (`app.py`, `settings.py`, `sqla_models.py`, `navbar.jinja`, `extensions.py`) to remove auth-related changes and match the main branch exactly.

## Completed Actions
1. ✅ **Created this analysis document** - `diagnostics/portal_directory_comparison_analysis_2025-01-27_1430.md`
2. ✅ **Moved `_old` files to archive/cursor_deleted** - Cleaned up backup files
3. ✅ **Fixed `utils/sector_util.py`** - Reverted to main branch version (added missing `DeclarativeMeta` import)

## Next Steps
1. ✅ **Move `_old` files to archive/cursor_deleted** - COMPLETED
2. ✅ **Investigate why `utils/sector_util.py` still shows differences** - COMPLETED
3. **Analyze new staging/AI files for potential compatibility issues**
4. **Focus on files that might cause runtime errors**

## Risk Assessment
- **Core files**: Now identical to main (low risk)
- **New staging features**: Need compatibility analysis
- **Modified utilities**: Need dependency analysis
- **Backup files**: ✅ **Archived (low risk)**

## Notes
- All core portal functionality should be preserved
- New features are additive and should not break existing functionality
- Need to verify no broken imports or references to removed auth code
- Archive folder created: `archive/cursor_deleted/` for backup files 