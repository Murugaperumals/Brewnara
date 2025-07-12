import os
from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_, desc, func, and_
from app import db
from models import User, Post, Comment, Like, Notification, Message, CafeLocation, CafeReview, followers, PostReaction, UserAchievement, NotificationEvent
from forms import RegistrationForm, LoginForm, PostForm, CommentForm, EditProfileForm, SearchForm, MessageForm, CafeForm, CafeReviewForm
from utils import save_picture, create_notification, format_timestamp, get_trending_locations

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
post_bp = Blueprint('posts', __name__)
user_bp = Blueprint('users', __name__)

# Context processor to make commonly used functions available in templates
@main_bp.app_context_processor
def utility_processor():
    return dict(
        format_timestamp=format_timestamp,
        len=len
    )

# Before request handler to update user's last seen timestamp
@main_bp.before_app_request
def update_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Main routes
@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    return render_template('index.html')

@main_bp.route('/feed')
@login_required
def feed():
    page = request.args.get('page', 1, type=int)
    posts = current_user.get_feed_posts().paginate(
        page=page, per_page=10, error_out=False)
    
    # Get trending locations
    trending_locations = get_trending_locations()
    
    # Get suggested users (users not followed by current user)
    suggested_users = User.query.filter(
        User.id != current_user.id,
        ~User.followers.any(id=current_user.id)
    ).limit(3).all()
    
    # Get online friends
    online_friends = User.query.join(followers, followers.c.followed_id == User.id).filter(
        followers.c.follower_id == current_user.id,
        User.is_online == True
    ).order_by(User.last_seen.desc()).limit(10).all()
    
    return render_template('feed.html', 
                         posts=posts.items,
                         next_url=url_for('main.feed', page=posts.next_num) if posts.has_next else None,
                         prev_url=url_for('main.feed', page=posts.prev_num) if posts.has_prev else None,
                         trending_locations=trending_locations,
                         suggested_users=suggested_users,
                         online_friends=online_friends)

@main_bp.route('/discover')
@login_required
def discover():
    # Get all cafes
    cafes = Cafe.query.all()
    
    # Get friends (users followed by current user)
    friends = current_user.followed.all()
    
    # Get suggested users (users not followed by current user)
    followed_ids = [user.id for user in current_user.followed.all()]
    followed_ids.append(current_user.id)  # Exclude current user too
    
    suggested_users = User.query.filter(~User.id.in_(followed_ids)).limit(6).all()
    
    # Pass Google Maps API key to template
    google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    return render_template('discover.html', 
                         cafes=cafes, 
                         friends=friends,
                         suggested_users=suggested_users,
                         google_maps_api_key=google_maps_api_key)

@main_bp.route('/search')
@login_required
def search():
    form = SearchForm()
    users = []
    posts = []
    locations = []
    
    if request.args.get('q'):
        query = request.args.get('q')
        
        # Search users
        users = User.query.filter(
            or_(
                User.username.contains(query),
                User.first_name.contains(query),
                User.last_name.contains(query)
            )
        ).limit(10).all()
        
        # Search posts
        posts = Post.query.filter(
            Post.content.contains(query)
        ).order_by(Post.timestamp.desc()).limit(20).all()
        
        # Search locations
        locations = Post.query.filter(
            Post.location.contains(query)
        ).with_entities(Post.location).distinct().limit(10).all()
    
    return render_template('search.html', form=form, users=users, 
                         posts=posts, locations=locations, query=request.args.get('q', ''))

# Authentication routes
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Welcome to Brewnara!', 'success')
        login_user(user)
        return redirect(url_for('main.feed'))
    
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.feed'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Try to find user by username or email
        user = User.query.filter(
            or_(User.username == form.username.data, 
                db.func.lower(User.email) == db.func.lower(form.username.data))
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to next page if it exists
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.feed')
            return redirect(next_page)
        
        flash('Invalid username/email or password', 'danger')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# Post routes
@post_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            content=form.content.data,
            location=form.location.data,
            mood=form.mood.data,
            brew_type=form.brew_type.data,
            user_id=current_user.id
        )
        
        # Handle image upload
        if form.image.data:
            picture_file = save_picture(form.image.data, 'uploads/posts', (800, 600))
            post.image_url = picture_file
        
        db.session.add(post)
        db.session.commit()
        
        flash('Your post has been shared!', 'success')
        return redirect(url_for('main.feed'))
    
    return render_template('create_post.html', form=form)

