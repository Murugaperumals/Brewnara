# Brewnara - Coffee & Tea Social Network

A Flask-based social media platform specifically designed for coffee and tea enthusiasts. Connect with fellow beverage lovers, share your brewing experiences, discover new cafes, and build a community around coffee and tea culture.

## Features

### Core Social Features
- **User Profiles**: Customizable profiles with bio, location, and favorite brews
- **Posts & Stories**: Share coffee/tea moments with photos, locations, and mood tags
- **Social Interactions**: Follow friends, like posts, comment, and save favorites
- **Real-time Online Status**: See which friends are currently active
- **Location Integration**: GPS-based location detection and cafe discovery

### Coffee & Tea Specific
- **Brew Type Tagging**: Coffee, espresso, tea, matcha, chai, and more
- **Mood Tracking**: Tag your brewing mood (relaxed, energized, cozy, etc.)
- **Cafe Discovery**: Find and share great coffee shops and tea houses
- **Location Sharing**: Share your favorite brewing spots with the community

### User Experience
- **Premium Design**: Apple-inspired clean interface with SF Pro typography
- **Responsive Layout**: Mobile-first design that works on all devices
- **Interactive Features**: Smooth animations and real-time updates
- **Search & Discovery**: Find users, posts, and locations easily

## Technology Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL (production) / SQLite (development)
- **Authentication**: Flask-Login with secure session management
- **Frontend**: Server-side templates with Bootstrap 5
- **File Handling**: Secure image uploads with PIL processing
- **APIs**: Browser geolocation, Google Maps, Apple Maps integration

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/brewnara.git
   cd brewnara
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="postgresql://username:password@localhost/brewnara"
   ```

5. **Initialize database**
   ```bash
   python main.py
   ```

6. **Run the application**
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reload main:app
   ```

## Project Structure

```
brewnara/
├── app.py              # Flask application factory
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # Application routes
├── forms.py            # WTForms for user input
├── utils.py            # Utility functions
├── static/
│   ├── css/           # Custom stylesheets
│   ├── js/            # JavaScript functionality
│   ├── images/        # Static images and SVGs
│   └── uploads/       # User uploaded content
└── templates/         # Jinja2 templates
```

## Key Features Implementation

### Location Detection
- Uses browser's native geolocation API
- Automatic address resolution with reverse geocoding
- Manual location input with map integration
- Privacy-respecting with user permission prompts

### Real-time Online Status
- Tracks user activity with last_seen timestamps
- Shows friends active in the last 5 minutes
- Live updates without page refresh
- Green indicators for online status

### Image Handling
- Secure file uploads with type validation
- Automatic image resizing and optimization
- Default SVG avatars and placeholders
- Error handling for failed uploads

### Social Features
- Follow/unfollow system with notifications
- Like and comment functionality
- Save posts for later viewing
- User feed with followed content

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## Deployment

The application is configured for deployment on platforms like:
- Heroku
- Railway
- DigitalOcean App Platform
- AWS Elastic Beanstalk

Set the `DATABASE_URL` and `SESSION_SECRET` environment variables in your deployment platform.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the global coffee and tea community
- Built with Flask and modern web technologies
- Premium design influenced by Apple's design principles