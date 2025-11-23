/**
 * Main Application Logic for Sahaaya Frontend
 * Handles all user interactions and coordinates with backend
 */

class SahaayaApp {
    constructor() {
        this.currentLanguage = 'en';
        this.userId = this.generateUserId();
        this.consultationHistory = this.loadHistory();
        this.currentResponse = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.loadUserPreferences();
        this.initializeTranslations();
        
        // Listen for connectivity changes
        if (window.connectivityManager) {
            window.connectivityManager.onStatusChange((status) => {
                this.handleConnectivityChange(status);
            });
        }
        
        console.log('Sahaaya App initialized');
    }
    
    setupEventListeners() {
        // Language selection
        const languageSelect = document.getElementById('language-select');
        if (languageSelect) {
            languageSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
        
        // Input method switching
        const voiceBtn = document.getElementById('voice-input-btn');
        const textBtn = document.getElementById('text-input-btn');
        
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => this.switchToVoiceInput());
        }
        if (textBtn) {
            textBtn.addEventListener('click', () => this.switchToTextInput());
        }
        
        // Voice recording
        const recordBtn = document.getElementById('record-btn');
        if (recordBtn) {
            recordBtn.addEventListener('click', () => this.toggleVoiceRecording());
        }
        
        // Text submission
        const submitBtn = document.getElementById('submit-text-btn');
        const textArea = document.getElementById('health-query');
        
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitTextQuery());
        }
        
        if (textArea) {
            textArea.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    this.submitTextQuery();
                }
            });
        }
        
        // Emergency button
        const emergencyBtn = document.getElementById('emergency-btn');
        if (emergencyBtn) {
            emergencyBtn.addEventListener('click', () => this.showEmergencyModal());
        }
        
        // Response controls
        const speakBtn = document.getElementById('speak-response-btn');
        const saveBtn = document.getElementById('save-response-btn');
        
        if (speakBtn) {
            speakBtn.addEventListener('click', () => this.speakCurrentResponse());
        }
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveCurrentResponse());
        }
        
        // Emergency actions
        const call108Btn = document.getElementById('call-108-btn');
        const callPoliceBtn = document.getElementById('call-police-btn');
        
        if (call108Btn) {
            call108Btn.addEventListener('click', () => this.makeEmergencyCall('108'));
        }
        if (callPoliceBtn) {
            callPoliceBtn.addEventListener('click', () => this.makeEmergencyCall('100'));
        }
        
        // History
        const historyBtn = document.getElementById('show-history-btn');
        if (historyBtn) {
            historyBtn.addEventListener('click', () => this.showHistoryModal());
        }
        
        // Modal controls
        this.setupModalListeners();
        
        // Emergency type selection
        const emergencyTypeBtns = document.querySelectorAll('.emergency-type-btn');
        emergencyTypeBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const emergencyType = e.currentTarget.getAttribute('data-emergency');
                this.handleEmergencyType(emergencyType);
            });
        });
    }
    
    setupModalListeners() {
        // Emergency modal
        const emergencyModal = document.getElementById('emergency-modal');
        const closeEmergencyModal = document.getElementById('close-emergency-modal');
        
        if (closeEmergencyModal) {
            closeEmergencyModal.addEventListener('click', () => {
                emergencyModal.classList.add('hidden');
            });
        }
        
        // History modal
        const historyModal = document.getElementById('history-modal');
        const closeHistoryModal = document.getElementById('close-history-modal');
        
        if (closeHistoryModal) {
            closeHistoryModal.addEventListener('click', () => {
                historyModal.classList.add('hidden');
            });
        }
        
        // Close modals on background click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.add('hidden');
            }
        });
        
        // Close modals on Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal:not(.hidden)');
                if (openModal) {
                    openModal.classList.add('hidden');
                }
            }
        });
    }
    
    changeLanguage(language) {
        this.currentLanguage = language;
        this.saveUserPreferences();
        this.updateTranslations();
        
        // Update voice handler language
        if (window.voiceHandler) {
            window.voiceHandler.currentLanguage = language;
        }
        
        console.log(`Language changed to: ${language}`);
    }
    
    switchToVoiceInput() {
        // Update button states
        const voiceBtn = document.getElementById('voice-input-btn');
        const textBtn = document.getElementById('text-input-btn');
        const voiceSection = document.getElementById('voice-section');
        const textSection = document.getElementById('text-section');
        
        voiceBtn.classList.add('active');
        textBtn.classList.remove('active');
        voiceSection.classList.add('active');
        textSection.classList.remove('active');
    }
    
    switchToTextInput() {
        // Update button states
        const voiceBtn = document.getElementById('voice-input-btn');
        const textBtn = document.getElementById('text-input-btn');
        const voiceSection = document.getElementById('voice-section');
        const textSection = document.getElementById('text-section');
        
        textBtn.classList.add('active');
        voiceBtn.classList.remove('active');
        textSection.classList.add('active');
        voiceSection.classList.remove('active');
    }
    
    toggleVoiceRecording() {
        if (window.voiceHandler) {
            window.voiceHandler.startRecording(this.currentLanguage);
        } else {
            this.showError('Voice input not available. Please use text input.');
            this.switchToTextInput();
        }
    }
    
    async submitTextQuery() {
        const textArea = document.getElementById('health-query');
        const query = textArea.value.trim();
        
        if (!query) {
            this.showError('Please enter your health concern.');
            return;
        }
        
        try {
            this.showLoading();
            
            const response = await this.sendHealthQuery(query);
            
            this.hideLoading();
            this.showResponse(response);
            
            // Clear the text area
            textArea.value = '';
            
            // Save to history
            this.addToHistory(query, response);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to get health guidance. Please try again.');
            console.error('Query error:', error);
        }
    }
    
    async sendHealthQuery(text) {
        const endpoint = 'https://sahaaya-rvuy.onrender.com/smart-process';
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                language: this.currentLanguage,
                user_id: this.userId
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    showLoading() {
        const loading = document.getElementById('loading');
        const responseSection = document.getElementById('response-section');
        
        if (loading) loading.classList.remove('hidden');
        if (responseSection) responseSection.classList.add('hidden');
    }
    
    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.classList.add('hidden');
    }
    
    showResponse(response) {
        this.currentResponse = response;
        
        const responseSection = document.getElementById('response-section');
        const responseContent = document.getElementById('response-content');
        const emergencyActions = document.getElementById('emergency-actions');
        
        if (!responseSection || !responseContent) return;
        
        // Build response HTML
        let html = this.buildResponseHTML(response);
        responseContent.innerHTML = html;
        
        // Show/hide emergency actions
        if (response.emergency_detected || response.severity === 'life_threatening') {
            emergencyActions.classList.remove('hidden');
        } else {
            emergencyActions.classList.add('hidden');
        }
        
        // Apply severity styling
        responseSection.className = 'response-section';
        if (response.severity) {
            responseSection.classList.add(`severity-${response.severity.replace('_', '-')}`);
        }
        
        responseSection.classList.remove('hidden');
        
        // Scroll to response
        responseSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    buildResponseHTML(response) {
        let html = '';
        
        // Main guidance
        if (response.guidance) {
            html += `<div class="guidance-text">${this.formatText(response.guidance)}</div>`;
        }
        
        // Severity indicator
        if (response.severity) {
            const severityText = response.severity.replace('_', ' ').toUpperCase();
            html += `<div class="severity-indicator severity-${response.severity.replace('_', '-')}">${severityText}</div>`;
        }
        
        // Emergency protocols
        if (response.immediate_actions) {
            html += '<div class="immediate-actions">';
            html += '<h4><i class="fas fa-exclamation-triangle"></i> Immediate Actions:</h4>';
            html += '<ul>';
            response.immediate_actions.forEach(action => {
                html += `<li>${action}</li>`;
            });
            html += '</ul></div>';
        }
        
        // Local resources
        if (response.local_resources && response.local_resources.length > 0) {
            html += '<div class="local-resources">';
            html += '<h4><i class="fas fa-map-marker-alt"></i> Nearby Healthcare:</h4>';
            response.local_resources.forEach(resource => {
                html += `
                    <div class="resource-item">
                        <strong>${resource.name}</strong>
                        <div class="resource-details">
                            <span><i class="fas fa-map-pin"></i> ${resource.distance || 'Unknown distance'}</span>
                            ${resource.contact ? `<span><i class="fas fa-phone"></i> ${resource.contact}</span>` : ''}
                            ${resource.estimated_cost ? `<span><i class="fas fa-rupee-sign"></i> ${resource.estimated_cost}</span>` : ''}
                        </div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Follow-up instructions
        if (response.follow_up_needed) {
            html += `
                <div class="follow-up">
                    <h4><i class="fas fa-calendar-check"></i> Follow-up Required</h4>
                    <p>Please consult a healthcare provider for further evaluation.</p>
                </div>
            `;
        }
        
        // Mode indicator
        html += `
            <div class="response-metadata">
                <small>
                    <i class="fas fa-info-circle"></i> 
                    Processed in ${response.processing_mode || 'auto'} mode
                    ${response.internet_required === false ? '(Offline capable)' : ''}
                </small>
            </div>
        `;
        
        return html;
    }
    
    formatText(text) {
        // Simple text formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    speakCurrentResponse() {
        if (this.currentResponse && window.voiceHandler) {
            const textToSpeak = this.extractTextFromResponse(this.currentResponse);
            window.voiceHandler.speakResponse(textToSpeak, this.currentLanguage);
        }
    }
    
    extractTextFromResponse(response) {
        let text = response.guidance || '';
        
        if (response.immediate_actions) {
            text += ' Immediate actions: ' + response.immediate_actions.join('. ');
        }
        
        return text;
    }
    
    saveCurrentResponse() {
        if (this.currentResponse) {
            // Implementation depends on your requirements
            // For now, we'll add to browser storage
            this.addToHistory('Current Query', this.currentResponse);
            this.showNotification('Response saved to history', 'success');
        }
    }
    
    showEmergencyModal() {
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            modal.classList.remove('hidden');
        }
    }
    
    async handleEmergencyType(emergencyType) {
        // Close emergency modal
        const modal = document.getElementById('emergency-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
        
        try {
            this.showLoading();
            
            const response = await fetch('https://sahaaya-rvuy.onrender.com/emergency-protocol', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emergency_type: emergencyType,
                    language: this.currentLanguage
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            this.hideLoading();
            this.showResponse(result.emergency_guidance || result);
            
        } catch (error) {
            this.hideLoading();
            this.showError('Failed to get emergency guidance. Call 108 immediately for medical emergencies.');
            console.error('Emergency protocol error:', error);
        }
    }
    
    makeEmergencyCall(number) {
        if (confirm(`Call emergency number ${number}?`)) {
            window.open(`tel:${number}`, '_self');
        }
    }
    
    showHistoryModal() {
        const modal = document.getElementById('history-modal');
        const historyContent = document.getElementById('history-content');
        
        if (!modal || !historyContent) return;
        
        // Build history HTML
        let html = '';
        
        if (this.consultationHistory.length === 0) {
            html = '<p class="no-history">No consultation history found.</p>';
        } else {
            this.consultationHistory.slice(-10).reverse().forEach((item, index) => {
                html += `
                    <div class="history-item">
                        <div class="history-header">
                            <strong>Query ${this.consultationHistory.length - index}</strong>
                            <small>${new Date(item.timestamp).toLocaleString()}</small>
                        </div>
                        <div class="history-query">${item.query}</div>
                        <div class="history-response">${item.response.guidance || 'No guidance available'}</div>
                    </div>
                `;
            });
        }
        
        historyContent.innerHTML = html;
        modal.classList.remove('hidden');
    }
    
    addToHistory(query, response) {
        const historyItem = {
            timestamp: new Date().toISOString(),
            query: query,
            response: response,
            language: this.currentLanguage
        };
        
        this.consultationHistory.push(historyItem);
        
        // Keep only last 50 items
        if (this.consultationHistory.length > 50) {
            this.consultationHistory = this.consultationHistory.slice(-50);
        }
        
        this.saveHistory();
    }
    
    loadHistory() {
        try {
            const history = localStorage.getItem('sahaaya_history');
            return history ? JSON.parse(history) : [];
        } catch (error) {
            console.warn('Failed to load history:', error);
            return [];
        }
    }
    
    saveHistory() {
        try {
            localStorage.setItem('sahaaya_history', JSON.stringify(this.consultationHistory));
        } catch (error) {
            console.warn('Failed to save history:', error);
        }
    }
    
    loadUserPreferences() {
        try {
            const prefs = localStorage.getItem('sahaaya_preferences');
            if (prefs) {
                const preferences = JSON.parse(prefs);
                this.currentLanguage = preferences.language || 'en';
                
                // Update language selector
                const languageSelect = document.getElementById('language-select');
                if (languageSelect) {
                    languageSelect.value = this.currentLanguage;
                }
            }
        } catch (error) {
            console.warn('Failed to load preferences:', error);
        }
    }
    
    saveUserPreferences() {
        try {
            const preferences = {
                language: this.currentLanguage
            };
            localStorage.setItem('sahaaya_preferences', JSON.stringify(preferences));
        } catch (error) {
            console.warn('Failed to save preferences:', error);
        }
    }
    
    generateUserId() {
        let userId = localStorage.getItem('sahaaya_user_id');
        if (!userId) {
            userId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('sahaaya_user_id', userId);
        }
        return userId;
    }
    
    getUserId() {
        return this.userId;
    }
    
    handleConnectivityChange(connectivityInfo) {
        // Handle any app-specific connectivity changes
        console.log('App handling connectivity change:', connectivityInfo);
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type = 'info') {
        // Use the connectivity manager's notification system
        if (window.connectivityManager) {
            window.connectivityManager.showNotification(message, type);
        } else {
            // Fallback
            alert(message);
        }
    }
    
    initializeTranslations() {
        this.updateTranslations();
    }
    
    updateTranslations() {
        // Update all translatable elements
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const translation = this.getTranslation(key);
            
            if (element.tagName.toLowerCase() === 'input' || element.tagName.toLowerCase() === 'textarea') {
                element.placeholder = translation;
            } else {
                element.textContent = translation;
            }
        });
        
        // Update placeholder translations
        const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
        placeholderElements.forEach(element => {
            const key = element.getAttribute('data-translate-placeholder');
            const translation = this.getTranslation(key);
            element.placeholder = translation;
        });
    }
    
    getTranslation(key) {
        // This would typically load from translations.js
        // For now, return the key itself
        return window.translations?.[key]?.[this.currentLanguage] || key;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new SahaayaApp();
});