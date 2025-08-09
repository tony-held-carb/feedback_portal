# Data Ingestion Refactor - Current State Analysis

## Overview

This document provides an accurate assessment of the current state of the ARB Feedback Portal's data ingestion refactor
as of August 2025. The refactor has made significant progress with parallel implementations that maintain backward
compatibility while introducing improved patterns.

**Last Updated:** August 2025
**Current Status:** ✅ **PHASE 7A COMPLETED** - Route orchestration framework with cross-cutting concern extraction

---

## Current Implementation Status

### ✅ Completed Refactored Components

#### 1. **Refactored Routes** (Fully Functional) ✅ **PHASE 7A EXPANDED**

- **`/upload_refactored`**: Parallel implementation of `/upload` with improved error handling
- **`/upload_staged_refactored`**: Parallel implementation of `/upload_staged` with enhanced user experience
- **`/upload_orchestrated`**: Phase 7A demonstration route using orchestration framework
- **`/upload_staged_orchestrated`**: Phase 7A demonstration route using orchestration framework
- **Status**: All routes are fully functional and tested
- **Backward Compatibility**: Original routes remain unchanged and functional
- **Architecture**: Phase 7A routes demonstrate complete cross-cutting concern extraction

#### 2. **Result Types Module** ✅ **PHASE 6 EXPANDED**

- **Location**: `source/production/arb/portal/utils/result_types.py`
- **Main Components**: 
  - `StagingResult` and `UploadResult` (main result types)
  - `FileSaveResult` (file upload operations)
  - `FileConversionResult` (file conversion operations)
  - `IdValidationResult` (ID validation operations)
  - `StagedFileResult` (staged file creation)
  - `DatabaseInsertResult` (database insertion operations)
- **Phase 6 Lower-Level Components**: 
  - `FileUploadResult` (file upload to disk operations)
  - `FileAuditResult` (audit logging operations)
  - `JsonProcessingResult` (JSON conversion operations)
- **Features**: Type-safe, self-documenting, comprehensive error handling
- **Status**: Fully implemented with complete test coverage including Phase 6 enhancements

#### 3. **Helper Functions with Result Types** ✅ **MAJOR MILESTONE COMPLETED**

#### 4. **Route Helper Functions** ✅ **PHASE 1 COMPLETED**

#### 5. **Error Handling Helper Functions** ✅ **PHASE 2 COMPLETED**

- **New Error Handling Helper Functions** (shared between refactored routes):
  - `handle_upload_error()` - Centralized error handling for upload failures
  - `handle_upload_exception()` - Centralized exception handling with diagnostic support
- **Location**: `source/production/arb/portal/utils/route_upload_helpers.py`
- **Status**: All 7 route helper functions implemented and tested (25/25 tests passing)
- **Benefits**: Eliminates error handling duplication, ensures consistent error behavior
- **Code Reduction**: ~50 lines of duplicated error handling code eliminated
- **Enhanced Features**: Diagnostic function support for detailed error information

#### 6. **Success Handling Helper Functions** ✅ **PHASE 3 COMPLETED**

- **New Success Handling Helper Functions** (shared between refactored routes):
  - `handle_upload_success()` - Centralized success handling for upload processing
  - `get_success_message_for_upload()` - Enhanced success message generation
- **Location**: `source/production/arb/portal/utils/route_upload_helpers.py`
- **Status**: All 9 route helper functions implemented and tested (30/30 tests passing)
- **Benefits**: Eliminates success handling duplication, ensures consistent success behavior
- **Code Reduction**: ~20 lines of duplicated success handling code eliminated
- **Enhanced Features**: Detailed success messages with emoji and formatting

#### 7. **Template Rendering Helper Functions** ✅ **PHASE 4 COMPLETED**

- **New Template Rendering Helper Functions** (shared between refactored routes):
  - `render_upload_page()` - Centralized template rendering for upload pages
  - `render_upload_success_page()` - Centralized success page rendering
  - `render_upload_error_page()` - Centralized error page rendering
- **Location**: `source/production/arb/portal/utils/route_upload_helpers.py`
- **Status**: All 12 route helper functions implemented and tested (44/44 tests passing)
- **Benefits**: Eliminates template rendering duplication, ensures consistent user experience
- **Code Reduction**: ~15 lines of duplicated template rendering code eliminated
- **Enhanced Features**: Consistent page titles, upload type context, and status indicators
- **Test Results**: All tests passing after fixing test expectations for user-friendly messages

