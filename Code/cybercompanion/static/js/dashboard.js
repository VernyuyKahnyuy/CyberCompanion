// static/js/dashboard.js

// Auto-refresh functionality for dashboard components
document.addEventListener('DOMContentLoaded', function() {
    
    // Update pet mood every 5 minutes (300,000ms)
    setInterval(function() {
        fetch('/pet/update-mood/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.mood) {
                updatePetDisplay(data);
            }
        })
        .catch(error => console.log('Error updating pet mood:', error));
    }, 300000);
    
    // Update recent activity every 2 minutes
    setInterval(function() {
        updateRecentActivity();
    }, 120000);
    
    // Initialize tooltips and interactive elements
    initializeDashboardFeatures();
});

// Update pet display with new mood data
function updatePetDisplay(moodData) {
    const petContainer = document.querySelector('.pet-container');
    if (!petContainer) return;
    
    // Update mood emoji
    const moodEmoji = petContainer.querySelector('.text-4xl');
    if (moodEmoji) {
        const emojiMap = {
            'happy': '😊',
            'excited': '🎉',
            'worried': '😟',
            'sad': '😢',
            'neutral': '😐'
        };
        moodEmoji.textContent = emojiMap[moodData.mood] || '😐';
    }
    
    // Update mood badge
    const moodBadge = petContainer.querySelector('.absolute.-top-2.-right-2');
    if (moodBadge) {
        moodBadge.textContent = moodData.mood_display;
    }
    
    // Update mood message
    const moodMessage = petContainer.querySelector('p[hx-get*="mood_message"]');
    if (moodMessage) {
        moodMessage.textContent = moodData.message;
    }
    
    // Add subtle animation to indicate update
    petContainer.classList.add('animate-pulse');
    setTimeout(() => {
        petContainer.classList.remove('animate-pulse');
    }, 1000);
}

// Update recent activity feed
function updateRecentActivity() {
    fetch('/dashboard/recent-activity/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.text())
    .then(html => {
        const activityContainer = document.querySelector('div[hx-get*="recent_activity"]');
        if (activityContainer) {
            activityContainer.innerHTML = html;
            // Add fade-in animation
            activityContainer.style.opacity = '0';
            activityContainer.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                activityContainer.style.opacity = '1';
            }, 100);
        }
    })
    .catch(error => console.log('Error updating activity:', error));
}

// Get CSRF token for AJAX requests
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Initialize dashboard interactive features
function initializeDashboardFeatures() {
    
    // Animate stat cards on scroll
    observeStatsCards();
    
    // Add click effects to quick action buttons
    addQuickActionEffects();
    
    // Initialize real-time notifications
    initializeNotifications();
    
    // Add keyboard shortcuts
    addKeyboardShortcuts();
}

// Observe stat cards for scroll animations
function observeStatsCards() {
    const statCards = document.querySelectorAll('.stat-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                entry.target.style.opacity = '1';
            }
        });
    }, { threshold: 0.1 });
    
    statCards.forEach(card => {
        card.style.opacity = '0';
        observer.observe(card);
    });
}

