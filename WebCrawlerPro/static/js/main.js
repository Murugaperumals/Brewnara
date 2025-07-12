// Brewnara - Main JavaScript File
// Coffee & Tea Social Network Interactive Features

document.addEventListener('DOMContentLoaded', function() {
    initializeLikeButtons();
    initializeFollowButtons();
    initializeSaveButtons();
    initializeImagePreviews();
    initializeTooltips();
    initializeScrollEffects();
});

// Like/Unlike functionality
function initializeLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.getAttribute('data-post-id');
            const heartIcon = this.querySelector('.fas.fa-heart');
            const likesCount = this.querySelector('.likes-count');
            
            // Disable button temporarily
            this.disabled = true;
            
            // Send AJAX request to toggle like
            fetch(`/posts/${postId}/like`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    heartIcon.classList.add('text-danger');
                    this.classList.add('liked');
                    animateHeart(heartIcon);
                } else {
                    heartIcon.classList.remove('text-danger');
                    this.classList.remove('liked');
                }
                likesCount.textContent = data.likes_count;
                
                // Re-enable button
                this.disabled = false;
            })
            .catch(error => {
                console.error('Error toggling like:', error);
                this.disabled = false;
                showNotification('Error liking post. Please try again.', 'error');
            });
        });
    });
}

// Follow/Unfollow functionality
function initializeFollowButtons() {
    const followButtons = document.querySelectorAll('.follow-btn');
    
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const username = this.getAttribute('data-username');
            const originalText = this.textContent.trim();
            
            // Disable button and show loading
            this.disabled = true;
            this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
            
            // Send AJAX request to toggle follow
            fetch(`/users/${username}/follow`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.following) {
                    this.innerHTML = '<i class="fas fa-check me-2"></i>Following';
                    this.classList.remove('btn-primary');
                    this.classList.add('btn-outline-primary');
                } else {
                    this.innerHTML = '<i class="fas fa-plus me-2"></i>Follow';
                    this.classList.remove('btn-outline-primary');
                    this.classList.add('btn-primary');
                }
                
                // Update followers count if present
                const followersCount = document.querySelector('.followers-count');
                if (followersCount) {
                    followersCount.textContent = data.followers_count;
                }
                
                // Re-enable button
                this.disabled = false;
                
                // Show success message
                const action = data.following ? 'followed' : 'unfollowed';
                showNotification(`Successfully ${action} user!`, 'success');
            })
            .catch(error => {
                console.error('Error toggling follow:', error);
                this.disabled = false;
                this.textContent = originalText;
                showNotification('Error following user. Please try again.', 'error');
            });
        });
    });
}

// Save/Unsave post functionality
function initializeSaveButtons() {
    const saveButtons = document.querySelectorAll('.save-post-btn');
    
    saveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.getAttribute('data-post-id');
            const icon = this.querySelector('i');
            const text = this.textContent.trim();
            
            // Send AJAX request to toggle save
            fetch(`/posts/${postId}/save`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.saved) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    this.innerHTML = '<i class="fas fa-bookmark me-2"></i>Unsave';
                    showNotification('Post saved!', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    this.innerHTML = '<i class="far fa-bookmark me-2"></i>Save';
                    showNotification('Post unsaved!', 'info');
                }
            })
            .catch(error => {
                console.error('Error toggling save:', error);
                showNotification('Error saving post. Please try again.', 'error');
            });
        });
    });
}

// Image preview functionality
function initializeImagePreviews() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImagePreview(e.target.result, input);
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

// Show image preview
function showImagePreview(imageSrc, inputElement) {
    const previewContainer = document.getElementById('imagePreview');
    const previewImg = document.getElementById('previewImg');
    
    if (previewContainer && previewImg) {
        previewImg.src = imageSrc;
        previewContainer.style.display = 'block';
        previewContainer.classList.add('fade-in');
    }
}

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Scroll effects
function initializeScrollEffects() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return; // Exit if navbar not found
    
    window.addEventListener('scroll', function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // Scrolling down
            if (navbar) navbar.style.transform = 'translateY(-100%)';
        } else {
            // Scrolling up
            if (navbar) navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
    });
    
    // Add transition to navbar
    if (navbar) {
        navbar.style.transition = 'transform 0.3s ease-in-out';
    }
}

// Animate heart icon on like
function animateHeart(heartIcon) {
    heartIcon.style.transform = 'scale(1.3)';
    heartIcon.style.transition = 'transform 0.2s ease';
    
    setTimeout(() => {
        heartIcon.style.transform = 'scale(1)';
    }, 200);
}

// Get CSRF token from meta tag or form
function getCSRFToken() {
    const tokenMeta = document.querySelector('meta[name="csrf-token"]');
    if (tokenMeta) {
        return tokenMeta.getAttribute('content');
    }
    
    const tokenInput = document.querySelector('input[name="csrf_token"]');
    if (tokenInput) {
        return tokenInput.value;
    }
    
    return '';
}

// Show notification messages
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add styles for floating notification
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        z-index: 1050;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form validation enhancements
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Please wait...';
                
                // Re-enable button after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 10000);
            }
        });
        
        // Store original button text
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.setAttribute('data-original-text', submitBtn.textContent.trim());
        }
    });
}