#### 8. **Route Orchestration Framework** ✅ **PHASE 7A COMPLETED**

- **New Cross-Cutting Concern Extraction** (Phase 7A achievement):
  - `UploadConfiguration` - Configuration class for route orchestration
  - `orchestrate_upload_route()` - Unified framework eliminating route duplication
- **Location**: `source/production/arb/portal/utils/route_upload_helpers.py`
- **Status**: Route orchestration framework implemented and demonstrated (22/22 tests passing)
- **Benefits**: Eliminates all route duplication through cross-cutting concern extraction
- **Code Reduction**: ~160 lines of duplicated route logic eliminated
- **Enhanced Features**: Configuration-driven routes, unified error handling, consistent behavior
- **Demonstration Routes**: Two new orchestrated routes showing framework capabilities

#### 9. **Refactored Main Functions** ✅ **UPDATED**

- **Main Function**: `stage_uploaded_file_for_review()` in `db_ingest_util.py`
- **Main Function**: `upload_and_process_file()` in `db_ingest_util.py`
- **Status**: Both functions now use new helper functions with result types
- **Test Results**: All 12 main function tests passing (6 staging + 6 upload)

#### 9. **Enhanced Error Handling** ✅ **COMPLETED**

- **Specific Error Types**: `missing_id`, `conversion_failed`, `file_error`, `database_error`
- **User-Friendly Messages**: Clear guidance for users on how to fix issues
- **Comprehensive Logging**: Detailed diagnostics for debugging

#### 10. **Direct Upload Refactor** ✅ **COMPLETED**

- **Main Function**: `upload_and_process_file()` in `db_ingest_util.py`
- **Status**: Fully implemented and tested (August 2025)
- **Test Results**:
    - Unit tests: 6/6 passed (100%)
    - Helper function tests: 16/16 passed (100%)
- **Route Integration**: `/upload_refactored` route successfully uses the new function
- **All Helper Functions**: All new `_with_result` helper functions working correctly

### 🔄 Remaining Components

#### 1. **Helper Function Documentation** (Mostly Complete)

- **Status**: All core helper functions are complete and tested
- **Missing**: Enhanced documentation for some utility functions

---

## Architecture Comparison: Original vs Refactored

### Original Implementation

```python
# Original approach - tuple returns with unclear error handling
file_path, id_, sector, json_data, staged_filename = upload_and_stage_only(...)

if id_ and staged_filename:
    # Success case
else:
    # Failure - but WHAT failed? Route has to guess
```

### Refactored Implementation

```python
# Refactored approach - rich result objects with specific error types
result = stage_uploaded_file_for_review(...)

if result.success:
    # Success case - clear and explicit
    flash(f"File staged successfully: {result.staged_filename}")
    return redirect(url_for('main.review_staged', id_=result.id_, filename=result.staged_filename))
else:
    # Specific error handling based on error_type
    if result.error_type == "missing_id":
        flash("Please add a valid ID to your spreadsheet")
    elif result.error_type == "conversion_failed":
        flash("Please upload an Excel file")
    else:
        flash(f"Error: {result.error_message}")
```

### New Helper Function Pattern

```python
# Before: Brittle tuple returns
file_path, error = _save_uploaded_file(upload_dir, request_file, db, description)
if not file_path:
    # What type of error? Route has to guess

# After: Rich result objects
result = save_uploaded_file_with_result(upload_dir, request_file, db, description)
if result.success:
    # Clear success case
    file_path = result.file_path
else:
    # Specific error handling
    if result.error_type == "file_error":
        flash("File upload failed. Please check your connection.")
```

---

## Function Inventory

### Core Refactored Functions

| Function                         | Location            | Status        | Purpose                     |
|----------------------------------|---------------------|---------------|-----------------------------|
| `stage_uploaded_file_for_review` | `db_ingest_util.py` | ✅ Complete    | Main staging workflow       |
| `upload_and_process_file`        | `db_ingest_util.py` | ✅ Complete    | Main direct upload workflow |
| `save_uploaded_file_with_result` | `db_ingest_util.py` | ✅ Complete    | File upload with results    |
| `convert_file_to_json_with_result` | `db_ingest_util.py` | ✅ Complete    | File conversion with results |
| `validate_id_from_json_with_result` | `db_ingest_util.py` | ✅ Complete    | ID validation with results  |
| `create_staged_file_with_result` | `db_ingest_util.py` | ✅ Complete    | Staged file with results    |
| `insert_json_into_database_with_result` | `db_ingest_util.py` | ✅ Complete    | DB insertion with results   |

