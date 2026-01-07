"""
Database Models for Acme Data Room

This module defines the SQLAlchemy models for storing file metadata.
Simplified version without external OAuth dependencies.

Author: Acme Team
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize SQLAlchemy - this is imported by app.py
db = SQLAlchemy()


class File(db.Model):
    """
    Store metadata for files in the data room.
    
    Files can come from different sources:
    - 'upload': Direct file upload
    - 'mock_drive': Simulated Drive import (for demo)
    
    Attributes:
        id: Primary key (used in API URLs)
        name: Original filename
        mime_type: MIME type of the stored file
        size: File size in bytes
        source_id: External ID (upload UUID or mock Drive ID)
        source_type: Where the file came from ('upload', 'mock_drive')
        local_path: Path to the file on the server's filesystem
        created_at: When this file was imported/uploaded
    """
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(255))
    size = db.Column(db.BigInteger)
    source_id = db.Column(db.String(255), unique=True)
    source_type = db.Column(db.String(50), default='upload')
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
            'source_id': self.source_id,
            'source_type': self.source_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<File {self.name}>'