@post_bp.route('/<int:post_id>')
@login_required
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    # Get comments for this post
    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).order_by(Comment.timestamp.asc()).all()
    
    return render_template('post_detail.html', post=post, form=form, comments=comments)

@post_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    
    if like:
        # Unlike the post
        db.session.delete(like)
        liked = False
    else:
        # Like the post
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        liked = True
        
        # Create notification for post author (if not liking own post)
        if post.user_id != current_user.id:
            create_notification(
                user_id=post.user_id,
                notification_type='like',
                title='New Like',
                message=f'{current_user.first_name} liked your post',
                related_user_id=current_user.id,
                related_post_id=post_id
            )
    
    db.session.commit()
    
    return jsonify({
        'liked': liked,
        'likes_count': post.likes_count
    })

@post_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(comment)
        db.session.commit()
        
        # Create notification for post author (if not commenting on own post)
        if post.user_id != current_user.id:
            create_notification(
                user_id=post.user_id,
                notification_type='comment',
                title='New Comment',
                message=f'{current_user.first_name} commented on your post',
                related_user_id=current_user.id,
                related_post_id=post_id
            )
        
        flash('Your comment has been added!', 'success')
    
    return redirect(url_for('posts.detail', post_id=post_id))

@post_bp.route('/<int:post_id>/save', methods=['POST'])
@login_required
def toggle_save(post_id):
    post = Post.query.get_or_404(post_id)
    
    if current_user.has_saved_post(post):
        current_user.unsave_post(post)
        saved = False
    else:
        current_user.save_post(post)
        saved = True
    
    db.session.commit()
    
    return jsonify({
        'saved': saved
    })

# User routes
@user_bp.route('/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    return render_template('profile.html', user=user, posts=posts)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.favorite_brew = form.favorite_brew.data
        
        # Handle profile image upload
        if form.profile_image.data:
            picture_file = save_picture(form.profile_image.data, 'uploads/avatars', (150, 150))
            current_user.profile_image = picture_file
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    
    elif request.method == 'GET':
        # Pre-populate form with current user data
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.favorite_brew.data = current_user.favorite_brew
    
    return render_template('edit_profile.html', form=form)

@user_bp.route('/<username>/follow', methods=['POST'])
@login_required
def toggle_follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    if user == current_user:
        return jsonify({'error': 'You cannot follow yourself'}), 400
    
    if current_user.is_following(user):
        current_user.unfollow(user)
        following = False
    else:
        current_user.follow(user)
        following = True
        
        # Create notification
        create_notification(
            user_id=user.id,
            notification_type='follow',
            title='New Follower',
            message=f'{current_user.first_name} started following you',
            related_user_id=current_user.id
        )
    
    db.session.commit()
    
    return jsonify({
        'following': following,
        'followers_count': user.followers_count
    })

@user_bp.route('/saved')
@login_required
def saved_posts():
    page = request.args.get('page', 1, type=int)
    posts = current_user.saved.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    return render_template('saved_posts.html', posts=posts)

@user_bp.route('/online')
@login_required
def online_users():
    # Get users based on their online status
    now = datetime.utcnow()
    
    # Online users (last seen within 5 minutes)
    online_users = User.query.filter(
        User.id != current_user.id,
        User.last_seen >= now - timedelta(minutes=5)
    ).order_by(desc(User.last_seen)).all()
    
    # Idle users (last seen between 5-15 minutes)
    idle_users = User.query.filter(
        User.id != current_user.id,
        User.last_seen >= now - timedelta(minutes=15),
        User.last_seen < now - timedelta(minutes=5)
    ).order_by(desc(User.last_seen)).all()
    
    # Away users (last seen between 15 minutes - 1 hour)
    away_users = User.query.filter(
        User.id != current_user.id,
        User.last_seen >= now - timedelta(hours=1),
        User.last_seen < now - timedelta(minutes=15)
    ).order_by(desc(User.last_seen)).all()
    
    return render_template('users/online_users.html', 
                         online_users=online_users,
                         idle_users=idle_users,
                         away_users=away_users)

@user_bp.route('/online-friends')
@login_required
def online_friends():
    from datetime import datetime, timedelta
    
    # Consider users online if they were active in the last 5 minutes
    online_threshold = datetime.utcnow() - timedelta(minutes=5)
    
    # Get followed users who are online
    online_friends = User.query.join(
        followers, (followers.c.followed_id == User.id)
    ).filter(
        followers.c.follower_id == current_user.id,
        User.last_seen >= online_threshold,
        User.id != current_user.id
    ).order_by(User.last_seen.desc()).limit(10).all()
    
    friends_data = []
    for friend in online_friends:
        friends_data.append({
            'name': friend.full_name,
            'username': friend.username,
            'avatar': f'uploads/avatars/{friend.profile_image}' if friend.profile_image != 'default-avatar.png' else 'images/default-avatar.svg',
            'status': 'Online',
            'last_seen': format_timestamp(friend.last_seen)
        })
    
    return jsonify({'friends': friends_data})

@post_bp.route('/comment/<int:comment_id>/edit', methods=['POST'])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    content = request.json.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Comment cannot be empty'}), 400
    
    if len(content) > 500:
        return jsonify({'error': 'Comment too long'}), 400
    
    comment.content = content
    db.session.commit()
    
    return jsonify({
        'success': True,
        'content': content,
        'timestamp': format_timestamp(comment.timestamp)
    })

@post_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    if comment.author != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'success': True})