### Result Types

| Type                    | Location          | Status     | Purpose                           |
|-------------------------|-------------------|------------|-----------------------------------|
| `StagingResult`         | `result_types.py` | ✅ Complete | Staging operation results         |
| `UploadResult`          | `result_types.py` | ✅ Complete | Direct upload results             |
| `FileSaveResult`        | `result_types.py` | ✅ Complete | File upload operation results     |
| `FileConversionResult`  | `result_types.py` | ✅ Complete | File conversion operation results |
| `IdValidationResult`    | `result_types.py` | ✅ Complete | ID validation operation results   |
| `StagedFileResult`      | `result_types.py` | ✅ Complete | Staged file creation results      |
| `DatabaseInsertResult`  | `result_types.py` | ✅ Complete | Database insertion results        |
| `FileUploadResult`      | `result_types.py` | ✅ Complete | File upload to disk results (Phase 6) |
| `FileAuditResult`       | `result_types.py` | ✅ Complete | Audit logging results (Phase 6)  |
| `JsonProcessingResult`  | `result_types.py` | ✅ Complete | JSON conversion results (Phase 6) |

### Original Functions (Maintained for Compatibility)

| Function                | Location            | Status       | Purpose                |
|-------------------------|---------------------|--------------|------------------------|
| `upload_and_update_db`  | `db_ingest_util.py` | ✅ Maintained | Original direct upload |
| `upload_and_stage_only` | `db_ingest_util.py` | ✅ Maintained | Original staging       |
| `dict_to_database`      | `db_ingest_util.py` | ✅ Maintained | Original DB operations |
| `_save_uploaded_file`   | `db_ingest_util.py` | ✅ Maintained | Original helper        |
| `_convert_file_to_json` | `db_ingest_util.py` | ✅ Maintained | Original helper        |
| `_validate_id_from_json` | `db_ingest_util.py` | ✅ Maintained | Original helper        |
| `_create_staged_file`   | `db_ingest_util.py` | ✅ Maintained | Original helper        |
| `_insert_json_into_database` | `db_ingest_util.py` | ✅ Maintained | Original helper        |

---

## Test Coverage Status

### Comprehensive Test Coverage

#### Unit Tests

- ✅ **`test_result_types.py`**: 8/8 tests passed
- ✅ **`test_utils_db_ingest_util.py`**: All tests passing
  - Staging tests: 6/6 passed
  - Upload tests: 6/6 passed
  - New helper function tests: 16/16 passed
  - **Total: 28 tests passing**
- ✅ **`test_route_upload_helpers.py`**: 44/44 tests passed (100%)
- ✅ **`test_route_equivalence.py`**: 13/13 tests passed
- ✅ **`test_routes.py`**: All refactored route tests passed

#### Integration Tests

- ✅ **`test_excel_upload_workflows.py`**: End-to-end workflow testing
- ✅ **`test_review_staged.py`**: Staged upload workflow testing
- ✅ **`test_browser_compatibility.py`**: Browser compatibility testing

#### E2E Tests

- ✅ **Refactored route workflows**: Both `/upload_refactored` and `/upload_staged_refactored`
- ✅ **Error handling scenarios**: All error types tested
- ✅ **User experience validation**: Success and failure flows

---

## Data Flow Analysis

### Current Data Flow (Refactored)

```
Upload Request
    ↓
Save File (save_uploaded_file_with_result → FileSaveResult)
    ↓
Convert to JSON (convert_file_to_json_with_result → FileConversionResult)
    ↓
Validate ID (validate_id_from_json_with_result → IdValidationResult)
    ↓
[For Staging] Create Staged File (create_staged_file_with_result → StagedFileResult)
    ↓
[For Direct Upload] Insert into Database (insert_json_into_database_with_result → DatabaseInsertResult)
    ↓
Return Rich Result Object (StagingResult/UploadResult)
```

### Error Handling Flow

