/**
 * Toast Notification Manager for ARB Feedback Portal
 * Handles success, error, warning, and info notifications
 */

class ToastManager {
  /**
   * Show a toast notification
   * @param {string} message - The message to display
   * @param {string} type - The type of notification (success, error, warning, info)
   * @param {object} options - Additional options
   */
  static show(message, type = 'info', options = {}) {
    const toast = document.createElement('div');
    toast.className = `toast ${options.class || ''}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    // Determine icon based on type
    const icons = {
      'success': '✅',
      'error': '❌',
      'warning': '⚠️',
      'info': 'ℹ️'
    };
    
    const icon = icons[type] || icons.info;
    const title = options.title || this.getDefaultTitle(type);
    
    toast.innerHTML = `
      <div class="toast-header bg-${type} text-white">
        <strong>${icon} ${title}</strong>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">${message}</div>
    `;
    
    const container = document.querySelector('.toast-container');
    if (container) {
      container.appendChild(toast);
      const bsToast = new bootstrap.Toast(toast, { 
        delay: options.delay || 5000,
        autohide: options.autohide !== false
      });
      bsToast.show();
      
      // Auto-remove after showing
      toast.addEventListener('hidden.bs.toast', () => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      });
    }
  }
  
  /**
   * Get default title based on notification type
   */
  static getDefaultTitle(type) {
    const titles = {
      'success': 'Success',
      'error': 'Error',
      'warning': 'Warning',
      'info': 'Information'
    };
    return titles[type] || 'Notification';
  }
  
  /**
   * Show success notification
   */
  static success(message, options = {}) {
    this.show(message, 'success', options);
  }
  
  /**
   * Show error notification
   */
  static error(message, options = {}) {
    this.show(message, 'danger', { ...options, delay: options.delay || 8000 });
  }
  
  /**
   * Show warning notification
   */
  static warning(message, options = {}) {
    this.show(message, 'warning', options);
  }
  
  /**
   * Show info notification
   */
  static info(message, options = {}) {
    this.show(message, 'info', options);
  }
  
  /**
   * Show staged upload success notification
   */
  static stagedUploadSuccess(filename, id, options = {}) {
    const message = `
      <strong>${filename}</strong> has been staged for review.<br>
      <a href="/review_staged/${id}/${filename}" class="btn btn-sm btn-primary mt-2">
        👁️ Review Now
      </a>
    `;
    this.success(message, { 
      title: 'File Staged Successfully',
      delay: 10000,
      ...options 
    });
  }
  
  /**
   * Show changes applied success notification
   */
  static changesAppliedSuccess(fieldCount, id, options = {}) {
    const message = `
      <strong>${fieldCount} fields</strong> updated for ID ${id}.<br>
      <small class="text-muted">Staged file moved to processed directory</small>
    `;
    this.success(message, { 
      title: 'Changes Applied Successfully',
      ...options 
    });
  }
  
  /**
   * Show concurrent changes warning
   */
  static concurrentChangesWarning(id, filename, options = {}) {
    const message = `
      The database was modified by another user. Please review the current state and reconfirm your changes.
      <a href="/review_staged/${id}/${filename}" class="btn btn-sm btn-danger mt-2">
        Review Again
      </a>
    `;
    this.error(message, { 
      title: 'Concurrent Changes Detected',
      delay: 15000,
      ...options 
    });
  }
  
  /**
   * Show file discarded notification
   */
  static fileDiscarded(id, options = {}) {
    const message = `Staged file for ID ${id} has been removed.`;
    this.info(message, { 
      title: 'File Discarded',
      ...options 
    });
  }
}

// Make ToastManager available globally
window.ToastManager = ToastManager; 