@post_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        flash('You can only edit your own posts.', 'error')
        return redirect(url_for('posts.detail', post_id=post_id))
    
    form = PostForm()
    if form.validate_on_submit():
        post.content = form.content.data
        post.location = form.location.data
        post.mood = form.mood.data
        post.brew_type = form.brew_type.data
        
        # Handle image upload
        if form.image.data:
            if post.image_url:
                # Delete old image
                old_image_path = os.path.join(current_app.root_path, 'static/uploads/posts', post.image_url)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            image_filename = save_picture(form.image.data, 'posts', size=(800, 600))
            post.image_url = image_filename
        
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.detail', post_id=post.id))
    
    # Pre-populate form with current data
    form.content.data = post.content
    form.location.data = post.location
    form.mood.data = post.mood
    form.brew_type.data = post.brew_type
    
    return render_template('edit_post.html', form=form, post=post)

@post_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete associated image
    if post.image_url:
        image_path = os.path.join(current_app.root_path, 'static/uploads/posts', post.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'success': True})

# Messaging System Routes
message_bp = Blueprint('messages', __name__)

@message_bp.route('/conversations')
@login_required
def conversations():
    # Get all conversations for the current user
    conversations = db.session.query(Message)\
        .filter(or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id))\
        .order_by(desc(Message.timestamp))\
        .all()
    
    # Group by conversation partner
    conv_dict = {}
    for msg in conversations:
        partner_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        if partner_id not in conv_dict:
            conv_dict[partner_id] = {
                'partner': User.query.get(partner_id),
                'last_message': msg,
                'unread_count': Message.query.filter_by(
                    sender_id=partner_id, 
                    recipient_id=current_user.id, 
                    is_read=False
                ).count()
            }
    
    return render_template('messages/conversations.html', conversations=conv_dict.values())

@message_bp.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    partner = User.query.get_or_404(user_id)
    
    # Mark messages as read
    Message.query.filter_by(
        sender_id=user_id, 
        recipient_id=current_user.id, 
        is_read=False
    ).update({'is_read': True})
    db.session.commit()
    
    # Get conversation messages
    messages = Message.query.filter(
        or_(
            (Message.sender_id == current_user.id) & (Message.recipient_id == user_id),
            (Message.sender_id == user_id) & (Message.recipient_id == current_user.id)
        )
    ).order_by(Message.timestamp).all()
    
    form = MessageForm()
    return render_template('messages/conversation.html', partner=partner, messages=messages, form=form)

@message_bp.route('/send/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    recipient = User.query.get_or_404(user_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=user_id,
            content=form.content.data
        )
        db.session.add(message)
        
        # Create notification
        create_notification(
            user_id=user_id,
            notification_type='message',
            title='New Message',
            message=f'{current_user.full_name} sent you a message',
            related_user_id=current_user.id,
            action_url=url_for('messages.conversation', user_id=current_user.id)
        )
        
        db.session.commit()
        flash('Message sent successfully!', 'success')
    
    return redirect(url_for('messages.conversation', user_id=user_id))