// Add interactive effects to quick action buttons
function addQuickActionEffects() {
    const quickActions = document.querySelectorAll('.quick-action-btn');
    
    quickActions.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px) scale(1.02)';
            this.style.boxShadow = '0 8px 25px rgba(0, 0, 0, 0.15)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '';
        });
        
        button.addEventListener('click', function(e) {
            // Add click ripple effect
            const ripple = document.createElement('div');
            ripple.className = 'ripple';
            ripple.style.cssText = `
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple 0.6s linear;
                pointer-events: none;
            `;
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
            ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add ripple animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        .quick-action-btn {
            position: relative;
            overflow: hidden;
        }
    `;
    document.head.appendChild(style);
}

// Initialize real-time notifications for security events
function initializeNotifications() {
    // Check for new security events periodically
    setInterval(function() {
        checkForSecurityNotifications();
    }, 30000); // Check every 30 seconds
}

// Check for new security notifications
function checkForSecurityNotifications() {
    fetch('/security/notifications/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.notifications && data.notifications.length > 0) {
            data.notifications.forEach(notification => {
                showNotification(notification);
            });
        }
    })
    .catch(error => {
        // Silently fail - this is a nice-to-have feature
    });
}

// Show notification to user
function showNotification(notification) {
    const notificationContainer = getOrCreateNotificationContainer();
    
    const notificationElement = document.createElement('div');
    notificationElement.className = `
        notification-item bg-white border-l-4 p-4 mb-3 rounded-lg shadow-lg
        ${notification.type === 'success' ? 'border-green-500' : 
          notification.type === 'warning' ? 'border-yellow-500' : 'border-blue-500'}
        transform translate-x-full transition-transform duration-300
    `;
    
    notificationElement.innerHTML = `
        <div class="flex items-center justify-between">
            <div class="flex items-center">
                <div class="text-2xl mr-3">
                    ${notification.type === 'success' ? '✅' : 
                      notification.type === 'warning' ? '⚠️' : 'ℹ️'}
                </div>
                <div>
                    <p class="font-semibold text-gray-800">${notification.title}</p>
                    <p class="text-sm text-gray-600">${notification.message}</p>
                </div>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" 
                    class="text-gray-400 hover:text-gray-600">
                ✕
            </button>
        </div>
    `;
    
    notificationContainer.appendChild(notificationElement);
    
    // Animate in
    setTimeout(() => {
        notificationElement.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notificationElement.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notificationElement.parentNode) {
                notificationElement.remove();
            }
        }, 300);
    }, 5000);
}

// Get or create notification container
function getOrCreateNotificationContainer() {
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.className = 'fixed top-4 right-4 z-50 w-80';
        document.body.appendChild(container);
    }
    return container;
}

// Add keyboard shortcuts for power users
function addKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only process if not typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        // Alt + P: Go to password check
        if (e.altKey && e.key === 'p') {
            e.preventDefault();
            window.location.href = '/security/password-check/';
        }
        
        // Alt + B: Go to breach check
        if (e.altKey && e.key === 'b') {
            e.preventDefault();
            window.location.href = '/security/breach-check/';
        }
        
        // Alt + T: Go to security tips
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            window.location.href = '/dashboard/security-tips/';
        }
        
        // Alt + D: Go to dashboard home
        if (e.altKey && e.key === 'd') {
            e.preventDefault();
            window.location.href = '/dashboard/';
        }
    });
}

// Utility function to format numbers with animation
function animateNumber(element, targetNumber, duration = 1000) {
    const startNumber = parseInt(element.textContent) || 0;
    const increment = (targetNumber - startNumber) / (duration / 16);
    let currentNumber = startNumber;
    
    const timer = setInterval(() => {
        currentNumber += increment;
        if ((increment > 0 && currentNumber >= targetNumber) || 
            (increment < 0 && currentNumber <= targetNumber)) {
            currentNumber = targetNumber;
            clearInterval(timer);
        }
        element.textContent = Math.floor(currentNumber);
    }, 16);
}

// Handle responsive design for mobile devices
function handleMobileResponsiveness() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Adjust update intervals for mobile to save battery
        clearInterval(window.petMoodInterval);
        clearInterval(window.activityUpdateInterval);
        
        // Update less frequently on mobile
        window.petMoodInterval = setInterval(updatePetMood, 600000); // 10 minutes
        window.activityUpdateInterval = setInterval(updateRecentActivity, 300000); // 5 minutes
    }
}

// Handle window resize
window.addEventListener('resize', handleMobileResponsiveness);

// Initialize mobile responsiveness on load
handleMobileResponsiveness();

// Error handling for AJAX requests
function handleAjaxError(error, context) {
    console.warn(`Dashboard AJAX error in ${context}:`, error);
    
    // Show user-friendly error message for critical failures
    if (context === 'security' || context === 'pet-update') {
        showNotification({
            type: 'warning',
            title: 'Connection Issue',
            message: 'Some features may not be up to date. Please refresh the page.'
        });
    }
}

// Performance monitoring
function monitorPerformance() {
    if ('performance' in window) {
        window.addEventListener('load', () => {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            if (loadTime > 3000) { // More than 3 seconds
                console.warn('Dashboard load time is slow:', loadTime + 'ms');
            }
        });
    }
}

// Initialize performance monitoring
monitorPerformance();
