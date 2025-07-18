/**
 * @fileoverview DataTables initialization and configuration for portal tables
 * 
 * This script handles the initialization and configuration of DataTables
 * for various portal pages including staged files list and portal updates.
 * 
 * Features:
 * - Staged files table with sorting and pagination
 * - Portal updates table with fixed header and date filtering
 * - Consistent styling and behavior across tables
 * - Discard confirmation dialogs for staged files
 * 
 * Functions:
 * - initializeStagedFilesTable() - Sets up staged files DataTable with custom language
 * - initializePortalUpdatesTable() - Configures portal updates table with filters and date pickers
 * - initializeDiscardConfirmations() - Adds confirmation dialogs for staged file deletion
 * 
 * Requirements:
 * - jQuery must be loaded
 * - DataTables CSS and JS must be loaded
 * - Bootstrap 5 DataTables integration
 */
window.addEventListener('DOMContentLoaded', function() {
    if (typeof logToDiagnostics === 'function') {
        logToDiagnostics('[JS_DIAG] [table_management] /list_staged page loaded');
        sendJsDiagnostic('/list_staged page loaded (table_management.js)', {source: 'table_management.js'});
    }
    // Initialize staged files table
    initializeStagedFilesTable();
    
    // Initialize portal updates table
    initializePortalUpdatesTable();
    
    // Initialize discard confirmations
    initializeDiscardConfirmations();
});

/**
 * Initializes the staged files DataTable
 * Configures sorting, pagination, and search functionality
 */
function initializeStagedFilesTable() {
    const stagedTable = document.getElementById('stagedTable');
    if (!stagedTable) return;
    
    $(stagedTable).DataTable({
        order: [[4, 'desc']], // Sort by staged time (newest first)
        pageLength: 25,
        language: {
            search: "🔍 Search staged files:",
            lengthMenu: "Show _MENU_ files per page",
            info: "Showing _START_ to _END_ of _TOTAL_ staged files"
        }
    });
}

/**
 * Initializes the portal updates DataTable with advanced features
 * Includes fixed header, date pickers, and filter controls
 */
function initializePortalUpdatesTable() {
    const updatesTable = document.getElementById('updatesTable');
    if (!updatesTable) return;
    
    const $toggleIcon = $('#toggle-icon');
    const $filtersCollapse = $('#filtersCollapse');
    
    // Toggle icon setup for filter collapse
    $filtersCollapse.on('show.bs.collapse', function () {
        $toggleIcon.text('➖');
    });
    
    $filtersCollapse.on('hide.bs.collapse', function () {
        $toggleIcon.text('➕');
    });
    
    // DataTables setup with fixed header
    const table = $('#updatesTable').DataTable({
        pageLength: 100,
        lengthMenu: [50, 100, 200, 500],
        order: [[0, 'desc']], // Sort by timestamp descending
        fixedHeader: {
            header: true,
            headerOffset: $('.navbar').outerHeight() || 56
        }
    });
    
    // Initialize date pickers if flatpickr is available
    if (typeof flatpickr !== 'undefined') {
        flatpickr("#start_date", {dateFormat: "Y-m-d"});
        flatpickr("#end_date", {dateFormat: "Y-m-d"});
    }
    
    // Clear filters functionality
    $('#clear-filters').on('click', function () {
        $('input[type="text"]').val('');
        $('form').trigger('submit');
    });
}

/**
 * Initializes discard confirmation dialogs for staged files
 * Replaces inline onsubmit handlers with proper event listeners
 */
function initializeDiscardConfirmations() {
    // Find all discard forms in the staged files table
    const discardForms = document.querySelectorAll('form[action*="discard_staged_update"]');
    
    discardForms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (typeof logToDiagnostics === 'function') {
                logToDiagnostics('[JS_DIAG] [table_management] Discard button clicked for action: ' + form.action);
                sendJsDiagnostic('Discard button clicked (table_management.js)', {action: form.action, source: 'table_management.js'});
            }
            const confirmed = confirm('Are you sure you want to discard this staged file?');
            if (!confirmed) {
                event.preventDefault();
                if (typeof logToDiagnostics === 'function') {
                    logToDiagnostics('[JS_DIAG] [table_management] Discard cancelled for action: ' + form.action);
                    sendJsDiagnostic('Discard cancelled (table_management.js)', {action: form.action, source: 'table_management.js'});
                }
            } else {
                if (typeof logToDiagnostics === 'function') {
                    logToDiagnostics('[JS_DIAG] [table_management] Discard confirmed for action: ' + form.action);
                    sendJsDiagnostic('Discard confirmed (table_management.js)', {action: form.action, source: 'table_management.js'});
                }
            }
        });
    });
} 