# Cafe and Reviews Routes
cafe_bp = Blueprint('cafes', __name__)

@cafe_bp.route('/cafes')
def cafe_list():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', 'all')
    
    query = CafeLocation.query
    if category != 'all':
        query = query.filter_by(category=category)
    
    cafes = query.order_by(desc(CafeLocation.rating)).paginate(
        page=page, per_page=12, error_out=False
    )
    
    return render_template('cafes/cafe_list.html', cafes=cafes, category=category)

@cafe_bp.route('/api/locations')
@login_required
def api_locations():
    """API endpoint to get cafe locations for map"""
    cafes = CafeLocation.query.all()
    cafes_data = []
    for cafe in cafes:
        cafes_data.append({
            'id': cafe.id,
            'name': cafe.name,
            'address': cafe.address,
            'latitude': cafe.latitude,
            'longitude': cafe.longitude,
            'category': cafe.category,
            'rating': cafe.average_rating(),
            'review_count': cafe.review_count(),
            'price_range': cafe.price_range
        })
    return jsonify({'cafes': cafes_data})

@cafe_bp.route('/cafe/<int:cafe_id>')
def cafe_detail(cafe_id):
    cafe = CafeLocation.query.get_or_404(cafe_id)
    reviews = cafe.reviews.order_by(desc(CafeReview.created_at)).limit(10).all()
    
    # Check if current user has reviewed this cafe
    user_review = None
    if current_user.is_authenticated:
        user_review = CafeReview.query.filter_by(
            user_id=current_user.id, 
            cafe_id=cafe_id
        ).first()
    
    return render_template('cafes/cafe_detail.html', cafe=cafe, reviews=reviews, user_review=user_review)

@cafe_bp.route('/cafe/<int:cafe_id>/review', methods=['GET', 'POST'])
@login_required
def add_review(cafe_id):
    cafe = CafeLocation.query.get_or_404(cafe_id)
    
    # Check if user already reviewed this cafe
    existing_review = CafeReview.query.filter_by(
        user_id=current_user.id, 
        cafe_id=cafe_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this cafe. You can edit your existing review.', 'info')
        return redirect(url_for('cafes.edit_review', review_id=existing_review.id))
    
    form = CafeReviewForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            image_filename = save_picture(form.image.data, 'cafe_reviews', size=(600, 400))
        
        review = CafeReview(
            user_id=current_user.id,
            cafe_id=cafe_id,
            rating=int(form.rating.data),
            title=form.title.data,
            review_text=form.review_text.data,
            visit_date=form.visit_date.data,
            image_url=image_filename
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Your review has been added!', 'success')
        return redirect(url_for('cafes.cafe_detail', cafe_id=cafe_id))
    
    return render_template('cafes/add_review.html', form=form, cafe=cafe)

@cafe_bp.route('/add-cafe', methods=['GET', 'POST'])
@login_required
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            image_filename = save_picture(form.image.data, 'cafes', size=(800, 600))
        
        cafe = CafeLocation(
            name=form.name.data,
            address=form.address.data,
            category=form.category.data,
            description=form.description.data,
            phone=form.phone.data,
            website=form.website.data,
            price_range=form.price_range.data,
            image_url=image_filename,
            user_id=current_user.id
        )
        
        db.session.add(cafe)
        db.session.commit()
        
        flash('Cafe added successfully!', 'success')
        return redirect(url_for('cafes.cafe_detail', cafe_id=cafe.id))
    
    return render_template('cafes/add_cafe.html', form=form)

@cafe_bp.route('/delete/<int:cafe_id>', methods=['POST'])
@login_required
def delete_cafe(cafe_id):
    try:
        cafe = CafeLocation.query.get_or_404(cafe_id)
        
        # Check if current user is the owner
        if cafe.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'You can only delete cafes you created'}), 403
        
        # Delete associated reviews first
        CafeReview.query.filter_by(cafe_id=cafe_id).delete()
        
        # Delete the cafe
        db.session.delete(cafe)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Cafe deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting cafe: {str(e)}'}), 500

