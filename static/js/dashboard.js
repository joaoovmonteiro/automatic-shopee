/**
 * Dashboard JavaScript functionality
 * Shopee Affiliate Marketing System
 */

// Global application state
const App = {
    initialized: false,
    updateInterval: null,
    charts: {},
    
    // Initialize the application
    init() {
        if (this.initialized) return;
        
        this.bindEvents();
        this.startRealTimeUpdates();
        this.initializeTooltips();
        this.checkConnections();
        
        this.initialized = true;
        console.log('Dashboard initialized successfully');
    },
    
    // Bind event handlers
    bindEvents() {
        // Real-time clock update
        this.updateClock();
        setInterval(() => this.updateClock(), 1000);
        
        // Auto-refresh data every 5 minutes
        setInterval(() => this.refreshDashboardData(), 300000);
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshDashboardData();
            }
        });
        
        // Handle network status
        window.addEventListener('online', () => this.showNotification('Conexão restaurada', 'success'));
        window.addEventListener('offline', () => this.showNotification('Sem conexão com a internet', 'warning'));
    },
    
    // Update the real-time clock
    updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('pt-BR');
        const clockElement = document.getElementById('current-time');
        if (clockElement) {
            clockElement.textContent = timeString;
        }
    },
    
    // Start real-time updates for dynamic content
    startRealTimeUpdates() {
        // Update engagement data every 30 seconds
        setInterval(() => {
            this.updateEngagementData();
        }, 30000);
        
        // Update post status every 60 seconds
        setInterval(() => {
            this.updatePostStatus();
        }, 60000);
    },
    
    // Initialize Bootstrap tooltips
    initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    },
    
    // Check system connections
    checkConnections() {
        // Simulate connection check
        setTimeout(() => {
            this.updateConnectionStatus('scheduler', true);
            this.updateConnectionStatus('database', true);
            this.updateConnectionStatus('apis', true);
        }, 1000);
    },
    
    // Update connection status indicators
    updateConnectionStatus(service, isConnected) {
        const indicators = document.querySelectorAll(`[data-service="${service}"]`);
        indicators.forEach(indicator => {
            if (isConnected) {
                indicator.className = 'status-indicator status-active';
                indicator.title = `${service} ativo`;
            } else {
                indicator.className = 'status-indicator status-error';
                indicator.title = `${service} com problemas`;
            }
        });
    },
    
    // Refresh dashboard data
    refreshDashboardData() {
        this.showLoading(true);
        
        // Simulate data refresh
        setTimeout(() => {
            this.updateStatistics();
            this.showLoading(false);
            this.showNotification('Dados atualizados', 'info', 2000);
        }, 1500);
    },
    
    // Update statistics on dashboard
    updateStatistics() {
        // This would typically make AJAX calls to get updated data
        // For now, we'll just add visual feedback
        const statCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-info, .card.bg-warning');
        statCards.forEach(card => {
            card.style.transform = 'scale(1.02)';
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 200);
        });
    },
    
    // Update engagement data
    updateEngagementData() {
        const engagementElements = document.querySelectorAll('[data-engagement]');
        engagementElements.forEach(element => {
            const currentValue = parseInt(element.textContent) || 0;
            const increment = Math.floor(Math.random() * 3); // Random small increment
            if (increment > 0) {
                element.textContent = currentValue + increment;
                element.style.color = 'var(--bs-success)';
                setTimeout(() => {
                    element.style.color = '';
                }, 1000);
            }
        });
    },
    
    // Update post status
    updatePostStatus() {
        const statusBadges = document.querySelectorAll('.badge[data-status="scheduled"]');
        statusBadges.forEach(badge => {
            // Simulate some scheduled posts being posted
            if (Math.random() < 0.1) { // 10% chance
                badge.textContent = 'Posted';
                badge.className = 'badge bg-success';
                badge.dataset.status = 'posted';
            }
        });
    },
    
    // Show loading state
    showLoading(show) {
        const loadingElements = document.querySelectorAll('.loading-overlay');
        loadingElements.forEach(element => {
            element.style.display = show ? 'flex' : 'none';
        });
        
        // Disable buttons during loading
        const buttons = document.querySelectorAll('button:not([data-bs-dismiss])');
        buttons.forEach(button => {
            button.disabled = show;
        });
    },
    
    // Show notification
    showNotification(message, type = 'info', duration = 4000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, duration);
    }
};

