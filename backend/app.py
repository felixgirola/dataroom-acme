"""
Acme Data Room - Backend API

This Flask application provides the backend for a secure document repository
that integrates with Google Drive. It handles OAuth authentication, file
imports, and local storage of documents for due diligence workflows.

Author: Felix Gabriel Girola
Created: December 24, 2025
Location: Mexico City, Mexico 🇲🇽

Assessment: Senior Full Stack Engineer (Python/Flask/React)
"""

import os
from flask import Flask, request, jsonify, redirect, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
from config import Config
from models import db, OAuthToken, File
from google_auth import (
    create_oauth_flow, 
    get_credentials_from_token, 
    get_drive_service,
    list_drive_files,
    download_file
)
from google.auth.transport.requests import Request as GoogleRequest

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for frontend requests
# This allows the React frontend to communicate with our API
CORS(app, origins=[Config.FRONTEND_URL], supports_credentials=True)

# Initialize database
db.init_app(app)

# Make sure the uploads directory exists for storing imported files
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Create database tables on startup
# In production, you'd want to use migrations (Flask-Migrate) instead
with app.app_context():
    db.create_all()


# =============================================================================
# Authentication Routes
# These endpoints handle the Google OAuth 2.0 flow for Drive access
# =============================================================================

@app.route('/api/auth/status')
def auth_status():
    """
    Check if the user has valid Google Drive authentication.
    
    This endpoint is called by the frontend on page load to determine
    whether to show the login screen or the main application.
    
    Returns:
        JSON with 'authenticated' boolean
    """
    token = OAuthToken.query.order_by(OAuthToken.id.desc()).first()
    
    # Check if we have a valid, non-expired token
    if token and token.token_expiry and token.token_expiry > datetime.utcnow():
        return jsonify({'authenticated': True})
    
    # Try to refresh an expired token if we have a refresh token
    elif token and token.refresh_token:
        try:
            creds = get_credentials_from_token({
                'access_token': token.access_token,
                'refresh_token': token.refresh_token,
                'client_id': Config.GOOGLE_CLIENT_ID,
                'client_secret': Config.GOOGLE_CLIENT_SECRET,
                'expiry': token.token_expiry
            })
            
            if creds.expired:
                creds.refresh(GoogleRequest())
                # Update the stored token with the new access token
                token.access_token = creds.token
                token.token_expiry = creds.expiry
                db.session.commit()
            
            return jsonify({'authenticated': True})
        except Exception as e:
            # Token refresh failed - user needs to re-authenticate
            app.logger.warning(f"Token refresh failed: {e}")
            return jsonify({'authenticated': False})
    
    return jsonify({'authenticated': False})


@app.route('/api/auth/login')
def auth_login():
    """
    Start the Google OAuth flow.
    
    This endpoint generates the Google authorization URL that the frontend
    will redirect the user to. After the user grants permission, Google
    redirects back to our callback endpoint.
    
    Returns:
        JSON with 'auth_url' - the Google OAuth authorization URL
    """
    flow = create_oauth_flow(
        Config.GOOGLE_CLIENT_ID,
        Config.GOOGLE_CLIENT_SECRET,
        Config.GOOGLE_REDIRECT_URI
    )
    
    # Generate the authorization URL
    # - access_type='offline' ensures we get a refresh token
    # - prompt='consent' forces the consent screen to show (ensures refresh token)
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return jsonify({'auth_url': auth_url})