@cafe_bp.route('/edit/<int:cafe_id>', methods=['GET', 'POST'])
@login_required
def edit_cafe(cafe_id):
    cafe = CafeLocation.query.get_or_404(cafe_id)
    
    # Check if current user is the owner
    if cafe.user_id != current_user.id:
        flash('You can only edit cafes you created.', 'error')
        return redirect(url_for('cafes.cafe_list'))
    
    form = CafeForm(obj=cafe)
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_filename = save_picture(form.image.data, 'cafes', size=(800, 600))
            cafe.image_url = image_filename
        
        # Update cafe details
        cafe.name = form.name.data
        cafe.address = form.address.data
        cafe.category = form.category.data
        cafe.description = form.description.data
        cafe.phone = form.phone.data
        cafe.website = form.website.data
        cafe.price_range = form.price_range.data
        
        db.session.commit()
        flash('Cafe updated successfully!', 'success')
        return redirect(url_for('cafes.cafe_detail', cafe_id=cafe.id))
    
    return render_template('cafes/edit_cafe.html', form=form, cafe=cafe)

# Notifications Routes
notification_bp = Blueprint('notifications', __name__)

@notification_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(desc(Notification.timestamp)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    return render_template('notifications/notifications.html', notifications=notifications)

@notification_bp.route('/count')
@login_required
def notification_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@notification_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Unauthorized'}), 403

# API Routes for Real-time Notifications
api_bp = Blueprint('api', __name__)

@api_bp.route('/api/notifications/check')
@login_required
def check_notifications():
    """Check for new notifications since last check"""
    try:
        since = request.args.get('since', type=float)
        if since:
            since_datetime = datetime.fromtimestamp(since / 1000)
            new_notifications = Notification.query.filter(
                Notification.user_id == current_user.id,
                Notification.timestamp > since_datetime,
                Notification.is_read == False
            ).order_by(desc(Notification.timestamp)).all()
        else:
            new_notifications = []
        
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        
        return jsonify({
            'new_notifications': [{
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'icon': n.get_icon(),
                'color': n.color,
                'action_url': n.action_url,
                'timestamp': n.timestamp.isoformat()
            } for n in new_notifications],
            'unread_count': unread_count
        })
    except Exception as e:
        return jsonify({'error': str(e), 'unread_count': 0}), 500

@api_bp.route('/api/notifications/recent')
@login_required
def recent_notifications():
    """Get recent notifications for dropdown"""
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        desc(Notification.timestamp)
    ).limit(10).all()
    
    return jsonify({
        'notifications': [{
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'icon': n.get_icon(),
            'color': n.color,
            'action_url': n.action_url,
            'is_read': n.is_read,
            'time_ago': n.get_time_ago()
        } for n in notifications]
    })

