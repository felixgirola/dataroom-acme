"""
Database Models for Acme Data Room

This module defines the SQLAlchemy models for storing OAuth tokens
and file metadata. The data model is designed to be simple but 
extensible for future features.

For production use with multiple users, you would add a User model
and associate tokens and files with specific users.

Author: Felix Gabriel Girola
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy - this is imported by app.py
db = SQLAlchemy()


class OAuthToken(db.Model):
    """
    Store Google OAuth tokens for API access.
    
    This model stores the access and refresh tokens obtained during
    the OAuth flow. The access token is used for API calls, while
    the refresh token allows us to get new access tokens when they expire.
    
    Note: In a multi-user application, you would add a user_id foreign key
    to associate tokens with specific users.
    
    Attributes:
        id: Primary key
        access_token: The OAuth access token (expires after ~1 hour)
        refresh_token: The refresh token (long-lived, used to get new access tokens)
        token_expiry: When the access token expires
        created_at: When this token was first created
        updated_at: Last time this token was updated (e.g., refreshed)
    """
    __tablename__ = 'oauth_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)  # May be null if not granted
    token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<OAuthToken {self.id}>'


class File(db.Model):
    """
    Store metadata for files imported into the data room.
    
    When a file is imported from Google Drive, we download it to local
    storage and save its metadata here. This allows us to list and
    serve files without hitting the Google Drive API.
    
    The google_drive_id is marked unique to prevent duplicate imports
    of the same file.
    
    Attributes:
        id: Primary key (used in API URLs)
        name: Original filename (may include extension added during export)
        mime_type: MIME type of the stored file
        size: File size in bytes
        google_drive_id: The original Google Drive file ID (unique)
        local_path: Path to the file on the server's filesystem
        created_at: When this file was imported
    """
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(255))
    size = db.Column(db.BigInteger)  # BigInteger for large files
    google_drive_id = db.Column(db.String(255), unique=True)
    local_path = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        Convert the model to a dictionary for JSON serialization.
        
        Note: We don't expose local_path to the frontend for security.
        """
        return {
            'id': self.id,
            'name': self.name,
            'mime_type': self.mime_type,
            'size': self.size,
            'google_drive_id': self.google_drive_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<File {self.name}>'
