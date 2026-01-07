"""
Acme Data Room - Backend API

This Flask application provides the backend for a secure document repository.
Simplified version without external service dependencies (Google Drive).

Features:
- Mock authentication (no external OAuth required)
- Direct file uploads
- Simulated "Drive" files for demo purposes
- Local storage of documents

Author: Acme Team
"""

import os
import uuid
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config
from models import db, File

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend requests
CORS(app, origins=[Config.FRONTEND_URL], supports_credentials=True)

# Initialize database
db.init_app(app)

# Make sure the uploads directory exists for storing files
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Create database tables on startup
with app.app_context():
    db.create_all()


# =============================================================================
# Mock Authentication Routes
# No external OAuth - just a simple session simulation
# =============================================================================

# Simple in-memory session (for demo purposes)
_mock_authenticated = True  # Always authenticated for demo


@app.route('/api/auth/status')
def auth_status():
    """
    Check authentication status.
    In this simplified version, we're always "authenticated".
    """
    return jsonify({'authenticated': _mock_authenticated})


@app.route('/api/auth/login')
def auth_login():
    """
    Mock login - just returns success.
    No external OAuth required.
    """
    global _mock_authenticated
    _mock_authenticated = True
    return jsonify({'success': True, 'message': 'Logged in (mock mode)'})


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """
    Mock logout - clears the session.
    """
    global _mock_authenticated
    _mock_authenticated = False
    return jsonify({'success': True})


# =============================================================================
# Mock "Drive" Files - Simulated external file source
# =============================================================================

# Sample files that simulate a Google Drive listing
MOCK_DRIVE_FILES = [
    {
        'id': 'mock-1',
        'name': 'Q4 2025 Financial Report.pdf',
        'mimeType': 'application/pdf',
        'size': '2457600',
        'modifiedTime': '2025-12-20T10:30:00Z',
    },
    {
        'id': 'mock-2',
        'name': 'Company Overview Presentation.pptx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'size': '5242880',
        'modifiedTime': '2025-12-18T14:22:00Z',
    },
    {
        'id': 'mock-3',
        'name': 'Employee Directory.xlsx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'size': '1048576',
        'modifiedTime': '2025-12-15T09:15:00Z',
    },
    {
        'id': 'mock-4',
        'name': 'Legal Agreement Draft.docx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'size': '524288',
        'modifiedTime': '2025-12-12T16:45:00Z',
    },
    {
        'id': 'mock-5',
        'name': 'Product Roadmap 2026.pdf',
        'mimeType': 'application/pdf',
        'size': '3145728',
        'modifiedTime': '2025-12-10T11:00:00Z',
    },
    {
        'id': 'mock-6',
        'name': 'Office Building Photo.jpg',
        'mimeType': 'image/jpeg',
        'size': '4194304',
        'modifiedTime': '2025-12-08T08:30:00Z',
    },
    {
        'id': 'mock-7',
        'name': 'Board Meeting Minutes.pdf',
        'mimeType': 'application/pdf',
        'size': '819200',
        'modifiedTime': '2025-12-05T15:00:00Z',
    },
    {
        'id': 'mock-8',
        'name': 'Marketing Budget.xlsx',
        'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'size': '2097152',
        'modifiedTime': '2025-12-01T10:00:00Z',
    },
]


@app.route('/api/drive/files')
def drive_files():
    """
    Return mock "Drive" files for the file picker.
    Supports search filtering.
    """
    query = request.args.get('query', '').lower()
    
    if query:
        filtered = [f for f in MOCK_DRIVE_FILES if query in f['name'].lower()]
    else:
        filtered = MOCK_DRIVE_FILES
    
    return jsonify({
        'files': filtered,
        'nextPageToken': None  # No pagination for mock data
    })


@app.route('/api/drive/import', methods=['POST'])
def import_mock_file():
    """
    Simulate importing a file from "Drive".
    Creates a placeholder file in the data room.
    """
    data = request.json
    file_id = data.get('file_id')
    file_name = data.get('name')
    mime_type = data.get('mime_type')
    size = data.get('size')
    
    # Check if already imported
    existing = File.query.filter_by(source_id=file_id).first()
    if existing:
        return jsonify({'error': 'File already imported', 'file': existing.to_dict()}), 409
    
    # Create a placeholder file
    safe_name = secure_filename(file_name) or f"file_{file_id}"
    local_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{safe_name}")
    
    # Create a simple placeholder file with some content
    with open(local_path, 'w') as f:
        f.write(f"[Mock file placeholder]\n")
        f.write(f"Original name: {file_name}\n")
        f.write(f"MIME type: {mime_type}\n")
        f.write(f"This is a simulated file for demo purposes.\n")
    
    # Save to database
    file_record = File(
        name=file_name,
        mime_type=mime_type,
        size=size or os.path.getsize(local_path),
        source_id=file_id,
        source_type='mock_drive',
        local_path=local_path
    )
    db.session.add(file_record)
    db.session.commit()
    
    app.logger.info(f"Mock imported file: {file_name}")
    return jsonify({'success': True, 'file': file_record.to_dict()})


# =============================================================================
# Direct File Upload Routes
# =============================================================================

ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'zip'
}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Direct file upload endpoint.
    Accepts multipart form data with a 'file' field.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Create a unique filename
    original_name = file.filename
    safe_name = secure_filename(original_name)
    unique_id = str(uuid.uuid4())[:8]
    local_path = os.path.join(Config.UPLOAD_FOLDER, f"{unique_id}_{safe_name}")
    
    # Save the file
    file.save(local_path)
    
    # Get file size
    file_size = os.path.getsize(local_path)
    
    # Determine MIME type
    mime_type = file.content_type or 'application/octet-stream'
    
    # Save to database
    file_record = File(
        name=original_name,
        mime_type=mime_type,
        size=file_size,
        source_id=unique_id,
        source_type='upload',
        local_path=local_path
    )
    db.session.add(file_record)
    db.session.commit()
    
    app.logger.info(f"Uploaded file: {original_name}")
    return jsonify({'success': True, 'file': file_record.to_dict()})


# =============================================================================
# Data Room File Routes
# CRUD operations for files stored in the data room
# =============================================================================

@app.route('/api/files')
def list_files():
    """
    List all files in the data room.
    """
    files = File.query.order_by(File.created_at.desc()).all()
    return jsonify({'files': [f.to_dict() for f in files]})


@app.route('/api/files/<int:file_id>')
def get_file(file_id):
    """
    View or download a file from the data room.
    """
    file_record = File.query.get_or_404(file_id)
    
    if not os.path.exists(file_record.local_path):
        return jsonify({'error': 'File not found on disk'}), 404
    
    return send_file(
        file_record.local_path,
        mimetype=file_record.mime_type,
        as_attachment=False,
        download_name=file_record.name
    )


@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    Delete a file from the data room.
    """
    file_record = File.query.get_or_404(file_id)
    
    # Remove the file from disk
    if os.path.exists(file_record.local_path):
        os.remove(file_record.local_path)
    
    # Remove from database
    db.session.delete(file_record)
    db.session.commit()
    
    app.logger.info(f"Deleted file: {file_record.name}")
    return jsonify({'success': True})


@app.route('/api/files/search')
def search_files():
    """
    Search files in the data room by name.
    """
    query = request.args.get('q', '')
    files = File.query.filter(
        File.name.ilike(f'%{query}%')
    ).order_by(File.created_at.desc()).all()
    
    return jsonify({'files': [f.to_dict() for f in files]})


# =============================================================================
# Application Entry Point
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
