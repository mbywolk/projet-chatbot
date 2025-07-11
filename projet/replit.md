# ChatBot Universitaire - University Assistant AI Application

## Overview

This is a Flask-based web application that provides an AI-powered chatbot specifically designed for university assistance. The application allows students and university staff to interact with an intelligent assistant that can help with various university-related queries including admissions, courses, services, and general campus information. The system features user authentication, conversation management, and integration with Google's Gemini AI model.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Database**: SQLAlchemy with configurable database backend (currently prepared for any SQL database)
- **AI Integration**: Google Gemini 2.5 Flash model for natural language processing
- **Session Management**: Flask sessions with configurable secret key
- **Security**: Werkzeug password hashing and ProxyFix middleware

### Frontend Architecture
- **Template Engine**: Jinja2 with Flask
- **Styling**: Bootstrap 5.3.0 framework
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript with progressive enhancement
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Authentication System
- User registration and login functionality
- Password hashing using Werkzeug security utilities
- Session-based authentication
- User profile management with full name support (nom, postnom, prenom structure)

## Key Components

### 1. Application Core (`app.py`)
- Flask application initialization
- SQLAlchemy database configuration
- Environment-based configuration for database URL and session secret
- Database connection pooling with health checks

### 2. Data Models (`models.py`)
- **User Model**: Stores user credentials and profile information
- **Conversation Model**: Tracks chat conversations with timestamps
- **Message Model**: Individual messages within conversations with user/bot distinction
- Relationships with cascade delete for data integrity

### 3. AI Service (`gemini_service.py`)
- Integration with Google Gemini API
- French-language university context prompting
- Error handling and fallback responses
- Contextual conversation support

### 4. Route Handlers (`routes.py`)
- Authentication routes (login, register, logout)
- Chat interface and conversation management
- User profile and settings pages
- API endpoints for real-time chat functionality

### 5. Frontend Templates
- **Base Template**: Common layout with Bootstrap and Font Awesome
- **Authentication**: Combined login/register interface with tabs
- **Chat Interface**: Real-time messaging with conversation history
- **User Dashboard**: Welcome screen with service overview
- **Profile Management**: User information and statistics display

## Data Flow

1. **User Authentication**: Users register/login through the auth system
2. **Session Management**: Authenticated sessions stored server-side
3. **Conversation Creation**: New conversations automatically created for users
4. **Message Processing**: User messages sent to Gemini AI service
5. **Response Generation**: AI responses generated with university context
6. **Data Persistence**: All conversations and messages stored in database
7. **Real-time Updates**: Chat interface updates dynamically

## External Dependencies

### Python Packages
- Flask: Web framework
- Flask-SQLAlchemy: Database ORM
- Werkzeug: Security utilities and WSGI helpers
- Google GenAI: Gemini AI integration

### Frontend Libraries
- Bootstrap 5.3.0: UI framework
- Font Awesome 6.4.0: Icon library

### Environment Variables Required
- `DATABASE_URL`: Database connection string
- `SESSION_SECRET`: Flask session encryption key
- `GEMINI_API_KEY`: Google Gemini API authentication

## Deployment Strategy

The application is configured for flexible deployment:

- **Development**: Direct Flask development server (port 5000)
- **Production**: WSGI-compatible with ProxyFix middleware for reverse proxy support
- **Database**: Environment-configurable with connection pooling
- **Scaling**: Stateless design allows for horizontal scaling
- **Security**: Environment-based secrets management

The application uses logging for debugging and monitoring, with configurable log levels. Database tables are automatically created on application startup.

## Changelog

```
Changelog:
- July 02, 2025. Initial setup complete with full chatbot functionality
- July 02, 2025. Fixed navigation errors for new conversation creation
- July 02, 2025. Fixed profile page template error for delete all conversations
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```