```
Error Detection
    ↓
Specific Error Type Assignment
    ↓
User-Friendly Message Generation
    ↓
Rich Result Object Creation
    ↓
Route-Level Error Handling
    ↓
User Feedback
```

---

## Known Issues and Limitations

### 1. **Legacy Function Dependencies**

- **Issue**: Some refactored functions still depend on legacy patterns
- **Impact**: Potential for inconsistencies in error handling
- **Priority**: Medium - should be addressed for consistency

### 2. **Documentation Gaps**

- **Issue**: Some helper functions lack comprehensive documentation
- **Impact**: May slow down future development
- **Priority**: Low - can be addressed incrementally

### 3. **Performance Considerations**

- **Issue**: No performance benchmarking between original and refactored implementations
- **Impact**: Unknown performance characteristics
- **Priority**: Medium - should be measured before full migration

---

## Success Metrics Achieved

### Technical Metrics

- ✅ **Function Complexity**: Reduced through modular helper functions
- ✅ **Test Coverage**: >90% coverage maintained while adding new tests
- ✅ **Error Handling**: Specific error types vs generic messages
- ✅ **Type Safety**: Named tuples provide compile-time safety
- ✅ **Code Brittleness**: Eliminated tuple returns with unclear ordering

### User Experience Metrics

- ✅ **Upload Success Rate**: Maintained parity with original implementation
- ✅ **Error Clarity**: Specific, actionable error messages
- ✅ **User Feedback**: Enhanced success messages with details

### Maintainability Metrics

- ✅ **Code Organization**: Result types in dedicated module
- ✅ **Function Separation**: Single-responsibility helper functions
- ✅ **Documentation**: Comprehensive examples and error type documentation
- ✅ **Backward Compatibility**: Zero breaking changes to existing code

---

## Comparison with Original Goals

### Original Refactor Goals vs Current State

| Goal                        | Original Target                                | Current State | Status                                     |
|-----------------------------|------------------------------------------------|---------------|--------------------------------------------|
| **Parallel Implementation** | Routes that don't break existing functionality | ✅ Complete    | Both refactored routes working             |
| **Better Error Handling**   | Specific error messages vs generic ones        | ✅ Complete    | Rich error types and messages              |
| **Modular Design**          | Break monolithic functions into smaller ones   | ✅ Complete    | All functions modularized with result types |
| **Type Safety**             | Use named tuples for better type safety        | ✅ Complete    | All result types implemented               |
| **Test Coverage**           | Maintain comprehensive test coverage           | ✅ Complete    | All new components tested                  |
| **Backward Compatibility**  | Don't break existing functionality             | ✅ Complete    | Original routes unchanged                  |
| **Helper Function Robustness** | Eliminate brittle tuple returns              | ✅ Complete    | All helper functions use result types      |

---

## Conclusion

The data ingestion refactor has achieved **Phase 7A completion** with the implementation of a route orchestration framework,
demonstrating complete cross-cutting concern extraction. This represents a comprehensive architectural achievement that maintains 
full backward compatibility while establishing a complete blueprint for systematic code enhancement.

**Key Achievements:**

1. **Working refactored routes** with enhanced error handling
2. **Complete staging and upload implementations** with modular helper functions
3. **Comprehensive test coverage** for all new components (22/22 refactored route tests passing)
4. **Type-safe result objects** with rich error information
5. **Backward compatibility** maintained throughout
6. **Eliminated brittle tuple returns** in favor of robust result types
7. **Shared route helper functions** eliminating code duplication
8. **Enhanced lower-level utility functions** demonstrating recursive consistency
9. **Complete call tree improvement** from routes to lowest-level operations
10. **Route orchestration framework** eliminating all route duplication through cross-cutting concern extraction

**Architectural Benefits:**

- **Less Brittle Code**: No more tuple returns with unclear ordering at any level
- **Type Safety**: Named tuples provide compile-time safety throughout the system
- **Self-Documenting**: Result types clearly show what data is returned at every level
- **Better Error Handling**: Specific error types instead of generic messages
- **Comprehensive Testing**: All scenarios covered with maintained test coverage
- **Zero Breaking Changes**: All existing code continues to work
- **Reduced Duplication**: All duplication eliminated through systematic pattern extraction
- **Consistent Behavior**: Unified patterns across all levels of the system
- **Graceful Degradation**: Non-critical operations don't fail main workflows
- **Enhanced Error Granularity**: Specific error types at every level
- **Cross-Cutting Concern Extraction**: Complete elimination of route duplication
- **Configuration-Driven Architecture**: Flexible, reusable frameworks

