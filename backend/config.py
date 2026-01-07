"""
Application Configuration

This module centralizes all configuration for the Flask application.
Simplified version without Google OAuth dependencies.

Environment Variables:
    DATABASE_URL: Database connection string (default: SQLite)
    SECRET_KEY: Flask secret key for session security
    FRONTEND_URL: URL of the React frontend for CORS and redirects

Author: Acme Team
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Flask application configuration."""
    
    # Flask secret key - used for session management
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    # Default to SQLite for easy local development
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        'sqlite:///dataroom.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Frontend URL - used for CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 
        'uploads'
    )
    
    # Max upload size: 50MB
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
