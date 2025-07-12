from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from wtforms import ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class PostForm(FlaskForm):
    content = TextAreaField('Share your coffee or tea moment...', validators=[
        DataRequired(), 
        Length(max=2000, message="Post content cannot exceed 2000 characters")
    ])
    image = FileField('Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    location = StringField('Location', validators=[Optional(), Length(max=200)])
    mood = SelectField('Mood', choices=[
        ('', 'Select a mood'),
        ('relaxed', '😌 Relaxed'),
        ('energized', '⚡ Energized'),
        ('cozy', '🏠 Cozy'),
        ('social', '👥 Social'),
        ('contemplative', '🤔 Contemplative'),
        ('happy', '😊 Happy'),
        ('focused', '🎯 Focused')
    ], validators=[Optional()])
    brew_type = SelectField('Brew Type', choices=[
        ('', 'Select brew type'),
        ('coffee', '☕ Coffee'),
        ('espresso', '☕ Espresso'),
        ('latte', '🥛 Latte'),
        ('cappuccino', '☕ Cappuccino'),
        ('americano', '☕ Americano'),
        ('tea', '🍵 Tea'),
        ('green_tea', '🍃 Green Tea'),
        ('black_tea', '🍵 Black Tea'),
        ('herbal_tea', '🌿 Herbal Tea'),
        ('chai', '🍵 Chai'),
        ('matcha', '🍃 Matcha'),
        ('cold_brew', '🧊 Cold Brew'),
        ('iced_coffee', '🧊 Iced Coffee')
    ], validators=[Optional()])
    submit = SubmitField('Share')

class CommentForm(FlaskForm):
    content = TextAreaField('Add a comment...', validators=[
        DataRequired(), 
        Length(max=500, message="Comment cannot exceed 500 characters")
    ])
    submit = SubmitField('Comment')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    bio = TextAreaField('Bio', validators=[Length(max=500, message="Bio cannot exceed 500 characters")])
    location = StringField('Location', validators=[Length(max=100)])
    favorite_brew = StringField('Favorite Brew', validators=[Length(max=100)])
    profile_image = FileField('Profile Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')

class SearchForm(FlaskForm):
    query = StringField('Search users, posts, or locations...', validators=[DataRequired()])
    submit = SubmitField('Search')

class CafeReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '★★★★★ Excellent'),
        ('4', '★★★★☆ Very Good'),
        ('3', '★★★☆☆ Good'),
        ('2', '★★☆☆☆ Fair'),
        ('1', '★☆☆☆☆ Poor')
    ], validators=[DataRequired()])
    title = StringField('Review Title', validators=[
        DataRequired(), 
        Length(max=200, message="Title cannot exceed 200 characters")
    ])
    review_text = TextAreaField('Your Review', validators=[
        DataRequired(), 
        Length(max=1000, message="Review cannot exceed 1000 characters")
    ])
    visit_date = DateField('Visit Date', validators=[Optional()])
    image = FileField('Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Submit Review')

class MessageForm(FlaskForm):
    content = TextAreaField('Message', validators=[
        DataRequired(), 
        Length(max=1000, message="Message cannot exceed 1000 characters")
    ])
    submit = SubmitField('Send Message')

class CafeForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired(), Length(max=200)])
    address = StringField('Address', validators=[DataRequired(), Length(max=300)])
    category = SelectField('Category', choices=[
        ('coffee', 'Coffee Shop'),
        ('tea', 'Tea House'),
        ('both', 'Coffee & Tea')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    price_range = SelectField('Price Range', choices=[
        ('$', '$ - Budget Friendly'),
        ('$$', '$$ - Moderate'),
        ('$$$', '$$$ - Upscale'),
        ('$$$$', '$$$$ - Fine Dining')
    ], validators=[Optional()])
    image = FileField('Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Add Cafe')

class EditCafeForm(FlaskForm):
    name = StringField('Cafe Name', validators=[DataRequired(), Length(max=200)])
    address = StringField('Address', validators=[DataRequired(), Length(max=300)])
    category = SelectField('Category', choices=[
        ('coffee', 'Coffee Shop'),
        ('tea', 'Tea House'),
        ('both', 'Coffee & Tea')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    price_range = SelectField('Price Range', choices=[
        ('$', '$ - Budget Friendly'),
        ('$$', '$$ - Moderate'),
        ('$$$', '$$$ - Upscale'),
        ('$$$$', '$$$$ - Fine Dining')
    ], validators=[Optional()])
    image = FileField('Photo', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Update Cafe')