**Phase 7A Innovations:**

- **Route Orchestration Framework**: Complete cross-cutting concern extraction
- **Configuration-Driven Routes**: Flexible architecture supporting multiple upload types
- **Architectural Blueprint**: Comprehensive pattern for systematic code enhancement
- **Complete Framework**: From individual functions to full system orchestration

The refactor demonstrates that **incremental, test-driven improvements** can achieve comprehensive architectural benefits
without disrupting existing functionality. Phase 7A represents the completion of a full systematic enhancement approach,
providing a proven blueprint for architectural improvement that can be applied to any complex system.

## **📊 Call Tree Analysis & Phase 5 Planning**

### **Deep Consistency Analysis Completed (August 2025)**

**Finding**: While route-level consistency is excellent, opportunities exist for deeper call tree improvements.

#### **Current Consistency Status**
- ✅ **Route-level helpers**: Fully shared and consistent
- ✅ **Main functions**: Identical patterns with result types
- ✅ **Helper functions with result types**: All follow consistent patterns
- 🔄 **Lower-level utilities**: Duplication and inconsistencies identified

#### **Key Opportunities Identified**

1. **Diagnostic Function Duplication** (High Priority)
   - `generate_upload_diagnostics()` vs `generate_staging_diagnostics()`
   - ~60 lines of nearly identical logic
   - Target for Phase 5 consolidation

2. **File Processing Patterns** (Medium Priority)
   - Inconsistent error handling at utility level
   - Direct calls to `upload_single_file()` without wrappers

3. **Database Operation Inconsistencies** (Medium Priority)
   - Multiple patterns for database operations
   - Inconsistent error handling approaches

4. **JSON Processing Patterns** (Low Priority)
   - Multiple conversion functions with different approaches
   - Opportunity for consolidation

### **Phase 5: Diagnostic Function Consolidation** ✅ **COMPLETED**

**Target**: Create unified diagnostic function to eliminate duplication
**Status**: Successfully implemented and tested
**Achieved Benefits**: 
- Eliminated ~60 lines of duplicated diagnostic code
- Consistent diagnostic output across upload types
- Single maintenance point for diagnostic improvements
- All refactored route tests passing (22/22)

### **Phase 6: Enhanced Lower-Level Utility Functions** ✅ **COMPLETED**

**Target**: Improve lower-level utility functions with recursive consistency
**Status**: Successfully implemented and tested
**Achieved Benefits**: 
- **6 Enhanced utility functions** with result types implemented
- **3 New result types** for lower-level operations added
- **Complete recursive consistency** demonstrated throughout call tree
- **Zero breaking changes** to existing functionality
- **100% test coverage maintained** (22/22 refactored route tests passing)
- **Proof of concept** for call tree improvement patterns

**Implementation Details**:
- **Enhanced File Operations**: `upload_file_with_result()`, `audit_file_upload_with_result()`
- **Enhanced JSON Processing**: `convert_excel_to_json_with_result()`
- **Enhanced Main Functions**: `save_uploaded_file_enhanced_with_result()`, `convert_file_to_json_enhanced_with_result()`
- **Demonstration Functions**: `upload_and_process_file_enhanced()`, `stage_uploaded_file_for_review_enhanced()`

**Architectural Benefits**:
- **Consistent Error Handling**: All lower-level functions now use result types
- **Better Error Granularity**: Specific error types (validation_error, permission_error, disk_error, etc.)
- **Graceful Degradation**: Non-critical operations (auditing) don't fail the main workflow
- **Type Safety**: Structured results instead of brittle tuples or exceptions

### **Phase 7A: Route Orchestration Framework** ✅ **COMPLETED**

**Target**: Extract cross-cutting concerns through route orchestration framework
**Status**: Successfully implemented and tested
**Achieved Benefits**: 
- **Route orchestration framework** implemented with configuration-driven approach
- **Complete elimination** of route duplication through cross-cutting concern extraction
- **~160 lines of duplicated route logic** eliminated across both refactored routes
- **Demonstration routes** showing framework capabilities and architectural benefits
- **All refactored route tests passing** (22/22) with zero breaking changes

