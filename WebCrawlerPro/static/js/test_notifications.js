// Simple notification test system
document.addEventListener('DOMContentLoaded', function() {
    console.log('Testing notification system...');
    
    // Test notification creation
    async function createTestNotification() {
        try {
            const response = await fetch('/api/test/create-notification', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('Test notification created:', data);
                
                // Refresh the page to show the notification
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                console.error('Failed to create test notification:', response.status);
            }
        } catch (error) {
            console.error('Error creating test notification:', error);
        }
    }
    
    // Add test button to create notifications
    const testButton = document.createElement('button');
    testButton.textContent = 'Test Notifications';
    testButton.className = 'btn btn-sm btn-outline-primary position-fixed';
    testButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999;';
    testButton.onclick = createTestNotification;
    
    document.body.appendChild(testButton);
    
    // Check notifications count periodically
    function checkNotificationsBadge() {
        fetch('/notifications/count', {
            method: 'GET',
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const badge = document.getElementById('notification-count');
            const badgeContainer = document.getElementById('notification-badge');
            
            if (badge && data.count > 0) {
                badge.textContent = data.count;
                badgeContainer.style.display = 'inline';
                console.log(`Found ${data.count} notifications`);
            } else if (badgeContainer) {
                badgeContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.log('Could not check notification count:', error);
        });
    }
    
    // Check every 20 seconds (reduced frequency)
    setInterval(checkNotificationsBadge, 20000);
    checkNotificationsBadge(); // Check immediately
});