@app.route('/api/auth/callback')
def auth_callback():
    """
    Handle the OAuth callback from Google.
    
    After the user grants permission on Google's consent screen, they're
    redirected here with an authorization code. We exchange this code for
    access and refresh tokens, then store them in the database.
    
    Query Parameters:
        code: The authorization code from Google
        
    Redirects:
        To the frontend with success=true or error message
    """
    code = request.args.get('code')
    
    if not code:
        return redirect(f"{Config.FRONTEND_URL}?error=no_code")
    
    try:
        # Exchange the authorization code for tokens
        flow = create_oauth_flow(
            Config.GOOGLE_CLIENT_ID,
            Config.GOOGLE_CLIENT_SECRET,
            Config.GOOGLE_REDIRECT_URI
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Store or update the token in the database
        # For a multi-user app, you'd associate this with a user ID
        token = OAuthToken.query.first()
        if token:
            token.access_token = credentials.token
            # Keep existing refresh token if new one isn't provided
            token.refresh_token = credentials.refresh_token or token.refresh_token
            token.token_expiry = credentials.expiry
        else:
            token = OAuthToken(
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry
            )
            db.session.add(token)
        
        db.session.commit()
        return redirect(f"{Config.FRONTEND_URL}?success=true")
        
    except Exception as e:
        app.logger.error(f"OAuth callback error: {e}")
        return redirect(f"{Config.FRONTEND_URL}?error={str(e)}")


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """
    Log out by clearing stored OAuth tokens.
    
    This removes all stored tokens from the database. The user will need
    to re-authenticate to access Google Drive again.
    
    Returns:
        JSON with 'success' boolean
    """
    OAuthToken.query.delete()
    db.session.commit()
    return jsonify({'success': True})


# =============================================================================
# Helper Functions
# =============================================================================

def get_valid_credentials():
    """
    Retrieve valid Google credentials, refreshing if necessary.
    
    This is a helper function used by all endpoints that need to access
    Google Drive. It handles token refresh automatically.
    
    Returns:
        google.oauth2.credentials.Credentials or None if not authenticated
    """
    token = OAuthToken.query.order_by(OAuthToken.id.desc()).first()
    if not token:
        return None
    
    creds = get_credentials_from_token({
        'access_token': token.access_token,
        'refresh_token': token.refresh_token,
        'client_id': Config.GOOGLE_CLIENT_ID,
        'client_secret': Config.GOOGLE_CLIENT_SECRET,
        'expiry': token.token_expiry
    })
    
    # Automatically refresh expired tokens
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        token.access_token = creds.token
        token.token_expiry = creds.expiry
        db.session.commit()
    
    return creds


# =============================================================================
# Google Drive Routes
# These endpoints interact with the Google Drive API
# =============================================================================

@app.route('/api/drive/files')
def drive_files():
    """
    List files from the user's Google Drive.
    
    Returns a paginated list of files that can be imported into the data room.
    Supports search queries to filter files by name.
    
    Query Parameters:
        pageToken: Token for pagination (from previous response)
        query: Search string to filter files by name
        
    Returns:
        JSON with 'files' array and optional 'nextPageToken'
    """
    creds = get_valid_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        service = get_drive_service(creds)
        page_token = request.args.get('pageToken')
        query = request.args.get('query')
        
        results = list_drive_files(service, page_token, query)
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Error listing drive files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/drive/import', methods=['POST'])
def import_file():
    """
    Import a file from Google Drive into the data room.
    
    Downloads the file from Google Drive and stores it locally on the server.
    File metadata is saved to the database for listing and retrieval.
    
    Google Docs, Sheets, and Slides are automatically exported to PDF/XLSX
    format since they don't have a native file format.
    
    Request Body (JSON):
        file_id: Google Drive file ID
        name: File name
        mime_type: MIME type of the file
        size: File size in bytes (optional)
        
    Returns:
        JSON with 'success' boolean and 'file' object
    """
    creds = get_valid_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    file_id = data.get('file_id')
    file_name = data.get('name')
    mime_type = data.get('mime_type')
    size = data.get('size')
    
    # Prevent duplicate imports - each file can only be imported once
    existing = File.query.filter_by(google_drive_id=file_id).first()
    if existing:
        return jsonify({'error': 'File already imported', 'file': existing.to_dict()}), 409
    
    try:
        service = get_drive_service(creds)
        
        # Download the file (handles Google Docs export automatically)
        file_buffer, final_name, final_mime = download_file(
            service, file_id, file_name, mime_type
        )
        
        # Create a safe filename for local storage
        # Remove any characters that could cause filesystem issues
        safe_name = "".join(
            c for c in final_name 
            if c.isalnum() or c in (' ', '.', '-', '_')
        ).strip()
        
        # Prefix with file_id to ensure uniqueness
        local_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}_{safe_name}")
        
        # Write the file to disk
        with open(local_path, 'wb') as f:
            f.write(file_buffer.read())
        
        # Save file metadata to database
        file_record = File(
            name=final_name,
            mime_type=final_mime,
            size=size or os.path.getsize(local_path),
            google_drive_id=file_id,
            local_path=local_path
        )
        db.session.add(file_record)
        db.session.commit()
        
        app.logger.info(f"Successfully imported file: {final_name}")
        return jsonify({'success': True, 'file': file_record.to_dict()})
        
    except Exception as e:
        app.logger.error(f"Error importing file: {e}")
        return jsonify({'error': str(e)}), 500


# =============================================================================
# Data Room File Routes
# CRUD operations for files stored in the data room
# =============================================================================

@app.route('/api/files')
def list_files():
    """
    List all files in the data room.
    
    Returns all imported files, sorted by creation date (newest first).
    
    Returns:
        JSON with 'files' array
    """
    files = File.query.order_by(File.created_at.desc()).all()
    return jsonify({'files': [f.to_dict() for f in files]})


@app.route('/api/files/<int:file_id>')
def get_file(file_id):
    """
    View or download a file from the data room.
    
    Serves the actual file content with appropriate MIME type headers
    so it can be viewed directly in the browser.
    
    Path Parameters:
        file_id: Database ID of the file
        
    Returns:
        The file content with appropriate headers
    """
    file_record = File.query.get_or_404(file_id)
    
    # Make sure the file still exists on disk
    if not os.path.exists(file_record.local_path):
        return jsonify({'error': 'File not found on disk'}), 404
    
    return send_file(
        file_record.local_path,
        mimetype=file_record.mime_type,
        as_attachment=False,  # Display in browser instead of download
        download_name=file_record.name
    )


@app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    """
    Delete a file from the data room.
    
    Removes the file from both local storage and the database.
    Note: This does NOT delete the original file from Google Drive.
    
    Path Parameters:
        file_id: Database ID of the file
        
    Returns:
        JSON with 'success' boolean
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
    
    Performs a case-insensitive search on file names.
    
    Query Parameters:
        q: Search query string
        
    Returns:
        JSON with 'files' array of matching files
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
    # Run in debug mode for development
    # In production, use gunicorn: gunicorn -w 4 app:app
    # Note: Port 5000 is often used by AirPlay on macOS, so we use 5001
    app.run(debug=True, port=5001)