@api_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read via API"""
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Unauthorized'}), 403

@api_bp.route('/api/messages/check')
@login_required
def check_messages():
    """Check for new messages since last check"""
    try:
        since = request.args.get('since', type=float)
        if since:
            since_datetime = datetime.fromtimestamp(since / 1000)
            new_messages = Message.query.filter(
                Message.recipient_id == current_user.id,
                Message.timestamp > since_datetime,
                Message.is_read == False
            ).order_by(desc(Message.timestamp)).all()
        else:
            new_messages = []
        
        return jsonify({
            'new_messages': [{
                'id': m.id,
                'content': m.content,
                'sender_id': m.sender_id,
                'sender_name': m.sender.full_name(),
                'timestamp': m.timestamp.isoformat()
            } for m in new_messages]
        })
    except Exception as e:
        return jsonify({'error': str(e), 'new_messages': []}), 500

@api_bp.route('/api/posts/<int:post_id>/react', methods=['POST'])
@login_required
def toggle_post_reaction(post_id):
    """Toggle emoji reaction on a post"""
    post = Post.query.get_or_404(post_id)
    data = request.get_json()
    reaction_type = data.get('reaction_type')
    
    if not reaction_type:
        return jsonify({'error': 'Reaction type required'}), 400
    
    # Check if user already reacted with this type
    existing_reaction = PostReaction.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction
            db.session.delete(existing_reaction)
            db.session.commit()
            is_reacted = False
        else:
            # Update reaction type
            existing_reaction.reaction_type = reaction_type
            existing_reaction.timestamp = datetime.utcnow()
            db.session.commit()
            is_reacted = True
    else:
        # Add new reaction
        reaction = PostReaction(
            user_id=current_user.id,
            post_id=post_id,
            reaction_type=reaction_type
        )
        db.session.add(reaction)
        db.session.commit()
        is_reacted = True
        
        # Create notification for post author
        if post.user_id != current_user.id:
            create_notification(
                user_id=post.user_id,
                notification_type='reaction',
                title=f'{current_user.full_name()} reacted to your post',
                message=f'reacted with {reaction_type} to your post',
                related_user_id=current_user.id,
                related_post_id=post_id,
                action_url=url_for('posts.detail', post_id=post_id),
                icon='fas fa-smile',
                color='warning'
            )
    
    # Get total reaction count for this type
    count = PostReaction.query.filter_by(post_id=post_id, reaction_type=reaction_type).count()
    
    return jsonify({
        'success': True,
        'is_reacted': is_reacted,
        'count': count,
        'reaction_type': reaction_type
    })

# Achievement system
@api_bp.route('/api/achievements/check')
@login_required
def check_achievements():
    """Check for new achievements earned by user"""
    achievements = check_user_achievements(current_user)
    return jsonify({
        'new_achievements': achievements
    })

def check_user_achievements(user):
    """Check and award achievements to user"""
    new_achievements = []
    
    # First Post Achievement
    if user.posts_count == 1 and not UserAchievement.query.filter_by(
        user_id=user.id, achievement_type='first_post'
    ).first():
        achievement = UserAchievement(
            user_id=user.id,
            achievement_type='first_post',
            title='First Brew Shared!',
            description='You shared your first coffee or tea moment',
            icon='fas fa-star',
            badge_color='gold'
        )
        db.session.add(achievement)
        new_achievements.append(achievement)
        
        # Create notification
        create_notification(
            user_id=user.id,
            notification_type='achievement',
            title='Achievement Unlocked!',
            message='You earned the "First Brew Shared" badge',
            icon='fas fa-trophy',
            color='success'
        )
    
    # Social Butterfly Achievement (10 followers)
    if user.followers_count >= 10 and not UserAchievement.query.filter_by(
        user_id=user.id, achievement_type='social_butterfly'
    ).first():
        achievement = UserAchievement(
            user_id=user.id,
            achievement_type='social_butterfly',
            title='Social Butterfly',
            description='You have 10 or more followers',
            icon='fas fa-users',
            badge_color='silver'
        )
        db.session.add(achievement)
        new_achievements.append(achievement)
    
    # Coffee Explorer Achievement (5 cafe reviews)
    if len(user.cafe_reviews) >= 5 and not UserAchievement.query.filter_by(
        user_id=user.id, achievement_type='coffee_explorer'
    ).first():
        achievement = UserAchievement(
            user_id=user.id,
            achievement_type='coffee_explorer',
            title='Coffee Explorer',
            description='You reviewed 5 different cafes',
            icon='fas fa-map-marked-alt',
            badge_color='bronze'
        )
        db.session.add(achievement)
        new_achievements.append(achievement)
    
    if new_achievements:
        db.session.commit()
    
    return [
        {
            'title': a.title,
            'description': a.description,
            'icon': a.icon,
            'badge_color': a.badge_color
        } for a in new_achievements
    ]



@api_bp.route('/api/posts/<int:post_id>/reactions')
@login_required
def get_post_reactions(post_id):
    """Get all reactions for a post"""
    try:
        reactions = db.session.query(
            PostReaction.reaction_type,
            db.func.count(PostReaction.id).label('count')
        ).filter_by(post_id=post_id).group_by(PostReaction.reaction_type).all()
        
        user_reactions = PostReaction.query.filter_by(
            user_id=current_user.id,
            post_id=post_id
        ).all()
        
        user_reaction_types = {r.reaction_type for r in user_reactions}
        
        reaction_data = {}
        for reaction_type, count in reactions:
            reaction_data[reaction_type] = {
                'count': count,
                'user_reacted': reaction_type in user_reaction_types
            }
        
        return jsonify({'reactions': reaction_data})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Test route to create sample notifications
@api_bp.route('/api/test/create-notification')
@login_required
def test_create_notification():
    """Create a test notification for the current user"""
    create_notification(
        user_id=current_user.id,
        notification_type='system',
        title='Welcome to Real-time Notifications!',
        message='Your notification system is working perfectly. Enjoy the enhanced Brewnara experience!',
        icon='fas fa-bell',
        color='success'
    )
    return jsonify({'success': True, 'message': 'Test notification created'})

# Make sure app is registered with all blueprints
def register_blueprints():
    from app import app
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(post_bp, url_prefix='/posts')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(cafe_bp, url_prefix='/cafes')
    app.register_blueprint(notification_bp, url_prefix='/notifications')
    app.register_blueprint(api_bp)

# API Routes for AJAX calls
@main_bp.route('/api/online-friends')
@login_required
def api_online_friends():
    try:
        # Get friends who are online (last seen within 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        online_friends = User.query.join(followers, followers.c.followed_id == User.id).filter(
            followers.c.follower_id == current_user.id,
            User.last_seen >= five_minutes_ago
        ).order_by(User.last_seen.desc()).all()
        
        friends_data = []
        for friend in online_friends:
            friends_data.append({
                'id': friend.id,
                'username': friend.username,
                'full_name': friend.full_name,
                'profile_image_url': friend.profile_image_url or '/static/images/default-avatar.png',
                'last_seen': friend.last_seen.isoformat() if friend.last_seen else None,
                'status': friend.get_online_status()
            })
        
        return jsonify({'friends': friends_data})
    except Exception as e:
        print(f"Error in api_online_friends: {e}")
        return jsonify({'error': str(e), 'friends': []}), 500

@main_bp.route('/api/check-messages')
@login_required  
def api_check_messages():
    try:
        unread_count = Message.query.filter_by(
            recipient_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({'unread_count': unread_count})
    except Exception as e:
        print(f"Error in api_check_messages: {e}")
        return jsonify({'error': str(e), 'unread_count': 0}), 500

@main_bp.route('/api/check-notifications')
@login_required
def api_check_notifications():
    try:
        unread_count = Notification.query.filter_by(
            user_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({'unread_count': unread_count})
    except Exception as e:
        print(f"Error in api_check_notifications: {e}")
        return jsonify({'error': str(e), 'unread_count': 0}), 500

@main_bp.route('/api/friends-locations')
@login_required
def api_friends_locations():
    try:
        # Get friends with location data
        friends = current_user.followed.filter(
            User.latitude.isnot(None),
            User.longitude.isnot(None)
        ).all()
        
        friends_data = []
        for friend in friends:
            friends_data.append({
                'id': friend.id,
                'username': friend.username,
                'full_name': friend.full_name,
                'latitude': float(friend.latitude) if friend.latitude else None,
                'longitude': float(friend.longitude) if friend.longitude else None,
                'profile_image_url': friend.profile_image_url or '/static/images/default-avatar.svg'
            })
        
        return jsonify({'friends': friends_data})
    except Exception as e:
        print(f"Error in api_friends_locations: {e}")
        return jsonify({'error': str(e), 'friends': []}), 500

@main_bp.route('/api/cafes-locations')
@login_required  
def api_cafes_locations():
    try:
        # Get cafes with location data
        cafes = Cafe.query.filter(
            Cafe.latitude.isnot(None),
            Cafe.longitude.isnot(None)
        ).all()
        
        cafes_data = []
        for cafe in cafes:
            # Calculate average rating
            reviews = CafeReview.query.filter_by(cafe_id=cafe.id).all()
            average_rating = sum(int(review.rating) for review in reviews) / len(reviews) if reviews else 0
            
            cafes_data.append({
                'id': cafe.id,
                'name': cafe.name,
                'address': cafe.address,
                'description': cafe.description,
                'latitude': float(cafe.latitude) if cafe.latitude else None,
                'longitude': float(cafe.longitude) if cafe.longitude else None,
                'average_rating': round(average_rating, 1),
                'review_count': len(reviews)
            })
        
        return jsonify({'cafes': cafes_data})
    except Exception as e:
        print(f"Error in api_cafes_locations: {e}")
        return jsonify({'error': str(e), 'cafes': []}), 500