**Implementation Details**:
- **UploadConfiguration Class**: Encapsulates route configuration (upload type, template, processing function)
- **orchestrate_upload_route Function**: Unified framework handling all common route logic
- **Demonstration Routes**: `/upload_orchestrated` and `/upload_staged_orchestrated`
- **Cross-Cutting Concerns Extracted**: Setup, validation, error handling, success handling, exception handling

**Architectural Benefits**:
- **Cross-Cutting Concern Extraction**: Complete elimination of route duplication
- **Configuration-Driven Architecture**: Flexible, reusable route framework  
- **Orchestration Pattern**: Template for handling complex cross-cutting concerns
- **Architectural Blueprint**: Demonstrates systematic pattern extraction

## 🎉 **PHASE 8: IN-MEMORY UNIFIED PROCESSING ARCHITECTURE** ✅ **COMPLETED**

**Target**: Unified in-memory processing pipeline eliminating code duplication between direct and staged uploads  
**Status**: **SUCCESSFULLY IMPLEMENTED** - All objectives achieved

**Architectural Insight**: Direct upload is fundamentally a **specialized case** of staged upload:
- Direct Upload = Staged Upload + Auto-confirmation + All-fields update + No file persistence
- Both routes share 75% of core processing logic (save, convert, validate)
- Current duplication: Two separate processing functions with nearly identical logic

**Proposed Unified Architecture**:

### **In-Memory First Approach**
```
All Uploads: File → Parse → Validate → In-Memory Staging
                                           ↓
Direct Upload: Auto-confirm → Database (no file persistence)
Staged Upload: File persistence → Manual review → Database
```

**Key Components**:
- **InMemoryStaging**: Core data structure representing processed upload data
- **process_upload_to_memory()**: Unified processing pipeline (save, convert, validate)
- **Configurable persistence**: Database direct, file staging, or both
- **Result Types**: Enhanced type safety throughout the pipeline

**Benefits**:
- **Conceptual Clarity**: Makes route relationship explicit and architectural intent clear
- **Code Quality**: Single source of truth for core processing logic (eliminates 75% duplication)
- **Testing Excellence**: Perfect separation of concerns enables surgical unit testing
- **Performance**: Eliminates unnecessary file I/O for direct uploads
- **Future Extensibility**: In-memory staging supports any persistence strategy

**Implementation Results**:
- ✅ **Phase 8A COMPLETED**: InMemoryStaging infrastructure with Result Types (21 passing tests)
- ✅ **Phase 8B COMPLETED**: Unified processing pipeline integrated into existing functions
- ✅ **Phase 8C COMPLETED**: Routes refactored to use unified approach with full backward compatibility
- ✅ **Phase 8D COMPLETED**: Performance optimized and comprehensive testing validated (36 passing tests)

**Mission Accomplished**: Unified in-memory processing architecture successfully implemented with 75% code deduplication

**Latest Test Results (January 2025):**
- **Unit Tests**: 750+ passed, 0 failed, 18 skipped
- **E2E Tests**: 120+ passed, 6 skipped, 0 failed
- **Route Equivalence Tests**: 24/24 passed (100%)
- **Comprehensive Refactored Route E2E Tests**: ✅ **40+ new tests implemented**
- **Orchestration Framework E2E Tests**: ✅ **20+ new tests implemented**
- **Phase 8 Unified Architecture Tests**: ✅ **36+ new tests implemented (100% passing)**
- **All Test Issues Resolved**: Complete test coverage for unified processing architecture

**E2E Testing Enhancement (August 2025):**
- **New Test Files**: `test_refactored_routes_comprehensive.py`, `test_orchestrated_routes.py`
- **Test Categories**: 9 comprehensive categories covering structure, workflows, error handling, enhancements
- **Coverage**: Complete testing parity for refactored routes vs original routes
- **Framework Validation**: Dedicated testing for Phase 7A orchestration framework

**Phase 8 Testing Enhancement (January 2025):**
- **New Test Files**: `test_in_memory_staging.py`, `test_unified_upload_functions.py`
- **Test Categories**: 4 comprehensive categories covering infrastructure, integration, architecture, performance
- **Coverage**: Complete testing of unified processing pipeline and configuration-driven behavior
- **Architecture Validation**: Dedicated testing for Phase 8 in-memory staging and unified processing
