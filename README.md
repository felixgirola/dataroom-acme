# Acme Data Room

A secure virtual data room MVP for document management during M&A due diligence. Built as a fullstack application with React/TypeScript frontend and Flask/Python backend.

## Quick Start

```bash
# Backend (Terminal 1)
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

---

## Features

### Core Functionality (All Required Features Implemented)
- **File Import** - Import files from external sources (simulated Google Drive)
- **Direct Upload** - Upload files directly from your computer
- **File Viewing** - Click any file to view/download in browser
- **File Deletion** - Remove files from the data room (does not affect source)
- **Search** - Filter files by name

### Technical Highlights
- OAuth flow simulation (demonstrates the full UI/UX without external dependencies)
- Token refresh handling pattern (ready for real OAuth integration)
- Duplicate file detection on import
- File type validation (whitelist-based security)
- Responsive design for desktop and mobile

---

## Important: Mock Authentication Approach

### Why Mock Authentication Instead of Real Google OAuth?

This implementation uses **simulated authentication and Google Drive integration** rather than real OAuth. Here's the reasoning:

#### 1. Zero-Configuration Demo
Real Google OAuth requires:
- Creating a Google Cloud Project
- Enabling the Drive API
- Configuring OAuth consent screen
- Creating credentials and managing secrets
- Adding test users (for unverified apps)

With mock auth, reviewers can **clone and run immediately** without any setup.

#### 2. Same UI/UX Flow
The mock implementation demonstrates the **exact same user experience**:
- Login screen with authentication prompt
- File picker showing available files to import
- Import flow with progress feedback
- Session management (login/logout)

The only difference is the data source - mock files instead of real Drive files.

#### 3. Production-Ready Architecture
The code is structured to easily swap mock for real OAuth:

```python
# backend/app.py - Current mock implementation
@app.route('/api/auth/login')
def auth_login():
    return jsonify({'success': True, 'message': 'Logged in (mock mode)'})

# To enable real OAuth, update to use google_auth.py:
# from google_auth import create_oauth_flow
# @app.route('/api/auth/login')
# def auth_login():
#     flow = create_oauth_flow()
#     return redirect(flow.authorization_url())
```

#### 4. The Real OAuth Code Exists
The file `backend/google_auth.py` contains a **complete Google OAuth implementation**:
- OAuth 2.0 flow with PKCE
- Token storage and refresh
- Drive API file listing
- File download with export handling for Google Workspace files

To enable it, see the [Google OAuth Setup](#google-oauth-setup-optional) section below.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React SPA)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   App.tsx   │  │  FileCard   │  │  DriveFilePicker    │  │
│  │  (routing,  │  │  (display,  │  │  (upload/import     │  │
│  │   state)    │  │   actions)  │  │   modal)            │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         └────────────────┼───────────────────┘              │
│                          ▼                                   │
│                 ┌─────────────────┐                          │
│                 │   api.ts        │                          │
│                 │  (API client)   │                          │
│                 └────────┬────────┘                          │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP/JSON
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    Backend (Flask)                            │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                    app.py                             │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │    │
│  │  │ Auth API   │  │ Files API  │  │ Drive API      │  │    │
│  │  │ /auth/*    │  │ /files/*   │  │ /drive/*       │  │    │
│  │  └────────────┘  └────────────┘  └────────────────┘  │    │
│  └──────────────────────────┬───────────────────────────┘    │
│                             ▼                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  SQLAlchemy ORM + SQLite Database                     │    │
│  │  - File metadata (name, size, mime_type, source)      │    │
│  │  - Prevents path traversal by using internal IDs      │    │
│  └──────────────────────────────────────────────────────┘    │
│                             │                                 │
│                             ▼                                 │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Local Filesystem (backend/uploads/)                  │    │
│  │  - UUID-prefixed filenames for uniqueness             │    │
│  │  - Secure filename sanitization                       │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Model

```sql
-- files table
CREATE TABLE files (
    id INTEGER PRIMARY KEY,           -- Internal ID (used in URLs)
    name VARCHAR(500) NOT NULL,       -- Original filename
    mime_type VARCHAR(255),           -- Content type
    size BIGINT,                      -- Size in bytes
    source_id VARCHAR(255) UNIQUE,    -- External ID (upload UUID or Drive file ID)
    source_type VARCHAR(50),          -- 'upload' | 'mock_drive' | 'google_drive'
    local_path VARCHAR(1000),         -- Server filesystem path (not exposed to client)
    created_at DATETIME               -- Import timestamp
);
```

**Design Decisions:**
- `source_id` is unique to prevent duplicate imports from the same source
- `local_path` is never exposed to frontend (security measure)
- File access is only through internal `id` (prevents enumeration attacks)
- `source_type` tracks file origin for audit purposes

---

## API Reference

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/status` | Check if authenticated |
| GET | `/api/auth/login` | Initiate login flow |
| POST | `/api/auth/logout` | End session |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/files` | List all files in data room |
| GET | `/api/files/:id` | View/download file |
| DELETE | `/api/files/:id` | Delete file from data room |
| GET | `/api/files/search?q=term` | Search by filename |
| POST | `/api/upload` | Upload file (multipart/form-data) |

### External Import (Google Drive / Mock)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/drive/files` | List available files to import |
| POST | `/api/drive/import` | Import selected file into data room |

---

## Design Decisions

### 1. Local File Storage

**Implementation:** Files are stored on the server filesystem with UUID-prefixed names.

**Alternatives Considered:**
- Cloud storage (S3, GCS) - Would add external dependencies and costs
- Database blob storage - Poor performance for large files

