"""
Vercel Serverless API for Acme Data Room

Simplified version with mock authentication and no external dependencies.
Perfect for demos and quick deployments.
"""

import os
import json
import uuid
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configuration
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://dataroom-acme.vercel.app')

# In-memory storage (for demo - resets on each cold start)
session_storage = {'authenticated': True}  # Always authenticated for demo
files_storage = {}

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'txt', 'csv', 'jpg', 'jpeg', 'png', 'gif', 'zip'
}

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
        """Handle file upload with multipart form parsing"""
        content_type = self.headers.get('Content-Type', '')

        if 'multipart/form-data' not in content_type:
            self.send_json({'error': 'Invalid content type'}, 400)
            return

        # Extract boundary from content type
        boundary_match = re.search(r'boundary=(.+)', content_type)
        if not boundary_match:
            self.send_json({'error': 'No boundary found'}, 400)
            return

        boundary = boundary_match.group(1).strip()
        if boundary.startswith('"') and boundary.endswith('"'):
            boundary = boundary[1:-1]

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            self.send_json({'error': 'No file provided'}, 400)
            return

        body = self.rfile.read(content_length)

        # Parse multipart data
        boundary_bytes = ('--' + boundary).encode()
        parts = body.split(boundary_bytes)

        filename = None
        file_content = None
        content_type_file = 'application/octet-stream'

        for part in parts:
            if b'Content-Disposition' not in part:
                continue

            # Split headers and content
            try:
                header_end = part.find(b'\r\n\r\n')
                if header_end == -1:
                    continue

                headers_raw = part[:header_end].decode('utf-8', errors='ignore')
                content = part[header_end + 4:]

                # Remove trailing boundary markers
                if content.endswith(b'--\r\n'):
                    content = content[:-4]
                elif content.endswith(b'\r\n'):
                    content = content[:-2]

                # Extract filename from Content-Disposition
                filename_match = re.search(r'filename="([^"]+)"', headers_raw)
                if filename_match:
                    filename = filename_match.group(1)
                    file_content = content

                    # Extract content type if present
                    ct_match = re.search(r'Content-Type:\s*([^\r\n]+)', headers_raw)
                    if ct_match:
                        content_type_file = ct_match.group(1).strip()
            except Exception:
                continue

        if not filename or file_content is None:
            self.send_json({'error': 'No file provided'}, 400)
            return

        # Validate extension
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            self.send_json({'error': f'File type .{ext} not allowed'}, 400)
            return

        unique_id = str(uuid.uuid4())[:8]
        file_record = {
            'id': len(files_storage) + 1,
            'name': filename,
            'mime_type': content_type_file,
            'size': len(file_content),
            'source_id': unique_id,
            'source_type': 'upload',
            'created_at': datetime.utcnow().isoformat(),
            '_content': file_content  # Store content for retrieval
        }
        files_storage[unique_id] = file_record

        # Return response without the _content field
        response_record = {k: v for k, v in file_record.items() if k != '_content'}
        self.send_json({'success': True, 'file': response_record})
    
    def handle_list_files(self):
        """List all files"""
        files = []
        for f in files_storage.values():
            # Exclude internal _content field from response
            files.append({k: v for k, v in f.items() if k != '_content'})
        files.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        self.send_json({'files': files})
    
    def handle_search_files(self, query):
        """Search files by name"""
        search = query.get('q', [''])[0].lower()
        files = []
        for f in files_storage.values():
            if search in f.get('name', '').lower():
                files.append({k: v for k, v in f.items() if k != '_content'})
        self.send_json({'files': files})
    
    def handle_get_file(self, file_id):
        """Get file - returns actual file content if available"""
        for f in files_storage.values():
            if str(f['id']) == file_id:
                mime_type = f.get('mime_type', 'application/octet-stream')
                filename = f.get('name', 'file')

                self.send_response(200)
                self.send_header('Content-Type', mime_type)
                self.send_header('Content-Disposition', f'inline; filename="{filename}"')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                # Return actual content if stored, otherwise placeholder
                if '_content' in f and f['_content']:
                    self.wfile.write(f['_content'])
                else:
                    # Mock files from demo library
                    content = f"[Demo file: {f['name']}]\n\nThis is a placeholder for demo purposes."
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
