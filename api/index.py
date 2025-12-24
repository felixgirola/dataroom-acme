"""
Vercel Serverless API for Acme Data Room

Lightweight API using direct HTTP requests instead of the heavy
google-api-python-client to stay within Vercel's 250MB limit.

Author: Felix Gabriel Girola
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import requests

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request as GoogleRequest

# Configuration from environment
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://dataroom-acme.vercel.app')
REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', f'{FRONTEND_URL}/api/auth/callback')

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

# In-memory storage (for demo - use Vercel KV or database in production)
token_storage = {}
files_storage = {}


def create_oauth_flow():
    """Create OAuth flow for Google Drive"""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


def get_credentials():
    """Get valid credentials from storage"""
    if 'token' not in token_storage:
        return None
    
    token_data = token_storage['token']
    creds = Credentials(
        token=token_data['access_token'],
        refresh_token=token_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
    )
    
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        token_storage['token']['access_token'] = creds.token
    
    return creds


def drive_api_request(creds, endpoint, params=None):
    """Make a request to Google Drive API using requests library"""
    headers = {'Authorization': f'Bearer {creds.token}'}
    url = f'https://www.googleapis.com/drive/v3/{endpoint}'
    response = requests.get(url, headers=headers, params=params)
    return response.json()


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/api/auth/status':
            self.handle_auth_status()
        elif path == '/api/auth/login':
            self.handle_auth_login()
        elif path == '/api/auth/callback':
            self.handle_auth_callback(query)
        elif path == '/api/drive/files':
            self.handle_drive_files(query)
        elif path == '/api/files':
            self.handle_list_files()
        elif path == '/api/files/search':
            self.handle_search_files(query)
        elif path.startswith('/api/files/'):
            file_id = path.split('/')[-1]
            self.handle_get_file(file_id)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        if path == '/api/auth/logout':
            self.handle_logout()
        elif path == '/api/drive/import':
            self.handle_import(data)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path.startswith('/api/files/'):
            file_id = path.split('/')[-1]
            self.handle_delete_file(file_id)
        else:
            self.send_json({'error': 'Not found'}, 404)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def handle_auth_status(self):
        authenticated = 'token' in token_storage and token_storage['token'].get('access_token')
        self.send_json({'authenticated': bool(authenticated)})
    
    def handle_auth_login(self):
        flow = create_oauth_flow()
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        self.send_json({'auth_url': auth_url})
    
    def handle_auth_callback(self, query):
        code = query.get('code', [None])[0]
        
        if not code:
            self.send_response(302)
            self.send_header('Location', f'{FRONTEND_URL}?error=no_code')
            self.end_headers()
            return
        
        try:
            flow = create_oauth_flow()
            flow.fetch_token(code=code)
            creds = flow.credentials
            
            token_storage['token'] = {
                'access_token': creds.token,
                'refresh_token': creds.refresh_token,
            }
            
            self.send_response(302)
            self.send_header('Location', f'{FRONTEND_URL}?success=true')
            self.end_headers()
        except Exception as e:
            self.send_response(302)
            self.send_header('Location', f'{FRONTEND_URL}?error={str(e)}')
            self.end_headers()
    
    def handle_logout(self):
        token_storage.clear()
        files_storage.clear()
        self.send_json({'success': True})
    
    def handle_drive_files(self, query):
        creds = get_credentials()
        if not creds:
            self.send_json({'error': 'Not authenticated'}, 401)
            return
        
        try:
            params = {
                'pageSize': 50,
                'fields': 'nextPageToken,files(id,name,mimeType,size,modifiedTime)',
                'q': 'trashed=false',
                'orderBy': 'modifiedTime desc'
            }
            
            page_token = query.get('pageToken', [None])[0]
            if page_token:
                params['pageToken'] = page_token
            
            search = query.get('query', [None])[0]
            if search:
                params['q'] = f"trashed=false and name contains '{search}'"
            
            result = drive_api_request(creds, 'files', params)
            self.send_json(result)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_import(self, data):
        creds = get_credentials()
        if not creds:
            self.send_json({'error': 'Not authenticated'}, 401)
            return
        
        file_id = data.get('file_id')
        file_name = data.get('name')
        mime_type = data.get('mime_type')
        size = data.get('size')
        
        if file_id in files_storage:
            self.send_json({'error': 'File already imported'}, 409)
            return
        
        try:
            file_record = {
                'id': len(files_storage) + 1,
                'name': file_name,
                'mime_type': mime_type,
                'size': size,
                'google_drive_id': file_id,
                'created_at': datetime.utcnow().isoformat()
            }
            files_storage[file_id] = file_record
            
            self.send_json({'success': True, 'file': file_record})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_list_files(self):
        files = list(files_storage.values())
        files.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        self.send_json({'files': files})
    
    def handle_search_files(self, query):
        search = query.get('q', [''])[0].lower()
        files = [f for f in files_storage.values() if search in f.get('name', '').lower()]
        self.send_json({'files': files})
    
    def handle_get_file(self, file_id):
        for f in files_storage.values():
            if str(f['id']) == file_id:
                creds = get_credentials()
                if creds:
                    try:
                        result = drive_api_request(
                            creds, 
                            f"files/{f['google_drive_id']}", 
                            {'fields': 'webViewLink'}
                        )
                        if 'webViewLink' in result:
                            self.send_response(302)
                            self.send_header('Location', result['webViewLink'])
                            self.end_headers()
                            return
                    except:
                        pass
                
                self.send_json({'error': 'Cannot view file'}, 500)
                return
        
        self.send_json({'error': 'File not found'}, 404)
    
    def handle_delete_file(self, file_id):
        for gid, f in list(files_storage.items()):
            if str(f['id']) == file_id:
                del files_storage[gid]
                self.send_json({'success': True})
                return
        
        self.send_json({'error': 'File not found'}, 404)