// Utility functions
const Utils = {
    // Format currency
    formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(value);
    },
    
    // Format number with thousand separators
    formatNumber(value) {
        return new Intl.NumberFormat('pt-BR').format(value);
    },
    
    // Format date
    formatDate(date) {
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Copy to clipboard
    copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            App.showNotification('Copiado para a área de transferência', 'success', 2000);
        }).catch(() => {
            App.showNotification('Erro ao copiar', 'danger', 2000);
        });
    },
    
    // Validate form data
    validateForm(formElement) {
        const inputs = formElement.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    }
};

// API functions
const API = {
    // Base API configuration
    baseURL: window.location.origin,
    
    // Make API request
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            App.showNotification(`Erro na API: ${error.message}`, 'danger');
            throw error;
        }
    },
    
    // Toggle product status
    async toggleProduct(productId) {
        return this.request(`/api/toggle_product/${productId}`);
    },
    
    // Create immediate post
    async postNow(productId) {
        return this.request(`/api/post_now/${productId}`);
    },
    
    // Get analytics data
    async getAnalytics(days = 7) {
        return this.request(`/api/analytics?days=${days}`);
    }
};

// Chart management
const Charts = {
    // Default chart options
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'bottom'
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    },
    
    // Create or update chart
    createChart(canvasId, type, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        // Destroy existing chart if it exists
        if (App.charts[canvasId]) {
            App.charts[canvasId].destroy();
        }
        
        const chartOptions = { ...this.defaultOptions, ...options };
        
        App.charts[canvasId] = new Chart(ctx, {
            type: type,
            data: data,
            options: chartOptions
        });
        
        return App.charts[canvasId];
    },
    
    // Update chart data
    updateChart(canvasId, newData) {
        const chart = App.charts[canvasId];
        if (chart) {
            chart.data = newData;
            chart.update('active');
        }
    },
    
    // Destroy chart
    destroyChart(canvasId) {
        if (App.charts[canvasId]) {
            App.charts[canvasId].destroy();
            delete App.charts[canvasId];
        }
    }
};

// Event handlers for specific actions
const Handlers = {
    // Handle product toggle
    toggleProduct: Utils.debounce(async (productId) => {
        try {
            const button = event.target.closest('button');
            const originalContent = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            const result = await API.toggleProduct(productId);
            
            if (result.success) {
                App.showNotification('Status do produto atualizado', 'success');
                // Update button appearance
                const icon = button.querySelector('i');
                if (result.is_active) {
                    icon.className = 'fas fa-eye';
                    button.className = button.className.replace('btn-secondary', 'btn-success');
                } else {
                    icon.className = 'fas fa-eye-slash';
                    button.className = button.className.replace('btn-success', 'btn-secondary');
                }
            }
        } catch (error) {
            App.showNotification('Erro ao atualizar produto', 'danger');
        } finally {
            const button = event.target.closest('button');
            button.disabled = false;
            if (!button.innerHTML.includes('spinner')) {
                button.innerHTML = originalContent;
            }
        }
    }, 300),
    
    // Handle immediate post creation
    postNow: Utils.debounce(async (productId) => {
        if (!confirm('Deseja criar posts para este produto em todas as redes sociais ativas?')) {
            return;
        }
        
        try {
            const button = event.target.closest('button');
            const originalContent = button.innerHTML;
            
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Postando...';
            
            const result = await API.postNow(productId);
            
            if (result.success) {
                App.showNotification(result.message, 'success');
            }
        } catch (error) {
            App.showNotification('Erro ao criar posts', 'danger');
        } finally {
            const button = event.target.closest('button');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-share-alt me-1"></i>Postar Agora';
        }
    }, 500),
    
    // Handle form submission with validation
    submitForm: (formId, callback) => {
        const form = document.getElementById(formId);
        if (!form) return;
        
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            if (Utils.validateForm(form)) {
                if (callback) callback(form);
            } else {
                App.showNotification('Por favor, preencha todos os campos obrigatórios', 'warning');
            }
        });
    }
};

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Export for global access
window.App = App;
window.Utils = Utils;
window.API = API;
window.Charts = Charts;
window.Handlers = Handlers;

// Global functions for template usage
function toggleProduct(productId) {
    Handlers.toggleProduct(productId);
}

function postNow(productId) {
    Handlers.postNow(productId);
}

// Service Worker registration for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then((registration) => {
                console.log('ServiceWorker registration successful');
            })
            .catch((error) => {
                console.log('ServiceWorker registration failed');
            });
    });
}
