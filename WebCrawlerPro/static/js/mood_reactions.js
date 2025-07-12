// Coffee & Tea Mood Reactions System
class BrewnaraMoodReactions {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.initializeReactionCounts();
    }

    bindEvents() {
        // Handle mood reaction button clicks
        document.addEventListener('click', async (e) => {
            if (e.target.closest('.mood-reaction-btn')) {
                e.preventDefault();
                const button = e.target.closest('.mood-reaction-btn');
                const postId = button.dataset.postId;
                const reactionType = button.dataset.reactionType;
                
                await this.toggleReaction(postId, reactionType, button);
            }
        });
    }

    async toggleReaction(postId, reactionType, button) {
        try {
            // Add loading state
            button.classList.add('reacting');
            button.disabled = true;

            const response = await fetch(`/api/posts/${postId}/react`, {
                method: 'POST',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    reaction_type: reactionType
                })
            });

            if (response.ok) {
                const data = await response.json();
                this.updateReactionButton(button, data);
                this.showReactionFeedback(button, data.is_reacted);
            } else {
                console.error('Failed to toggle reaction:', response.statusText);
                this.showErrorFeedback(button);
            }
        } catch (error) {
            console.error('Error toggling reaction:', error);
            this.showErrorFeedback(button);
        } finally {
            // Remove loading state
            button.classList.remove('reacting');
            button.disabled = false;
        }
    }

    updateReactionButton(button, data) {
        const countSpan = button.querySelector('.reaction-count');
        if (countSpan) {
            countSpan.textContent = data.count;
        }

        // Update visual state
        if (data.is_reacted) {
            button.classList.add('reacted');
        } else {
            button.classList.remove('reacted');
        }
    }

    showReactionFeedback(button, isReacted) {
        // Add a brief animation to show the reaction was registered
        const emoji = button.querySelector('.reaction-emoji');
        if (emoji) {
            emoji.style.transform = 'scale(1.3)';
            emoji.style.transition = 'transform 0.2s ease';
            
            setTimeout(() => {
                emoji.style.transform = 'scale(1)';
            }, 200);
        }

        // Show brief feedback
        if (isReacted) {
            this.createFloatingEmoji(button);
        }
    }

    createFloatingEmoji(button) {
        const emoji = button.querySelector('.reaction-emoji').textContent;
        const floatingEmoji = document.createElement('div');
        floatingEmoji.textContent = emoji;
        floatingEmoji.className = 'floating-emoji';
        
        const rect = button.getBoundingClientRect();
        floatingEmoji.style.position = 'fixed';
        floatingEmoji.style.left = rect.left + rect.width / 2 + 'px';
        floatingEmoji.style.top = rect.top + 'px';
        floatingEmoji.style.pointerEvents = 'none';
        floatingEmoji.style.fontSize = '1.5rem';
        floatingEmoji.style.zIndex = '9999';
        floatingEmoji.style.animation = 'floatUp 1s ease-out forwards';
        
        document.body.appendChild(floatingEmoji);
        
        setTimeout(() => {
            floatingEmoji.remove();
        }, 1000);
    }

    showErrorFeedback(button) {
        button.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => {
            button.style.animation = '';
        }, 500);
    }

    initializeReactionCounts() {
        // Initialize any reaction counts that need to be loaded dynamically
        const reactionContainers = document.querySelectorAll('.mood-reactions');
        reactionContainers.forEach(container => {
            const postId = container.dataset.postId;
            if (postId) {
                this.loadReactionCounts(postId, container);
            }
        });
    }

    async loadReactionCounts(postId, container) {
        try {
            const response = await fetch(`/api/posts/${postId}/reactions`, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateAllReactionCounts(container, data.reactions);
            }
        } catch (error) {
            console.error('Error loading reaction counts:', error);
        }
    }

    updateAllReactionCounts(container, reactions) {
        Object.entries(reactions).forEach(([reactionType, data]) => {
            const button = container.querySelector(`[data-reaction-type="${reactionType}"]`);
            if (button) {
                const countSpan = button.querySelector('.reaction-count');
                if (countSpan) {
                    countSpan.textContent = data.count;
                }
                
                if (data.user_reacted) {
                    button.classList.add('reacted');
                }
            }
        });
    }
}

// CSS for animations
const reactionStyles = `
.mood-reaction-btn {
    border: 1px solid #dee2e6;
    background: white;
    border-radius: 20px;
    padding: 5px 12px;
    font-size: 0.875rem;
    transition: all 0.2s ease;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.mood-reaction-btn:hover {
    background: #f8f9fa;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.mood-reaction-btn.reacted {
    background: linear-gradient(135deg, #8B4513, #D2691E);
    color: white;
    border-color: #8B4513;
}

.mood-reaction-btn.reacting {
    opacity: 0.7;
    transform: scale(0.95);
}

.reaction-emoji {
    font-size: 1.1rem;
}

.reaction-count {
    font-size: 0.75rem;
    font-weight: 600;
}

@keyframes floatUp {
    0% {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
    100% {
        opacity: 0;
        transform: translateY(-50px) scale(1.5);
    }
}

@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
}

.mood-reactions {
    padding: 10px 15px;
    border-top: 1px solid #eee;
}
`;

// Add styles to document
const styleSheet = document.createElement('style');
styleSheet.textContent = reactionStyles;
document.head.appendChild(styleSheet);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    if (!window.brewnaraMoodReactions) {
        window.brewnaraMoodReactions = new BrewnaraMoodReactions();
    }
});