// Initialize form validation on page load
document.addEventListener('DOMContentLoaded', enhanceFormValidation);

// Auto-resize textareas
function initializeAutoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    });
}

// Initialize auto-resize on page load
document.addEventListener('DOMContentLoaded', initializeAutoResizeTextareas);

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if supported
if ('IntersectionObserver' in window) {
    document.addEventListener('DOMContentLoaded', initializeLazyLoading);
}

// Search functionality enhancements
function initializeSearchEnhancements() {
    const searchInput = document.querySelector('input[name="q"]');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    // You could add live search suggestions here
                    console.log('Searching for:', query);
                }, 300);
            }
        });
    }
}

// Initialize search enhancements
document.addEventListener('DOMContentLoaded', initializeSearchEnhancements);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals/dropdowns
    if (e.key === 'Escape') {
        // Close any open Bootstrap modals
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const modalInstance = bootstrap.Modal.getInstance(modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        });
        
        // Close any open dropdowns
        const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
        openDropdowns.forEach(dropdown => {
            const toggleBtn = dropdown.previousElementSibling;
            if (toggleBtn) {
                toggleBtn.click();
            }
        });
    }
});

// Performance monitoring
function initializePerformanceMonitoring() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(() => {
                const perf = performance.getEntriesByType('navigation')[0];
                console.log('Page load time:', perf.loadEventEnd - perf.loadEventStart, 'ms');
            }, 0);
        });
    }
}

// Initialize performance monitoring
initializePerformanceMonitoring();

// Image error handling
function initializeImageErrorHandling() {
    // Handle avatar image errors
    const avatarImages = document.querySelectorAll('img[src*="uploads/avatars"]');
    avatarImages.forEach(img => {
        img.onerror = function() {
            this.src = '/static/images/default-avatar.svg';
        };
    });

    // Handle post image errors
    const postImages = document.querySelectorAll('img[src*="uploads/posts"]');
    postImages.forEach(img => {
        img.onerror = function() {
            this.src = '/static/images/post-placeholder.svg';
            this.style.maxHeight = '200px';
        };
    });
}

// Initialize image error handling
document.addEventListener('DOMContentLoaded', initializeImageErrorHandling);

// Comment Edit/Delete functionality
function initializeCommentActions() {
    // Edit comment buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.edit-comment-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.edit-comment-btn');
            const commentId = btn.getAttribute('data-comment-id');
            showEditForm(commentId);
        }
        
        if (e.target.closest('.save-comment-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.save-comment-btn');
            const commentId = btn.getAttribute('data-comment-id');
            saveComment(commentId);
        }
        
        if (e.target.closest('.cancel-edit-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.cancel-edit-btn');
            const commentId = btn.getAttribute('data-comment-id');
            cancelEdit(commentId);
        }
        
        if (e.target.closest('.delete-comment-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.delete-comment-btn');
            const commentId = btn.getAttribute('data-comment-id');
            deleteComment(commentId);
        }
    });
}

function showEditForm(commentId) {
    const contentElement = document.getElementById(`comment-content-${commentId}`);
    const editForm = document.getElementById(`edit-form-${commentId}`);
    
    if (contentElement && editForm) {
        contentElement.style.display = 'none';
        editForm.classList.remove('d-none');
    }
}

function cancelEdit(commentId) {
    const contentElement = document.getElementById(`comment-content-${commentId}`);
    const editForm = document.getElementById(`edit-form-${commentId}`);
    
    if (contentElement && editForm) {
        contentElement.style.display = 'block';
        editForm.classList.add('d-none');
    }
}

function saveComment(commentId) {
    const textarea = document.getElementById(`edit-content-${commentId}`);
    const content = textarea.value.trim();
    
    if (!content) {
        showNotification('Comment cannot be empty', 'error');
        return;
    }
    
    // Show loading state
    const saveBtn = document.querySelector(`[data-comment-id="${commentId}"].save-comment-btn`);
    const originalText = saveBtn.textContent;
    saveBtn.textContent = 'Saving...';
    saveBtn.disabled = true;
    
    fetch(`/posts/comment/${commentId}/edit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ content: content })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the comment content
            const contentElement = document.getElementById(`comment-content-${commentId}`);
            contentElement.textContent = data.content;
            
            // Hide edit form and show content
            cancelEdit(commentId);
            showNotification('Comment updated successfully', 'success');
        } else {
            showNotification(data.error || 'Failed to update comment', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating comment:', error);
        showNotification('Failed to update comment', 'error');
    })
    .finally(() => {
        saveBtn.textContent = originalText;
        saveBtn.disabled = false;
    });
}

function deleteComment(commentId) {
    if (!confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
        return;
    }
    
    fetch(`/posts/comment/${commentId}/delete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the comment from the DOM
            const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`).closest('.comment');
            if (commentElement) {
                commentElement.style.opacity = '0.5';
                setTimeout(() => {
                    commentElement.remove();
                    showNotification('Comment deleted successfully', 'success');
                }, 300);
            }
        } else {
            showNotification(data.error || 'Failed to delete comment', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting comment:', error);
        showNotification('Failed to delete comment', 'error');
    });
}

// Post Delete functionality
function initializePostActions() {
    document.addEventListener('click', function(e) {
        if (e.target.closest('.delete-post-btn')) {
            e.preventDefault();
            const btn = e.target.closest('.delete-post-btn');
            const postId = btn.getAttribute('data-post-id');
            deletePost(postId);
        }
    });
}

function deletePost(postId) {
    if (!confirm('Are you sure you want to delete this post? This action cannot be undone and will also delete all comments and likes.')) {
        return;
    }
    
    fetch(`/posts/delete/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Post deleted successfully', 'success');
            
            // Check if we're on post detail page
            const postDetailCard = document.querySelector('.card .card-header');
            if (postDetailCard && window.location.pathname.includes('/posts/')) {
                // Redirect to feed page after deletion
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            } else {
                // Remove post from feed
                const postElement = document.querySelector(`[data-post-id="${postId}"]`).closest('.post-card');
                if (postElement) {
                    postElement.style.opacity = '0.5';
                    setTimeout(() => {
                        postElement.remove();
                    }, 300);
                }
            }
        } else {
            showNotification(data.error || 'Failed to delete post', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting post:', error);
        showNotification('Failed to delete post', 'error');
    });
}

