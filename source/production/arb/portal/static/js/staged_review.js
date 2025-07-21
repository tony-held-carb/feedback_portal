/**
 * @fileoverview Review staged upload functionality with table filtering and confirmation logic
 *
 * This script handles the review interface for staged uploads, including:
 * - Table filtering and visibility controls
 * - Confirmation checkbox management
 * - DataTables integration with fixed headers
 * - Context-aware notifications
 *
 * Features:
 * - Hide/show unchanged fields
 * - Search/filter fields by name or value
 * - Select all/none confirmation checkboxes
 * - Responsive table with fixed headers
 * - Automatic notification based on context
 *
 * Classes:
 * - ReviewStagedManager - Main class for managing the review interface
 *
 * Methods:
 * - constructor(options) - Initializes the manager with configuration
 * - init() - Sets up event listeners and initial state
 * - setupEventListeners() - Attaches all event handlers
 * - updateVisibleRows() - Filters table rows based on user preferences
 * - updateConfirmAllState() - Manages select-all checkbox state
 * - initializeDataTable() - Sets up DataTable with custom configuration
 * - showContextNotifications() - Shows appropriate notifications based on data
 *
 * Requirements:
 * - jQuery and DataTables must be loaded
 * - Template must pass staged_fields data
 * - ToastManager must be available for notifications
 */
class ReviewStagedManager {
    constructor(options = {}) {
        this.options = {
            changedCount: options.changedCount || 0,
            confirmCount: options.confirmCount || 0,
            isNewRow: options.isNewRow || false,
            ...options
        };

        this.selectAllBox = document.getElementById("selectAllConfirmations");
        this.hideUnchangedCheckbox = document.getElementById("hideUnchangedFields");
        this.fieldSearchInput = document.getElementById("fieldSearch");
        this.reviewTable = document.getElementById("reviewTable");

        this.init();
    }

    /**
     * Initializes the review staged interface
     * Sets up event listeners and initial state
     */
    init() {
        if (!this.selectAllBox || !this.hideUnchangedCheckbox || !this.fieldSearchInput) {
            console.warn("ReviewStagedManager: Missing required elements");
            return;
        }

        // Set up event listeners
        this.setupEventListeners();

        // Initialize DataTable
        this.initializeDataTable();

        // Set initial state
        this.updateVisibleRows();
        this.updateConfirmAllState();

        // Show context-aware notifications
        this.showContextNotifications();
    }

    /**
     * Sets up all event listeners for the interface
     */
    setupEventListeners() {
        // Hide unchanged fields toggle
        this.hideUnchangedCheckbox.addEventListener("change", () => {
            this.updateVisibleRows();
        });

        // Field search/filter
        this.fieldSearchInput.addEventListener("input", () => {
            this.updateVisibleRows();
        });

        // Select all confirmations
        this.selectAllBox.addEventListener("change", () => {
            document.querySelectorAll(".confirm-checkbox").forEach(cb => {
                cb.checked = this.selectAllBox.checked;
            });
            this.updateConfirmAllState();
        });

        // Individual confirmation checkboxes
        document.querySelectorAll(".confirm-checkbox").forEach(cb => {
            cb.addEventListener("change", () => {
                this.updateConfirmAllState();
            });
        });
    }

    /**
     * Updates the visibility of table rows based on filters
     * Handles both the "hide unchanged" toggle and search filter
     */
    updateVisibleRows() {
        const hideUnchanged = this.hideUnchangedCheckbox.checked;
        const query = this.fieldSearchInput.value.toLowerCase();

        document.querySelectorAll("tbody tr").forEach(function (row) {
            const isUnchanged = row.classList.contains("unchanged-field");
            const matchesFilter = row.innerText.toLowerCase().includes(query);
            row.style.display = matchesFilter && (!hideUnchanged || !isUnchanged) ? "" : "none";
        });
    }

    /**
     * Updates the state of the "select all" checkbox
     * Handles indeterminate state when some but not all are selected
     */
    updateConfirmAllState() {
        const checkboxes = document.querySelectorAll(".confirm-checkbox");
        const checkedCount = [...checkboxes].filter(cb => cb.checked).length;

        if (checkedCount === 0) {
            this.selectAllBox.indeterminate = false;
            this.selectAllBox.checked = false;
        } else if (checkedCount === checkboxes.length) {
            this.selectAllBox.indeterminate = false;
            this.selectAllBox.checked = true;
        } else {
            this.selectAllBox.indeterminate = true;
            this.selectAllBox.checked = false;
        }
    }

    /**
     * Initializes the DataTable with fixed headers and custom configuration
     */
    initializeDataTable() {
        if (!this.reviewTable || typeof $ === 'undefined') return;

        $('#reviewTable').DataTable({
            fixedHeader: {
                header: true,
                headerOffset: $('.navbar').outerHeight() || 56
            },
            paging: false,
            info: false,
            ordering: true,
            order: [],  // prevent default sort
            orderClasses: false,  // remove auto sorting classes
            stripeClasses: [],
            searching: false,
            columnDefs: [
                {orderable: false, targets: 0}  // Confirm column not sortable
            ]
        });
    }

    /**
     * Shows context-aware notifications based on the staged data
     * FALLBACK: If ToastManager is not available, uses console logging
     * TODO: Consider implementing Bootstrap alert fallback for better UX
     */
    showContextNotifications() {
        const {changedCount, confirmCount, isNewRow} = this.options;

        // Check if ToastManager is available (disabled in old system)
        if (!window.ToastManager) {
            // Fallback to console logging for debugging
            if (isNewRow) {
                console.info('New Record: This is a new record that will be created.');
            } else if (changedCount === 0) {
                console.warn('No Changes: No changes detected in the uploaded file.');
            } else if (confirmCount > 10) {
                console.warn(`Multiple Changes: Many changes detected (${confirmCount} fields). Review carefully.`);
            } else {
                console.info('Review Instructions: Check ✅ boxes for fields you want to update. Unchecked fields will remain unchanged.');
            }
            return;
        }

        // Original ToastManager implementation (commented out for old system)
        /*
        if (isNewRow) {
            window.ToastManager.info('This is a new record that will be created.', {
                title: 'New Record',
                delay: 8000
            });
        } else if (changedCount === 0) {
            window.ToastManager.warning('No changes detected in the uploaded file.', {
                title: 'No Changes',
                delay: 6000
            });
        } else if (confirmCount > 10) {
            window.ToastManager.warning(`Many changes detected (${confirmCount} fields). Review carefully.`, {
                title: 'Multiple Changes',
                delay: 10000
            });
        } else {
            window.ToastManager.info('Check ✅ boxes for fields you want to update. Unchecked fields will remain unchanged.', {
                title: 'Review Instructions',
                delay: 8000
            });
        }
        */
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get data from template variables (these will be set by the template)
    const reviewData = window.reviewStagedData || {};

    // Initialize the review manager
    new ReviewStagedManager(reviewData);
}); 