**Security Measures:**
- Extension whitelist (pdf, doc, xlsx, ppt, txt, csv, images, zip)
- Secure filename sanitization via Werkzeug
- UUID prefix prevents naming collisions
- Internal IDs in URLs prevent path traversal

### 2. Dual Backend Architecture

The project includes two backend implementations:

| File | Purpose | When to Use |
|------|---------|-------------|
| `backend/app.py` | Full Flask server with SQLite | Local development |
| `api/index.py` | Serverless function (stdlib only) | Vercel deployment |

This allows:
- Rich local development experience with database persistence
- Zero-dependency production deployment on Vercel

### 3. Component Architecture

React components follow a clear separation of concerns:
- **App.tsx** - Application state, routing, and layout
- **FileCard** - Stateless display component for individual files
- **DriveFilePicker** - Complex modal with tabs for upload/import
- **api.ts** - Centralized API client with TypeScript interfaces

### 4. Edge Case Handling

- **Expired OAuth tokens**: Architecture supports token refresh (mock simulates this)
- **Duplicate imports**: `source_id` uniqueness prevents re-importing same file
- **Large files**: 50MB limit with streaming upload support
- **Invalid file types**: Whitelist-based validation before storage

---

## Security Considerations

1. **File Upload Validation**
   - Extension whitelist (no executables, scripts, or dangerous formats)
   - 50MB size limit enforced
   - MIME type verification on upload

2. **Path Traversal Prevention**
   - Files accessed by internal ID only
   - `local_path` never exposed to frontend
   - `werkzeug.secure_filename()` sanitizes all filenames

3. **SQL Injection Protection**
   - SQLAlchemy ORM with parameterized queries
   - No raw SQL in the application

4. **CORS Configuration**
   - Restricted to frontend origin only
   - Credentials supported for session management

---

## Google OAuth Setup (Optional)

To enable real Google Drive integration instead of mock data:

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "Acme Data Room")
3. Enable the **Google Drive API** under APIs & Services > Library

### 2. Configure OAuth Consent Screen
1. Navigate to **APIs & Services > OAuth consent screen**
2. Select **External** user type
3. Fill in required fields:
   - App name: "Acme Data Room"
   - User support email: your email
   - Developer contact: your email
4. Add scopes: `https://www.googleapis.com/auth/drive.readonly`
5. Add test users (your Google account)

### 3. Create OAuth Credentials
1. Go to **APIs & Services > Credentials**
2. Click **Create Credentials > OAuth client ID**
3. Application type: **Web application**
4. Name: "Acme Data Room Local"
5. Authorized redirect URIs: `http://localhost:5001/api/auth/callback`
6. Copy the **Client ID** and **Client Secret**

### 4. Configure Environment
Create `backend/.env`:
```env
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
SECRET_KEY=generate-a-random-secure-key-here
FRONTEND_URL=http://localhost:5173
```

### 5. Enable Real OAuth in Code
The file `backend/google_auth.py` contains the complete implementation. To activate:

1. In `backend/app.py`, import the Google auth functions:
   ```python
   from google_auth import create_oauth_flow, get_drive_service, list_drive_files
   ```

2. Replace the mock auth endpoints with real OAuth flow
3. Update `/api/drive/files` to call `list_drive_files()`

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI library with hooks |
| TypeScript | 5.x | Type safety |
| Vite | 7.x | Build tool with HMR |
| Tailwind CSS | 4.x | Utility-first styling |
| Lucide React | - | Icon library |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.x | Web framework |
| SQLAlchemy | 2.x | Database ORM |
| SQLite | - | Local database |
| Flask-CORS | - | Cross-origin requests |

---

## Project Structure

```
dataroom-acme/
├── backend/
│   ├── app.py              # Main Flask application (343 lines)
│   ├── models.py           # SQLAlchemy File model
│   ├── config.py           # Configuration management
│   ├── google_auth.py      # Real OAuth implementation (ready to use)
│   ├── requirements.txt    # Python dependencies
│   └── uploads/            # File storage directory
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main component (200 lines)
│   │   ├── main.tsx        # Entry point
│   │   ├── components/
│   │   │   ├── FileCard.tsx      # File display card
│   │   │   ├── DriveFilePicker.tsx # Upload/import modal
│   │   │   └── Button.tsx        # Reusable button
│   │   └── lib/
│   │       ├── api.ts      # API client (type-safe)
│   │       └── utils.ts    # Utility functions
│   ├── package.json
│   └── vite.config.ts
│
├── api/                    # Vercel serverless deployment
│   └── index.py            # Stdlib-only API handler
│
├── vercel.json             # Vercel configuration
└── README.md
```

---

## What I Would Add With More Time

1. **Folder Organization** - Nested folder structure with drag-and-drop
2. **File Preview** - Inline PDF/image viewer without download
3. **User Authentication** - Multi-user support with role-based permissions
4. **Audit Logging** - Track all file operations with timestamps
5. **Batch Operations** - Select multiple files for bulk delete/download
6. **Real-time Updates** - WebSocket for multi-user collaboration

---

## Running Tests

```bash
# Backend (if tests were added)
cd backend
pytest

# Frontend (if tests were added)
cd frontend
npm test
```

---

## Deployment

### Vercel (Recommended for Demo)
The project is configured for Vercel deployment:
```bash
vercel
```

### Manual Deployment
1. Build frontend: `cd frontend && npm run build`
2. Serve `frontend/dist` as static files
3. Run Flask with Gunicorn: `gunicorn -w 4 app:app`

---

## License

MIT
