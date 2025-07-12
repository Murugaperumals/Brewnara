from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association table for followers
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

# Association table for saved posts
saved_posts = db.Table('saved_posts',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200), default='default-avatar.svg')
    location = db.Column(db.String(100))
    favorite_brew = db.Column(db.String(100))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    online_status = db.Column(db.String(20), default='offline')  # online, idle, away, offline
    
    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    # Following system
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    # Saved posts
    saved = db.relationship(
        'Post', secondary=saved_posts,
        backref=db.backref('saved_by', lazy='dynamic'), lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def save_post(self, post):
        if not self.has_saved_post(post):
            self.saved.append(post)
    
    def unsave_post(self, post):
        if self.has_saved_post(post):
            self.saved.remove(post)
    
    def has_saved_post(self, post):
        return self.saved.filter(saved_posts.c.post_id == post.id).count() > 0
    
    def get_feed_posts(self):
        # Get posts from followed users and own posts
        followed_posts = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)
        return followed_posts.union(own_posts).order_by(Post.timestamp.desc())
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def following_count(self):
        return self.followed.count()
    
    @property
    def posts_count(self):
        return self.posts.count()
    
    def is_online(self):
        """Check if user is online (last seen within 5 minutes)"""
        if self.last_seen:
            return (datetime.utcnow() - self.last_seen).total_seconds() < 300  # 5 minutes
        return False
    
    def is_idle(self):
        """Check if user is idle (last seen within 15 minutes but more than 5)"""
        if self.last_seen:
            seconds = (datetime.utcnow() - self.last_seen).total_seconds()
            return 300 <= seconds < 900  # 5-15 minutes
        return False
    
    def is_away(self):
        """Check if user is away (last seen within 1 hour but more than 15 minutes)"""
        if self.last_seen:
            seconds = (datetime.utcnow() - self.last_seen).total_seconds()
            return 900 <= seconds < 3600  # 15 minutes - 1 hour
        return False
    
    def get_status_icon(self):
        """Get status icon based on online presence"""
        if self.is_online():
            return 'fas fa-leaf', '#28a745', 'online'  # Green leaf for online
        elif self.is_idle():
            return 'fas fa-coffee', '#007bff', 'idle'  # Blue coffee cup for idle
        elif self.is_away():
            return 'fas fa-mug-hot', '#8B4513', 'away'  # Brown coffee mug for away
        else:
            return 'fas fa-circle', '#6c757d', 'offline'  # Gray circle for offline

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))
    location = db.Column(db.String(200))
    mood = db.Column(db.String(50))
    brew_type = db.Column(db.String(50))  # coffee, tea, espresso, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('PostReaction', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def likes_count(self):
        return self.likes.count()
    
    @property
    def comments_count(self):
        return self.comments.count()
    
    def is_liked_by(self, user):
        return self.likes.filter_by(user_id=user.id).first() is not None

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    
    # Self-referential relationship for nested comments
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_like'),)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # like, comment, follow, message, cafe_review, system, achievement
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    related_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    related_post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    related_cafe_id = db.Column(db.Integer, db.ForeignKey('cafe_location.id'))
    action_url = db.Column(db.String(500))  # URL to redirect when notification is clicked
    icon = db.Column(db.String(100))  # FontAwesome icon class
    color = db.Column(db.String(20), default='primary')  # Bootstrap color classes
    
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    related_post = db.relationship('Post', foreign_keys=[related_post_id])
    related_cafe = db.relationship('CafeLocation', foreign_keys=[related_cafe_id])
    
    def get_icon(self):
        """Get appropriate icon based on notification type"""
        icons = {
            'like': 'fas fa-heart',
            'comment': 'fas fa-comment',
            'follow': 'fas fa-user-plus',
            'message': 'fas fa-envelope',
            'cafe_review': 'fas fa-star',
            'system': 'fas fa-bell',
            'achievement': 'fas fa-trophy'
        }
        return self.icon or icons.get(self.type, 'fas fa-bell')
    
    def get_time_ago(self):
        """Get human-readable time difference"""
        from utils import format_timestamp
        return format_timestamp(self.timestamp)

class CafeLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    category = db.Column(db.String(50), nullable=False)  # coffee, tea, both
    rating = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    hours = db.Column(db.Text)  # JSON string for operating hours
    price_range = db.Column(db.String(10))  # $, $$, $$$, $$$$
    amenities = db.Column(db.Text)  # JSON string for amenities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Owner of the cafe
    
    # Relationships
    reviews = db.relationship('CafeReview', backref='cafe', lazy='dynamic', cascade='all, delete-orphan')
    
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def review_count(self):
        return self.reviews.count()

class CafeReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cafe_id = db.Column(db.Integer, db.ForeignKey('cafe_location.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    visit_date = db.Column(db.Date)
    image_url = db.Column(db.String(200))
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='cafe_reviews')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'cafe_id', name='unique_user_cafe_review'),)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, emoji, image, system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_deleted_by_sender = db.Column(db.Boolean, default=False)
    is_deleted_by_recipient = db.Column(db.Boolean, default=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('message.id'))  # For threaded conversations
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    reply_to = db.relationship('Message', remote_side=[id], backref='replies')
    
    def get_time_ago(self):
        """Get human-readable time difference"""
        from utils import format_timestamp
        return format_timestamp(self.timestamp)
    
    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            self.is_read = True
            db.session.commit()

# Coffee mood reactions for posts
class PostReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    reaction_type = db.Column(db.String(20), nullable=False)  # coffee_love, tea_love, energized, relaxed, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reactions')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='unique_user_post_reaction'),)

# User achievements/badges system
class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_type = db.Column(db.String(50), nullable=False)  # first_post, coffee_explorer, social_butterfly, etc.
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    icon = db.Column(db.String(100))  # FontAwesome icon or emoji
    badge_color = db.Column(db.String(20), default='gold')  # gold, silver, bronze, special
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_featured = db.Column(db.Boolean, default=False)  # Show on profile prominently
    
    user = db.relationship('User', backref='achievements')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_type', name='unique_user_achievement'),)

# Real-time notification events table
class NotificationEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # new_message, new_notification, user_online, etc.
    event_data = db.Column(db.Text)  # JSON data for the event
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='notification_events')