// Initialize comment actions on page load
document.addEventListener('DOMContentLoaded', initializeCommentActions);
// Real-time notifications
function initializeNotifications() {
    // Only initialize if user is logged in (notification badge exists)
    const badge = document.getElementById('notification-badge');
    if (!badge) return;
    
    // Check for notification count on page load
    updateNotificationCount();
    
    // Update notification count every 30 seconds
    setInterval(updateNotificationCount, 30000);
}

function updateNotificationCount() {
    // Only check notifications if user is logged in (badge exists)
    const badge = document.getElementById('notification-badge');
    if (!badge) return;
    
    fetch('/notifications/notifications/count')
        .then(response => {
            if (response.ok) {
                return response.json();
            } else if (response.status === 302) {
                // User not logged in, hide badge
                badge.style.display = 'none';
                return null;
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            if (data !== null) {
                const count = document.getElementById('notification-count');
                
                if (data.count > 0) {
                    badge.style.display = 'block';
                    count.textContent = data.count;
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(error => {
            // Silently fail for unauthenticated users
            console.log('Notification check skipped - user not authenticated');
        });
}

// Password visibility toggle functions
function initializePasswordToggles() {
    // Login password toggle
    const loginToggle = document.getElementById('toggleLoginPassword');
    const loginPassword = document.getElementById('loginPassword');
    const loginIcon = document.getElementById('loginPasswordIcon');
    
    if (loginToggle && loginPassword && loginIcon) {
        loginToggle.addEventListener('click', function() {
            const type = loginPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            loginPassword.setAttribute('type', type);
            loginIcon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        });
    }
    
    // Register password toggle
    const registerToggle = document.getElementById('toggleRegisterPassword');
    const registerPassword = document.getElementById('registerPassword');
    const registerIcon = document.getElementById('registerPasswordIcon');
    
    if (registerToggle && registerPassword && registerIcon) {
        registerToggle.addEventListener('click', function() {
            const type = registerPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            registerPassword.setAttribute('type', type);
            registerIcon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        });
    }
    
    // Register confirm password toggle
    const registerToggle2 = document.getElementById('toggleRegisterPassword2');
    const registerPassword2 = document.getElementById('registerPassword2');
    const registerIcon2 = document.getElementById('registerPassword2Icon');
    
    if (registerToggle2 && registerPassword2 && registerIcon2) {
        registerToggle2.addEventListener('click', function() {
            const type = registerPassword2.getAttribute('type') === 'password' ? 'text' : 'password';
            registerPassword2.setAttribute('type', type);
            registerIcon2.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
        });
    }
}

// Initialize post actions on page load
document.addEventListener('DOMContentLoaded', initializePostActions);
// Initialize notifications on page load
document.addEventListener('DOMContentLoaded', initializeNotifications);
// Initialize password toggles on page load
document.addEventListener('DOMContentLoaded', initializePasswordToggles);
// Initialize image error handling on page load
document.addEventListener('DOMContentLoaded', initializeGlobalImageHandling);

// Image error handling
function handleImageError(img) {
    img.src = '/static/images/default-avatar.svg';
}

// Initialize image error handling for all profile images
function initializeGlobalImageHandling() {
    document.querySelectorAll('img[src*="uploads/avatars"], img[src*="uploads/posts"]').forEach(img => {
        img.onerror = function() {
            this.src = '/static/images/default-avatar.svg';
            this.classList.add('image-error');
        };
        
        // Add loading class initially
        img.classList.add('image-loading');
        
        // Remove loading class when image loads
        img.onload = function() {
            this.classList.remove('image-loading');
        };
    });
}

// Export functions for external use
window.Brewnara = {
    showNotification,
    animateHeart,
    getCSRFToken,
    initializeImageErrorHandling,
    initializeCommentActions,
    handleImageError
};
