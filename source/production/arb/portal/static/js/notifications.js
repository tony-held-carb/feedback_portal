/**
 * @fileoverview Toast notification system for the ARB Feedback Portal
 * 
 * This script provides a comprehensive toast notification system that can be used
 * throughout the portal to show success, error, warning, and info messages.
 * 
 * Features:
 * - Multiple notification types (success, error, warning, info)
 * - Auto-dismiss with configurable delays
 * - Manual dismiss functionality
 * - Flash message integration
 * - Upload progress notifications
 * - Responsive design with Bootstrap styling
 * 
 * Usage:
 * - ToastManager.show(message, type, options)
 * - ToastManager.success(message, options)
 * - ToastManager.error(message, options)
 * - ToastManager.warning(message, options)
 * - ToastManager.info(message, options)
 * - ToastManager.handleFlashMessages() - Auto-process flash messages
 * - ToastManager.showUploadProgress() - Show upload progress notification
 */
class ToastManager {
    constructor() {
        this.container = this.createContainer();
        this.toastCount = 0;
    }

    /**
     * Creates the toast container if it doesn't exist
     * @returns {HTMLElement} The toast container element
     */
    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        return container;
    }

    /**
     * Shows a toast notification
     * @param {string} message - The message to display
     * @param {string} type - The type of notification (success, error, warning, info)
     * @param {Object} options - Additional options (title, delay, etc.)
     */
    show(message, type = 'info', options = {}) {
        const {
            title = this.getDefaultTitle(type),
            delay = this.getDefaultDelay(type),
            dismissible = true
        } = options;

        const toast = this.createToast(message, type, title, dismissible);
        this.container.appendChild(toast);

        // Trigger the toast animation
        const bsToast = new bootstrap.Toast(toast, { delay: delay });
        bsToast.show();

        // Auto-remove from DOM after animation
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        this.toastCount++;
        return toast;
    }

    /**
     * Shows a success notification
     * @param {string} message - The success message
     * @param {Object} options - Additional options
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    /**
     * Shows an error notification
     * @param {string} message - The error message
     * @param {Object} options - Additional options
     */
    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    /**
     * Shows a warning notification
     * @param {string} message - The warning message
     * @param {Object} options - Additional options
     */
    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }

    /**
     * Shows an info notification
     * @param {string} message - The info message
     * @param {Object} options - Additional options
     */
    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    /**
     * Creates a toast element with Bootstrap styling
     * @param {string} message - The message content
     * @param {string} type - The notification type
     * @param {string} title - The toast title
     * @param {boolean} dismissible - Whether the toast can be dismissed
     * @returns {HTMLElement} The toast element
     */
    createToast(message, type, title, dismissible) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${this.getBootstrapClass(type)} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');

        const icon = this.getIcon(type);
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${title ? `<strong>${title}</strong><br>` : ''}
                    ${message}
                </div>
                ${dismissible ? `
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                            data-bs-dismiss="toast" aria-label="Close"></button>
                ` : ''}
            </div>
        `;

        return toast;
    }

    /**
     * Gets the Bootstrap CSS class for the notification type
     * @param {string} type - The notification type
     * @returns {string} The Bootstrap class name
     */
    getBootstrapClass(type) {
        const classes = {
            success: 'success',
            error: 'danger',
            warning: 'warning',
            info: 'info'
        };
        return classes[type] || 'info';
    }

    /**
     * Gets the default title for the notification type
     * @param {string} type - The notification type
     * @returns {string} The default title
     */
    getDefaultTitle(type) {
        const titles = {
            success: '✅ Success',
            error: '❌ Error',
            warning: '⚠️ Warning',
            info: 'ℹ️ Info'
        };
        return titles[type] || 'ℹ️ Info';
    }

    /**
     * Gets the default delay for the notification type
     * @param {string} type - The notification type
     * @returns {number} The delay in milliseconds
     */
    getDefaultDelay(type) {
        const delays = {
            success: 5000,
            error: 8000,
            warning: 6000,
            info: 4000
        };
        return delays[type] || 4000;
    }

    /**
     * Gets the icon for the notification type
     * @param {string} type - The notification type
     * @returns {string} The icon HTML
     */
    getIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || 'ℹ️';
    }

    /**
     * Automatically processes flash messages from the page
     * Converts Bootstrap alerts to toast notifications
     */
    handleFlashMessages() {
        const flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(function(alert) {
            const message = alert.textContent.trim();
            const category = alert.classList.contains('alert-success') ? 'success' :
                            alert.classList.contains('alert-danger') ? 'error' :
                            alert.classList.contains('alert-warning') ? 'warning' : 'info';
            
            // Show toast notification
            this.show(message, category);
            
            // Hide the original alert
            alert.style.display = 'none';
        }.bind(this));
    }

    /**
     * Shows upload progress notification
     * @param {Object} options - Options for the upload notification
     */
    showUploadProgress(options = {}) {
        const defaultOptions = {
            title: 'Upload in Progress',
            message: 'Processing your file...',
            delay: 3000
        };
        
        return this.info(defaultOptions.message, {
            title: defaultOptions.title,
            delay: defaultOptions.delay,
            ...options
        });
    }
}

// Create global instance
window.ToastManager = new ToastManager();

// Auto-process flash messages when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (window.ToastManager) {
        window.ToastManager.handleFlashMessages();
    }
}); 