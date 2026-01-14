# Acme Data Room

A secure virtual data room for document management during M&A due diligence. Built as a fullstack application with React/TypeScript frontend and Flask/Python backend.

**Live Demo:** [dataroom-acme.vercel.app](https://dataroom-acme.vercel.app)

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

## Features

- **File Upload** - Upload PDFs, documents, spreadsheets, images directly from your computer
- **File Import** - Import files from external sources (simulated Google Drive)
- **File Viewing** - Click any file to view/download in browser
- **File Deletion** - Remove files from the data room
- **Search** - Filter files by name

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
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Dual Backend Design

| File | Purpose | When to Use |
|------|---------|-------------|
| `backend/app.py` | Full Flask server with SQLite | Local development |
| `api/index.py` | Serverless function (stdlib only) | Vercel deployment |

This allows rich local development with database persistence, and zero-dependency production deployment on Vercel.

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

### External Import
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/drive/files` | List available files to import |
| POST | `/api/drive/import` | Import selected file into data room |

## Security

- **File Validation**: Extension whitelist (pdf, doc, xlsx, ppt, txt, csv, images, zip)
- **Size Limit**: 50MB maximum file size
- **Path Traversal Prevention**: Files accessed by internal ID only, `local_path` never exposed
- **Filename Sanitization**: Uses `werkzeug.secure_filename()`
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries

## Tech Stack

**Frontend:** React 19, TypeScript 5, Vite 7, Tailwind CSS 4

**Backend:** Flask 3, SQLAlchemy 2, SQLite

## Project Structure

```
dataroom-acme/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # SQLAlchemy File model
│   ├── config.py           # Configuration management
│   ├── google_auth.py      # Real OAuth implementation (optional)
│   └── uploads/            # File storage directory
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx         # Main component
│   │   ├── components/     # UI components
│   │   └── lib/api.ts      # Type-safe API client
│   └── package.json
│
├── api/
│   └── index.py            # Vercel serverless function
│
└── vercel.json             # Vercel configuration
```

## Deployment

The project is configured for Vercel:

```bash
vercel
```

For manual deployment:
1. Build frontend: `cd frontend && npm run build`
2. Run Flask with Gunicorn: `gunicorn app:app`

## License

MIT
