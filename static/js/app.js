// Main application JavaScript

// Theme management
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update any existing charts to match new theme
    updateChartsTheme(newTheme);
}

// Load saved theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize other components
    initializeComponents();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize other components
function initializeComponents() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
    
    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                
                // Re-enable after 30 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 30000);
            }
        });
    });
}

// Update charts theme
function updateChartsTheme(theme) {
    // This will be used by chart components
    window.currentTheme = theme;
    
    // Redraw existing Plotly charts with new theme
    const chartElements = document.querySelectorAll('[id^="chart_"]');
    chartElements.forEach(el => {
        if (window.Plotly && window.Plotly.restyle) {
            const template = theme === 'dark' ? 'plotly_dark' : 'plotly_white';
            window.Plotly.relayout(el, {
                template: template,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            });
        }
    });
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// File validation
function validateFile(file, maxSize = 16 * 1024 * 1024) {
    const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
    const allowedExtensions = ['.csv', '.xlsx', '.xls'];
    
    // Check file size
    if (file.size > maxSize) {
        return {
            valid: false,
            message: `File size must be less than ${formatBytes(maxSize)}`
        };
    }
    
    // Check file type
    const fileName = file.name.toLowerCase();
    const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
    const hasValidType = allowedTypes.includes(file.type);
    
    if (!hasValidExtension && !hasValidType) {
        return {
            valid: false,
            message: 'Please select a valid CSV or Excel file'
        };
    }
    
    return { valid: true };
}

// Progress tracking
function updateProgress(elementId, percentage, message = '') {
    const progressElement = document.getElementById(elementId);
    if (progressElement) {
        const progressBar = progressElement.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            if (message) {
                progressBar.textContent = message;
            }
        }
    }
}

// Error handling
function showError(message, containerId = null) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = alertHtml;
        }
    } else {
        // Add to top of main content
        const main = document.querySelector('main.container');
        if (main) {
            main.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }
}

// Success messages
function showSuccess(message, containerId = null) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    if (containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = alertHtml;
        }
    } else {
        const main = document.querySelector('main.container');
        if (main) {
            main.insertAdjacentHTML('afterbegin', alertHtml);
        }
    }
}

// Local storage helpers
function saveToStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Error saving to localStorage:', e);
        return false;
    }
}

function loadFromStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error loading from localStorage:', e);
        return defaultValue;
    }
}

// Export helpers
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + U for upload
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        const uploadLink = document.querySelector('a[href*="upload"]');
        if (uploadLink) {
            uploadLink.click();
        }
    }
    
    // Ctrl/Cmd + D for dashboard
    if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        const dashboardLink = document.querySelector('a[href*="dashboard"]');
        if (dashboardLink) {
            dashboardLink.click();
        }
    }
    
    // Ctrl/Cmd + Shift + T for theme toggle
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
        e.preventDefault();
        toggleTheme();
    }
});

// Responsive table helper
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table:not(.table-responsive table)');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialize responsive tables on page load
document.addEventListener('DOMContentLoaded', makeTablesResponsive);

// Global error handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Could send error to logging service here
});

// Page visibility change handler
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, pause any intensive operations
        console.log('Page hidden');
    } else {
        // Page is visible, resume operations
        console.log('Page visible');
    }
});
