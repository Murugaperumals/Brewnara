// Real-time notifications and messaging system
class NotificationManager {
    constructor() {
        this.notificationSound = new Audio('/static/sounds/notification.mp3');
        this.messageSound = new Audio('/static/sounds/message.mp3');
        this.lastNotificationCheck = Date.now();
        this.unreadCount = 0;
        this.init();
    }

    init() {
        this.startPolling();
        this.bindEvents();
        this.updateNotificationBadge();
    }

    // Start polling for new notifications every 15 seconds (reduced frequency)
    startPolling() {
        // Initial check after 3 seconds
        setTimeout(() => {
            this.checkForNewNotifications();
            this.checkForNewMessages();
        }, 3000);
        
        // Then check every 15 seconds
        setInterval(() => {
            this.checkForNewNotifications();
            this.checkForNewMessages();
        }, 15000);
    }

    bindEvents() {
        // Mark notification as read when clicked
        document.addEventListener('click', (e) => {
            if (e.target.closest('.notification-item')) {
                const notificationId = e.target.closest('.notification-item').dataset.notificationId;
                this.markNotificationAsRead(notificationId);
            }
        });

        // Show notification dropdown
        const notificationBell = document.getElementById('notification-bell');
        if (notificationBell) {
            notificationBell.addEventListener('click', () => {
                this.toggleNotificationDropdown();
            });
        }
    }

    async checkForNewNotifications() {
        try {
            const response = await fetch('/api/check-notifications', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.unread_count > 0) {
                    this.updateNotificationBadge(data.unread_count);
                }
            } else if (response.status === 401) {
                // User not authenticated, stop polling
                console.warn('User not authenticated for notifications');
                return;
            }
        } catch (error) {
            console.error('Error checking notifications:', error);
        }
    }

    async checkForNewMessages() {
        try {
            const response = await fetch('/api/check-messages', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.unread_count > 0) {
                    this.updateMessageBadge(data.unread_count);
                }
            }
        } catch (error) {
            console.error('Error checking messages:', error);
        }
    }

    handleNewNotifications(notifications) {
        notifications.forEach(notification => {
            this.showNotificationToast(notification);
            this.playNotificationSound();
        });
    }

    handleNewMessages(messages) {
        messages.forEach(message => {
            this.showMessageToast(message);
            this.playMessageSound();
        });
    }

    showNotificationToast(notification) {
        const toast = this.createToast({
            type: 'notification',
            icon: notification.icon || 'fas fa-bell',
            title: notification.title,
            message: notification.message,
            color: notification.color || 'primary',
            action_url: notification.action_url
        });
        this.showToast(toast);
    }

    showMessageToast(message) {
        const toast = this.createToast({
            type: 'message',
            icon: 'fas fa-envelope',
            title: `New message from ${message.sender_name}`,
            message: message.content.substring(0, 100) + (message.content.length > 100 ? '...' : ''),
            color: 'info',
            action_url: `/messages/conversation/${message.sender_id}`
        });
        this.showToast(toast);
    }

    createToast({ type, icon, title, message, color, action_url }) {
        const toastId = 'toast-' + Date.now();
        const toast = document.createElement('div');
        toast.className = `toast notification-toast ${type}-toast`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="toast-header bg-${color} text-white">
                <i class="${icon} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
                ${action_url ? `<br><a href="${action_url}" class="btn btn-sm btn-${color} mt-2">View</a>` : ''}
            </div>
        `;
        return toast;
    }

    showToast(toast) {
        // Create toast container if it doesn't exist
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        container.appendChild(toast);

        // Initialize Bootstrap toast
        const bsToast = new bootstrap.Toast(toast, {
            delay: 5000,
            autohide: true
        });
        
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });

        // Add click handler for action
        const actionLink = toast.querySelector('a[href]');
        if (actionLink) {
            actionLink.addEventListener('click', () => {
                bsToast.hide();
            });
        }
    }

    async markNotificationAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
                if (notificationElement) {
                    notificationElement.classList.remove('unread');
                    notificationElement.classList.add('read');
                }
                this.updateNotificationBadge();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    updateNotificationBadge(count = null) {
        if (count !== null) {
            this.unreadCount = count;
        }
        
        const badge = document.getElementById('notification-badge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    toggleNotificationDropdown() {
        // Load recent notifications
        this.loadNotificationDropdown();
    }

    async loadNotificationDropdown() {
        try {
            const response = await fetch('/api/notifications/recent', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateNotificationDropdown(data.notifications);
            }
        } catch (error) {
            console.error('Error loading notifications:', error);
        }
    }

    updateNotificationDropdown(notifications) {
        const dropdown = document.getElementById('notification-dropdown');
        if (!dropdown) return;

        const notificationsList = dropdown.querySelector('.notifications-list');
        if (!notificationsList) return;

        if (notifications.length === 0) {
            notificationsList.innerHTML = `
                <div class="text-center py-3 text-muted">
                    <i class="fas fa-bell-slash fa-2x mb-2"></i>
                    <p>No notifications yet</p>
                </div>
            `;
            return;
        }

        notificationsList.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.is_read ? 'read' : 'unread'}" 
                 data-notification-id="${notification.id}">
                <div class="d-flex align-items-start">
                    <div class="notification-icon me-3">
                        <i class="${notification.icon} text-${notification.color}"></i>
                    </div>
                    <div class="notification-content flex-grow-1">
                        <h6 class="notification-title mb-1">${notification.title}</h6>
                        <p class="notification-message mb-1 text-muted">${notification.message}</p>
                        <small class="notification-time text-muted">${notification.time_ago}</small>
                    </div>
                    ${!notification.is_read ? '<div class="unread-indicator"></div>' : ''}
                </div>
            </div>
        `).join('');
    }

    playNotificationSound() {
        if (this.notificationSound && typeof this.notificationSound.play === 'function') {
            this.notificationSound.play().catch(e => {
                // Ignore autoplay errors
                console.log('Notification sound autoplay prevented');
            });
        }
    }

    playMessageSound() {
        if (this.messageSound && typeof this.messageSound.play === 'function') {
            this.messageSound.play().catch(e => {
                // Ignore autoplay errors
                console.log('Message sound autoplay prevented');
            });
        }
    }
}

// Coffee mood emoji reactions system
class MoodReactionManager {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // Handle mood reaction clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.mood-reaction-btn')) {
                const btn = e.target.closest('.mood-reaction-btn');
                const postId = btn.dataset.postId;
                const reactionType = btn.dataset.reactionType;
                this.toggleReaction(postId, reactionType, btn);
            }
        });
    }

    async toggleReaction(postId, reactionType, button) {
        try {
            const response = await fetch(`/api/posts/${postId}/react`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    reaction_type: reactionType
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateReactionButton(button, data.is_reacted, data.count);
                this.animateReaction(button);
            }
        } catch (error) {
            console.error('Error toggling reaction:', error);
        }
    }

    updateReactionButton(button, isReacted, count) {
        const countElement = button.querySelector('.reaction-count');
        if (countElement) {
            countElement.textContent = count;
        }
        
        if (isReacted) {
            button.classList.add('reacted');
        } else {
            button.classList.remove('reacted');
        }
    }

    animateReaction(button) {
        // Add bounce animation
        button.classList.add('reaction-animate');
        setTimeout(() => {
            button.classList.remove('reaction-animate');
        }, 300);
    }
}

// Initialize managers when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
    window.moodReactionManager = new MoodReactionManager();
});