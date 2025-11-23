/**
 * Frontend Connectivity Manager for Sahaaya
 * Monitors internet connectivity and updates UI accordingly
 */

class ConnectivityManager {
    constructor() {
        this.isOnline = navigator.onLine;
        this.lastCheck = Date.now();
        this.checkInterval = 10000; // 10 seconds
        this.backendUrl = window.location.origin; // Assumes frontend served from same origin
        this.intervalId = null;
        
        this.statusCallbacks = [];
        
        this.init();
    }
    
    init() {
        // Listen to browser online/offline events
        window.addEventListener('online', () => this.handleOnlineStatus(true));
        window.addEventListener('offline', () => this.handleOnlineStatus(false));
        
        // Start periodic connectivity checks
        this.startMonitoring();
        
        // Initial status check
        this.checkConnectivity();
    }
    
    startMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        
        this.intervalId = setInterval(() => {
            this.checkConnectivity();
        }, this.checkInterval);
    }
    
    stopMonitoring() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
    
    async checkConnectivity() {
        try {
            // Method 1: Check backend connectivity
            const backendOnline = await this.checkBackendConnectivity();
            
            // Method 2: Check general internet connectivity
            const internetOnline = await this.checkInternetConnectivity();
            
            // Method 3: Browser online status
            const browserOnline = navigator.onLine;
            
            // Combine results for comprehensive assessment
            const isConnected = backendOnline && internetOnline && browserOnline;
            
            const connectivityInfo = {
                backend_available: backendOnline,
                internet_available: internetOnline,
                browser_online: browserOnline,
                overall_status: isConnected,
                last_check: new Date().toISOString(),
                check_method: 'comprehensive'
            };
            
            // Update status if changed
            if (this.isOnline !== isConnected) {
                this.isOnline = isConnected;
                this.handleConnectivityChange(connectivityInfo);
            }
            
            // Always update the status indicators
            this.updateStatusIndicators(connectivityInfo);
            
            return connectivityInfo;
            
        } catch (error) {
            console.error('Connectivity check failed:', error);
            
            // Fallback to browser status
            const fallbackStatus = navigator.onLine;
            if (this.isOnline !== fallbackStatus) {
                this.isOnline = fallbackStatus;
                this.handleConnectivityChange({
                    backend_available: false,
                    internet_available: fallbackStatus,
                    browser_online: fallbackStatus,
                    overall_status: fallbackStatus,
                    last_check: new Date().toISOString(),
                    check_method: 'fallback',
                    error: error.message
                });
            }
            
            return {
                backend_available: false,
                internet_available: fallbackStatus,
                overall_status: fallbackStatus,
                error: error.message
            };
        }
    }
    
    async checkBackendConnectivity() {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
            
            const response = await fetch(`https://sahaaya-rvuy.onrender.com/connectivity-status`, {
                method: 'GET',
                signal: controller.signal,
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                this.lastBackendResponse = data;
                return true;
            }
            
            return false;
            
        } catch (error) {
            console.warn('Backend connectivity check failed:', error.name);
            return false;
        }
    }
    
    async checkInternetConnectivity() {
        try {
            // Use a reliable, fast endpoint
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
            
            const response = await fetch('https://dns.google/resolve?name=google.com&type=A', {
                method: 'GET',
                signal: controller.signal,
                mode: 'cors',
                cache: 'no-cache'
            });
            
            clearTimeout(timeoutId);
            
            return response.ok;
            
        } catch (error) {
            // Try fallback method
            try {
                const img = new Image();
                return new Promise((resolve) => {
                    img.onload = () => resolve(true);
                    img.onerror = () => resolve(false);
                    img.src = 'https://www.google.com/favicon.ico?' + Date.now();
                    
                    // Timeout after 3 seconds
                    setTimeout(() => resolve(false), 3000);
                });
            } catch (fallbackError) {
                return false;
            }
        }
    }
    
    handleOnlineStatus(online) {
        console.log(`Browser online status changed: ${online}`);
        
        // Immediate connectivity check when browser status changes
        setTimeout(() => {
            this.checkConnectivity();
        }, 1000);
    }
    
    handleConnectivityChange(connectivityInfo) {
        console.log('Connectivity changed:', connectivityInfo);
        
        // Notify all callbacks
        this.statusCallbacks.forEach(callback => {
            try {
                callback(connectivityInfo);
            } catch (error) {
                console.error('Connectivity callback error:', error);
            }
        });
        
        // Update UI
        this.updateStatusIndicators(connectivityInfo);
        this.showConnectivityNotification(connectivityInfo);
    }
    
    updateStatusIndicators(connectivityInfo) {
        // Update connectivity status indicator
        const connectivityIndicator = document.getElementById('connectivity-status');
        if (connectivityIndicator) {
            const icon = connectivityIndicator.querySelector('i');
            const text = connectivityIndicator.querySelector('span');
            
            if (connectivityInfo.overall_status) {
                connectivityIndicator.className = 'status-indicator online';
                icon.className = 'fas fa-wifi';
                text.textContent = 'Online';
            } else {
                connectivityIndicator.className = 'status-indicator offline';
                icon.className = 'fas fa-wifi-slash';
                text.textContent = 'Offline';
            }
        }
        
        // Update mode indicator
        const modeIndicator = document.getElementById('current-mode');
        if (modeIndicator) {
            if (connectivityInfo.backend_available && connectivityInfo.internet_available) {
                modeIndicator.textContent = 'Hybrid Mode';
            } else if (connectivityInfo.backend_available) {
                modeIndicator.textContent = 'Local Mode';
            } else {
                modeIndicator.textContent = 'Offline Mode';
            }
        }
        
        // Update footer info
        const footerModeInfo = document.getElementById('footer-mode-info');
        if (footerModeInfo) {
            if (connectivityInfo.overall_status) {
                footerModeInfo.textContent = '🌐 Online Mode: AI-enhanced guidance available';
            } else {
                footerModeInfo.textContent = '📱 Offline Mode: Local database active';
            }
        }
        
        // Update any mode-specific UI elements
        this.updateModeSpecificUI(connectivityInfo);
    }
    
    updateModeSpecificUI(connectivityInfo) {
        // Enable/disable features based on connectivity
        const voiceBtn = document.getElementById('voice-input-btn');
        const textBtn = document.getElementById('text-input-btn');
        
        if (!connectivityInfo.overall_status) {
            // In offline mode, prefer text input as it's more reliable
            if (voiceBtn) {
                voiceBtn.title = 'Voice input may be limited offline';
            }
            
            // Show offline mode indicators
            document.body.classList.add('offline-mode');
        } else {
            // Online mode
            if (voiceBtn) {
                voiceBtn.title = 'Voice input with AI enhancement';
            }
            
            document.body.classList.remove('offline-mode');
        }
    }
    
    showConnectivityNotification(connectivityInfo) {
        // Don't show notification for initial check
        if (!this.lastCheck) return;
        
        const isOnlineNow = connectivityInfo.overall_status;
        const wasOnline = this.isOnline;
        
        if (isOnlineNow && !wasOnline) {
            this.showNotification('🌐 Back online! AI-enhanced features available.', 'success');
        } else if (!isOnlineNow && wasOnline) {
            this.showNotification('📱 Offline mode activated. Local database active.', 'info');
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `connectivity-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            background: ${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#2563eb'};
            color: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
        `;
        
        // Add close functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOut 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
        
        // Add CSS animations if not exist
        if (!document.getElementById('notification-animations')) {
            const style = document.createElement('style');
            style.id = 'notification-animations';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    // Public API methods
    onStatusChange(callback) {
        this.statusCallbacks.push(callback);
        
        // Return unsubscribe function
        return () => {
            const index = this.statusCallbacks.indexOf(callback);
            if (index > -1) {
                this.statusCallbacks.splice(index, 1);
            }
        };
    }
    
    getCurrentStatus() {
        return {
            isOnline: this.isOnline,
            lastCheck: this.lastCheck,
            backendResponse: this.lastBackendResponse
        };
    }
    
    async forceCheck() {
        return await this.checkConnectivity();
    }
    
    destroy() {
        this.stopMonitoring();
        window.removeEventListener('online', this.handleOnlineStatus);
        window.removeEventListener('offline', this.handleOnlineStatus);
        this.statusCallbacks = [];
    }
}

// Initialize connectivity manager
window.connectivityManager = new ConnectivityManager();