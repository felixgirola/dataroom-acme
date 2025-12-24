"""
Application Configuration

This module centralizes all configuration for the Flask application.
Configuration is loaded from environment variables with sensible defaults
for local development.

Environment Variables:
    DATABASE_URL: Database connection string (default: SQLite)
    GOOGLE_CLIENT_ID: OAuth client ID from Google Cloud Console
    GOOGLE_CLIENT_SECRET: OAuth client secret from Google Cloud Console
    GOOGLE_REDIRECT_URI: OAuth callback URL (default: localhost:5001)
    SECRET_KEY: Flask secret key for session security
    FRONTEND_URL: URL of the React frontend for CORS and redirects

Author: Felix Gabriel Girola
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This is useful for local development
load_dotenv()


class Config:
    """Flask application configuration."""
    
    # Flask secret key - used for session management
    # IMPORTANT: Change this in production!
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # Default to SQLite for easy local development
    # For production, use PostgreSQL: postgresql://user:pass@host:port/dbname
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///dataroom.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable Flask-SQLAlchemy event system
    
    # Google OAuth configuration
    # These MUST be set for the application to work
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv(
        'GOOGLE_REDIRECT_URI', 
        'http://localhost:5001/api/auth/callback'
    )
    
    # Frontend URL - used for CORS and OAuth redirects
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # File upload configuration
    # Uploaded files are stored in the 'uploads' directory next to app.py
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'uploads'
    )
