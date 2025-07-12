// PWA-specific functionality
class PWAManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.offlineQueue = [];
        this.installPrompt = null;
        this.init();
    }

    init() {
        // Monitor online/offline status
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showConnectionStatus('Connected', 'success');
            this.processOfflineQueue();
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showConnectionStatus('Offline', 'warning');
        });

        // Listen for install prompt
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.installPrompt = e;
            this.showInstallButton();
        });

        // Show install status
        window.addEventListener('appinstalled', () => {
            this.showConnectionStatus('App Installed Successfully!', 'success');
            this.hideInstallButton();
        });
    }

    showConnectionStatus(message, type) {
        const statusDiv = document.createElement('div');
        statusDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        statusDiv.style.cssText = 'top: 20px; left: 20px; z-index: 9999; max-width: 300px;';
        statusDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(statusDiv);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (statusDiv.parentNode) {
                statusDiv.parentNode.removeChild(statusDiv);
            }
        }, 3000);
    }

    showInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'block';
        }
    }

    hideInstallButton() {
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.style.display = 'none';
        }
    }

    async installApp() {
        if (!this.installPrompt) return;

        try {
            await this.installPrompt.prompt();
            const result = await this.installPrompt.userChoice;
            
            if (result.outcome === 'accepted') {
                this.showConnectionStatus('Installing app...', 'info');
            }
            
            this.installPrompt = null;
            this.hideInstallButton();
        } catch (error) {
            console.error('Installation failed:', error);
            this.showConnectionStatus('Installation failed', 'danger');
        }
    }

    // Queue operations for offline sync
    queueOperation(operation) {
        if (!this.isOnline) {
            this.offlineQueue.push(operation);
            this.showConnectionStatus('Operation queued for sync', 'info');
        }
    }

    async processOfflineQueue() {
        if (this.offlineQueue.length === 0) return;

        this.showConnectionStatus('Syncing offline data...', 'info');
        
        for (const operation of this.offlineQueue) {
            try {
                await this.executeOperation(operation);
            } catch (error) {
                console.error('Sync failed for operation:', operation, error);
            }
        }
        
        this.offlineQueue = [];
        this.showConnectionStatus('Sync complete', 'success');
    }

    async executeOperation(operation) {
        // Execute queued operations when back online
        return fetch(operation.url, {
            method: operation.method || 'GET',
            headers: operation.headers || {},
            body: operation.body || null
        });
    }

    // Cache management
    async clearCache() {
        if ('caches' in window) {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
            this.showConnectionStatus('Cache cleared', 'info');
        }
    }

    // Storage management
    getStorageUsage() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            return navigator.storage.estimate();
        }
        return null;
    }

    // Notification permissions
    async requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }

    // Show notification
    showNotification(title, options = {}) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                icon: '/static/icons/icon-192x192.png',
                badge: '/static/icons/icon-72x72.png',
                ...options
            });
        }
    }
}

// Initialize PWA manager
const pwaManager = new PWAManager();

// Export for global use
window.pwaManager = pwaManager;