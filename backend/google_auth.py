"""
Google OAuth and Drive API Helper Functions

This module handles all interactions with Google's OAuth 2.0 system
and the Google Drive API. It provides utilities for:
- Creating OAuth flows for authentication
- Managing credentials and tokens
- Listing files from Google Drive
- Downloading files (including exporting Google Docs formats)

The OAuth scopes used are read-only to minimize security risks.

Author: Felix Gabriel Girola
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime, timedelta
import io

# OAuth scopes - we only request read access to Drive
# This follows the principle of least privilege
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]


def create_oauth_flow(client_id, client_secret, redirect_uri):
    """
    Create an OAuth 2.0 flow for Google authentication.
    
    This sets up the OAuth flow that will be used to get authorization
    from the user. The flow handles the OAuth dance and token exchange.
    
    Args:
        client_id: Google OAuth client ID from Cloud Console
        client_secret: Google OAuth client secret
        redirect_uri: Where Google should redirect after authorization
        
    Returns:
        A configured google_auth_oauthlib.flow.Flow object
    """
    # Build the client configuration programmatically
    # This avoids needing to manage a client_secrets.json file
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri]
        }
    }
    
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = redirect_uri
    return flow


def get_credentials_from_token(token_data):
    """
    Create a Credentials object from stored token data.
    
    This reconstructs Google credentials from our database storage
    so we can make API calls.
    
    Args:
        token_data: Dictionary with access_token, refresh_token, 
                    client_id, client_secret, and expiry
                    
    Returns:
        A google.oauth2.credentials.Credentials object
    """
    return Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=token_data['client_id'],
        client_secret=token_data['client_secret'],
        expiry=token_data.get('expiry')
    )


def get_drive_service(credentials):
    """
    Get a Google Drive API service client.
    
    Args:
        credentials: Valid Google OAuth credentials
        
    Returns:
        A googleapiclient.discovery.Resource for Drive API v3
    """
    return build('drive', 'v3', credentials=credentials)


def list_drive_files(service, page_token=None, query=None):
    """
    List files from the user's Google Drive.
    
    Returns files sorted by modification time (most recent first).
    Automatically filters out trashed files.
    
    Args:
        service: Google Drive API service
        page_token: Token for fetching the next page of results
        query: Optional search string to filter by filename
        
    Returns:
        Dictionary with 'files' list and optional 'nextPageToken'
    """
    # Build the query - always exclude trashed files
    q = "trashed=false"
    if query:
        # Add name search - escape single quotes in the query
        safe_query = query.replace("'", "\\'")
        q += f" and name contains '{safe_query}'"
    
    # Request file metadata we need for the UI
    results = service.files().list(
        pageSize=50,  # Reasonable page size for UI
        fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, iconLink, thumbnailLink)",
        pageToken=page_token,
        q=q,
        orderBy="modifiedTime desc"
    ).execute()
    
    return results


def download_file(service, file_id, file_name, mime_type):
    """
    Download a file from Google Drive.
    
    Handles special cases for Google Workspace files (Docs, Sheets, Slides)
    which need to be exported to a standard format since they don't have
    a native file format.
    
    Export mappings:
    - Google Docs -> PDF
    - Google Sheets -> Excel (.xlsx)
    - Google Slides -> PDF
    - Google Drawings -> PDF
    
    Args:
        service: Google Drive API service
        file_id: ID of the file to download
        file_name: Original filename
        mime_type: Original MIME type
        
    Returns:
        Tuple of (file_buffer, final_filename, final_mime_type)
    """
    # Mapping of Google Workspace MIME types to export formats
    # These files don't have a "native" format - they must be exported
    export_mime_types = {
        'application/vnd.google-apps.document': 'application/pdf',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/pdf',
        'application/vnd.google-apps.drawing': 'application/pdf',
    }
    
    if mime_type in export_mime_types:
        # Export Google Workspace file to a standard format
        export_mime = export_mime_types[mime_type]
        request = service.files().export_media(
            fileId=file_id,
            mimeType=export_mime
        )
        
        # Add appropriate file extension if not already present
        ext_map = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx'
        }
        if export_mime in ext_map and not file_name.endswith(ext_map[export_mime]):
            file_name += ext_map[export_mime]
        
        mime_type = export_mime
    else:
        # Regular file - download directly
        request = service.files().get_media(fileId=file_id)
    
    # Download the file content to memory
    file_buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(file_buffer, request)
    
    done = False
    while not done:
        status, done = downloader.next_chunk()
        # Could add progress tracking here for large files
    
    # Reset buffer position for reading
    file_buffer.seek(0)
    return file_buffer, file_name, mime_type
