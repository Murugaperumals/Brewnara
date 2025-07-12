import os
import secrets
from PIL import Image
from flask import current_app, url_for

def save_picture(form_picture, folder, size=None):
    """Save uploaded picture with a random filename"""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static', folder, picture_fn)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)
    
    if size:
        # Resize image
        img = Image.open(form_picture)
        img.thumbnail(size)
        img.save(picture_path)
    else:
        form_picture.save(picture_path)
    
    return picture_fn

def get_trending_locations():
    """Get trending cafe locations based on recent posts"""
    from models import Post, CafeLocation
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get locations mentioned in posts from the last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trending = Post.query.filter(
        Post.timestamp >= thirty_days_ago,
        Post.location.isnot(None)
    ).with_entities(
        Post.location,
        func.count(Post.location).label('mention_count')
    ).group_by(Post.location).order_by(
        func.count(Post.location).desc()
    ).limit(5).all()
    
    return trending

def create_notification(user_id, notification_type, title, message, related_user_id=None, related_post_id=None, related_cafe_id=None, action_url=None):
    """Create a notification for a user"""
    from models import Notification
    from app import db
    
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        related_user_id=related_user_id,
        related_post_id=related_post_id,
        related_cafe_id=related_cafe_id,
        action_url=action_url
    )
    db.session.add(notification)
    db.session.commit()

def format_timestamp(timestamp):
    """Format timestamp for display"""
    from datetime import datetime, timedelta
    
    now = datetime.utcnow()
    diff = now - timestamp
    
    if diff < timedelta(minutes=1):
        return "just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"{minutes}m ago"
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    elif diff < timedelta(days=7):
        days = diff.days
        return f"{days}d ago"
    else:
        return timestamp.strftime("%b %d, %Y")

def get_mood_emoji(mood):
    """Get emoji for mood"""
    mood_emojis = {
        'relaxed': '😌',
        'energized': '⚡',
        'cozy': '🏠',
        'social': '👥',
        'contemplative': '🤔',
        'happy': '😊',
        'focused': '🎯'
    }
    return mood_emojis.get(mood, '😊')

def get_brew_emoji(brew_type):
    """Get emoji for brew type"""
    brew_emojis = {
        'coffee': '☕',
        'espresso': '☕',
        'latte': '🥛',
        'cappuccino': '☕',
        'americano': '☕',
        'tea': '🍵',
        'green_tea': '🍃',
        'black_tea': '🍵',
        'herbal_tea': '🌿',
        'chai': '🍵',
        'matcha': '🍃',
        'cold_brew': '🧊',
        'iced_coffee': '🧊'
    }
    return brew_emojis.get(brew_type, '☕')
