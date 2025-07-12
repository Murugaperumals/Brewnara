// Coffee Journey Achievement System
class AchievementManager {
    constructor() {
        this.init();
    }

    init() {
        this.showAchievementToasts();
        this.updateProgressBars();
    }

    showAchievementToasts() {
        // Show floating achievement notifications when earned
        this.checkForNewAchievements();
    }

    async checkForNewAchievements() {
        try {
            const response = await fetch('/api/achievements/check', {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.new_achievements && data.new_achievements.length > 0) {
                    data.new_achievements.forEach(achievement => {
                        this.showAchievementToast(achievement);
                    });
                }
            }
        } catch (error) {
            console.log('Could not check achievements:', error);
        }
    }

    showAchievementToast(achievement) {
        const toast = document.createElement('div');
        toast.className = 'achievement-toast';
        toast.innerHTML = `
            <div class="achievement-content">
                <div class="achievement-icon">
                    <i class="${achievement.icon} fa-2x"></i>
                </div>
                <div class="achievement-text">
                    <h6 class="achievement-title">Achievement Unlocked!</h6>
                    <p class="achievement-description">${achievement.title}</p>
                    <small class="text-muted">${achievement.description}</small>
                </div>
            </div>
        `;

        // Style the toast
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #8B4513, #D2691E);
            color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 9999;
            max-width: 350px;
            animation: slideInRight 0.5s ease;
        `;

        document.body.appendChild(toast);

        // Play achievement sound
        this.playAchievementSound();

        // Remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.5s ease';
            setTimeout(() => toast.remove(), 500);
        }, 5000);
    }

    playAchievementSound() {
        try {
            const audio = new Audio('/static/sounds/achievement.mp3');
            audio.volume = 0.3;
            audio.play().catch(() => {
                // Sound failed to play, ignore silently
            });
        } catch (error) {
            // Audio not available, ignore
        }
    }

    updateProgressBars() {
        // Animate progress bars on page load
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.transition = 'width 1s ease';
                bar.style.width = width;
            }, 500);
        });
    }
}

// Add CSS for achievement toasts
const achievementStyles = `
@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}

.achievement-toast {
    border: 2px solid rgba(255,255,255,0.3);
}

.achievement-content {
    display: flex;
    align-items: center;
    gap: 15px;
}

.achievement-icon {
    flex-shrink: 0;
    color: #FFD700;
}

.achievement-text h6 {
    margin: 0 0 5px 0;
    font-weight: bold;
}

.achievement-text p {
    margin: 0 0 3px 0;
    font-size: 0.9rem;
}

.achievement-text small {
    font-size: 0.75rem;
    opacity: 0.9;
}
`;

// Add achievement styles
const achievementStyleSheet = document.createElement('style');
achievementStyleSheet.textContent = achievementStyles;
document.head.appendChild(achievementStyleSheet);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.achievementManager) {
        window.achievementManager = new AchievementManager();
    }
});