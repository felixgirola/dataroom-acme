"""
Vercel Serverless API for Acme Data Room

Simplified version with mock authentication and no external dependencies.
Perfect for demos and quick deployments.

Author: Acme Team
"""

import os
import json
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://dataroom-acme.vercel.app')

# In-memory storage (for demo - resets on each cold start)
session_storage = {'authenticated': True}  # Always authenticated for demo
files_storage = {}

# Mock "Drive" files for demo
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


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
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
        elif path == '/api/upload':
            self.handle_upload()
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
        """Always authenticated in demo mode"""
        self.send_json({'authenticated': session_storage.get('authenticated', True)})
    
    def handle_auth_login(self):
        """Mock login"""
        session_storage['authenticated'] = True
        self.send_json({'success': True, 'message': 'Logged in (demo mode)'})
    
    def handle_logout(self):
        """Mock logout"""
        session_storage['authenticated'] = False
        files_storage.clear()
        self.send_json({'success': True})
    
    def handle_drive_files(self, query):
        """Return mock Drive files"""
        search = query.get('query', [None])[0]
        
        if search:
            search_lower = search.lower()
            filtered = [f for f in MOCK_DRIVE_FILES if search_lower in f['name'].lower()]
        else:
            filtered = MOCK_DRIVE_FILES
        
        self.send_json({
            'files': filtered,
            'nextPageToken': None
        })
    
    def handle_import(self, data):
        """Import mock file"""
        file_id = data.get('file_id')
        file_name = data.get('name')
        mime_type = data.get('mime_type')
        size = data.get('size')
        
        if file_id in files_storage:
            self.send_json({'error': 'File already imported'}, 409)
            return
        
        file_record = {
            'id': len(files_storage) + 1,
            'name': file_name,
            'mime_type': mime_type,
            'size': size,
            'source_id': file_id,
            'source_type': 'mock_drive',
            'created_at': datetime.utcnow().isoformat()
        }
        files_storage[file_id] = file_record
        
        self.send_json({'success': True, 'file': file_record})
    
    def handle_upload(self):
        """Handle file upload (limited in serverless)"""
        # Note: In serverless, we simulate the upload
        unique_id = str(uuid.uuid4())[:8]
        file_record = {
            'id': len(files_storage) + 1,
            'name': f'uploaded_file_{unique_id}.txt',
            'mime_type': 'text/plain',
            'size': 1024,
            'source_id': unique_id,
            'source_type': 'upload',
            'created_at': datetime.utcnow().isoformat()
        }
        files_storage[unique_id] = file_record
        self.send_json({'success': True, 'file': file_record})
    
    def handle_list_files(self):
        """List all files"""
        files = list(files_storage.values())
        files.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        self.send_json({'files': files})
    
    def handle_search_files(self, query):
        """Search files by name"""
        search = query.get('q', [''])[0].lower()
        files = [f for f in files_storage.values() if search in f.get('name', '').lower()]
        self.send_json({'files': files})
    
    def handle_get_file(self, file_id):
        """Get file - returns mock content"""
        for f in files_storage.values():
            if str(f['id']) == file_id:
                # Return mock content as text
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                content = f"[Mock file: {f['name']}]\n\nThis is a demo file placeholder."
                self.wfile.write(content.encode())
                return
        
        self.send_json({'error': 'File not found'}, 404)
    
    def handle_delete_file(self, file_id):
        """Delete a file"""
        for source_id, f in list(files_storage.items()):
            if str(f['id']) == file_id:
                del files_storage[source_id]
                self.send_json({'success': True})
                return
        
        self.send_json({'error': 'File not found'}, 404)
