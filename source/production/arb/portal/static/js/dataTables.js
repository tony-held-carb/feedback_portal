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
 * 
 * Requirements:
 * - jQuery must be loaded
 * - DataTables CSS and JS must be loaded
 * - Bootstrap 5 DataTables integration
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize staged files table
    initializeStagedFilesTable();
    
    // Initialize portal updates table
    initializePortalUpdatesTable();
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