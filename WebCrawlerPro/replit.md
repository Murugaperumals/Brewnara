# Brewnara - Coffee & Tea Social Network

## Overview

Brewnara is a Flask-based social media platform specifically designed for coffee and tea enthusiasts. It allows users to share their brewing experiences, discover new cafes, connect with fellow beverage lovers, and build a community around coffee and tea culture. The application features user profiles, posts with images, social interactions (likes, comments, follows), and location-based discovery.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a traditional Flask web application architecture with a Model-View-Controller (MVC) pattern:

**Backend Framework**: Flask with SQLAlchemy ORM
**Database**: SQLite (development) with support for PostgreSQL (production via DATABASE_URL)
**Authentication**: Flask-Login with session-based authentication
**Frontend**: Server-side rendered templates using Jinja2, Bootstrap 5 for styling
**File Handling**: Local file storage for user uploads (avatars and post images)

## Key Components

### Authentication System
- **User Registration/Login**: Custom forms with validation using WTForms
- **Session Management**: Flask-Login handles user sessions
- **Password Security**: Werkzeug for password hashing

### Database Models
- **User Model**: Stores user profiles, authentication data, and relationships
- **Post Model**: Handles user posts with content, images, and metadata
- **Social Features**: Following system, likes, comments, and saved posts through association tables
- **Location Integration**: Posts can be tagged with cafe/location information

### File Upload System
- **Image Processing**: PIL (Pillow) for image resizing and optimization
- **Secure Uploads**: File type validation and secure filename generation
- **Storage Structure**: Organized in static/uploads with separate folders for avatars and posts

### Frontend Architecture
- **Template System**: Jinja2 templates with inheritance (base.html)
- **Responsive Design**: Bootstrap 5 for mobile-first responsive layout
- **Interactive Features**: JavaScript for AJAX interactions (likes, follows, saves)
- **Custom Styling**: CSS variables for consistent coffee/tea theme

## Data Flow

1. **User Registration**: Form validation → Password hashing → Database storage
2. **Post Creation**: Content validation → Image processing → Database storage → Feed distribution
3. **Social Interactions**: AJAX requests → Database updates → Real-time UI updates
4. **Feed Generation**: Follow relationships → Post aggregation → Pagination → Template rendering

## External Dependencies

### Core Flask Extensions
- **Flask-SQLAlchemy**: Database ORM and migrations
- **Flask-Login**: User session management
- **Flask-WTF**: Form handling and CSRF protection

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements
- **Custom JavaScript**: AJAX functionality for social interactions

### Image Processing
- **Pillow (PIL)**: Image resizing and optimization
- **Werkzeug**: Secure file handling utilities

### Deployment
- **ProxyFix**: Handles reverse proxy headers for production deployment
- **Environment Variables**: Configuration management for secrets and database URLs

## Deployment Strategy

The application is configured for flexible deployment:

**Development**: SQLite database with debug mode enabled
**Production**: Environment-based configuration with PostgreSQL support
**File Storage**: Local storage with organized directory structure
**Security**: CSRF protection, secure sessions, and input validation
**Scalability**: Database connection pooling and configurable upload limits

The application uses environment variables for configuration management, making it suitable for deployment on platforms like Heroku, Railway, or similar PaaS providers. The database schema is automatically created on first run, and the application includes proper error handling and logging.

## Recent Changes

- **Interactive Map Multiple Provider Support (July 12, 2025)**: Implemented comprehensive map provider switching
  - Added support for Google Maps, OpenStreetMap, Mapbox, and Apple Maps style
  - Created seamless provider switching with dropdown menu in map header
  - Implemented unified marker management across all map providers
  - Added provider-specific marker rendering and interaction handling
  - Enhanced user experience with consistent functionality across all providers
  - Integrated real geolocation with Google Places API for authentic data
  - Added toggle functionality for friends and cafes that works across all providers

- **Map Reliability Enhancement (July 12, 2025)**: Upgraded from OpenStreetMap to multi-provider support
  - Fixed persistent map loading issues by implementing Google Maps as primary provider
  - Added fallback mechanisms for different mapping services
  - Implemented consistent "Get Directions" functionality across all providers
  - Enhanced marker icons with SVG-based custom designs for better visibility
  - Added provider-specific optimizations for performance and user experience

- **Online Status System (July 11, 2025)**: Implemented comprehensive online presence tracking
  - Added coffee-themed status indicators: green leaf (online), blue coffee cup (idle), brown coffee mug (away)
  - Integrated status display across chat conversations, message lists, and user profiles
  - Created animated status indicators with pulsing effects for online and idle users
  - Built "Friends Activity" page showing real-time user status with automatic updates
  - Added automatic status updates every 15 seconds in chat conversations

- **Cafe Management Enhancement (July 11, 2025)**: Added ownership-based cafe management
  - Enabled cafe owners to delete cafes they created with confirmation dialog
  - Added delete buttons visible only to cafe creators on cafe listing page
  - Implemented secure deletion with proper authorization checks
  - Added user_id tracking for cafe ownership and management rights

- **Chat System Enhancement (July 11, 2025)**: Transformed basic messaging into modern chat experience
  - Added real-time chat interface with modern bubble design and animations
  - Implemented message buttons on user profiles for easy conversation start
  - Enhanced chat with auto-scroll, Enter-to-send, and auto-refresh functionality
  - Created dedicated CSS styling for chat bubbles with WhatsApp-like design
  - Added message status indicators and improved conversation list UX