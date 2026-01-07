# Acme Data Room

A secure document repository for due diligence workflows. Self-contained demo application with **no external dependencies** - no Google account, no OAuth, no cloud storage setup required.

## 🌐 Live Demo

**[https://dataroom-acme.vercel.app](https://dataroom-acme.vercel.app/)**

## ✨ Features

- 📁 **File Management** - Upload, view, search, and delete documents
- 📤 **Direct Upload** - Upload files from your computer (up to 50MB)
- 📚 **Demo Library** - Sample files to showcase the import workflow
- 🎨 **Modern UI** - Clean, responsive interface with smooth animations
- ⚡ **Serverless** - Runs entirely on Vercel with zero configuration

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VERCEL EDGE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────┐         ┌─────────────────────────────┐  │
│   │   Static Files  │         │   Serverless Functions      │  │
│   │   (frontend/)   │         │   (api/index.py)            │  │
│   │                 │         │                             │  │
│   │  • React SPA    │  ──→    │  • Auth endpoints           │  │
│   │  • Vite build   │  /api/* │  • File CRUD                │  │
│   │  • Tailwind CSS │         │  • Mock Drive library       │  │
│   │                 │         │  • In-memory storage        │  │
│   └─────────────────┘         └─────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Request Flow

1. User visits the app → Vercel serves the React SPA
2. Frontend makes API calls to `/api/*`
3. Vercel routes requests to the Python serverless function
4. Function processes request and returns JSON response

### Data Storage

| Environment | Storage Method |
|-------------|----------------|
| **Vercel (Production)** | In-memory (resets on cold start) |
| **Local Development** | SQLite + filesystem |

---

## 🛠️ Tech Stack

### Frontend

| Technology | Purpose |
|------------|---------|
| **React 18** | UI library with hooks |
| **TypeScript** | Type safety |
| **Vite** | Build tool & dev server |
| **Tailwind CSS** | Utility-first styling |
| **Lucide React** | Icon library |
| **clsx + tailwind-merge** | Class name utilities |

### Backend (Local Development)

| Technology | Purpose |
|------------|---------|
| **Flask 3.x** | Web framework |
| **SQLAlchemy** | ORM for database |
| **SQLite** | Local database |
| **Flask-CORS** | Cross-origin requests |

### Backend (Vercel Production)

| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Runtime |
| **http.server** | Request handling (stdlib) |
| **In-memory dict** | Temporary storage |

*No external Python packages required for production!*

---

## 📁 Project Structure

```
dataroom-acme/
│
├── api/                          # Vercel serverless functions
│   ├── index.py                  # Main API handler (Python stdlib only)
│   └── requirements.txt          # Empty - no dependencies needed
│
├── backend/                      # Local development server
│   ├── app.py                    # Flask application
│   ├── models.py                 # SQLAlchemy models
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Python dependencies
│   └── uploads/                  # Uploaded files (local only)
│
├── frontend/                     # React application
│   ├── src/
│   │   ├── App.tsx               # Main component
│   │   ├── components/
│   │   │   ├── Button.tsx        # Reusable button
│   │   │   ├── FileCard.tsx      # File display card
│   │   │   └── DriveFilePicker.tsx  # Upload/import modal
│   │   └── lib/
│   │       ├── api.ts            # API client
│   │       └── utils.ts          # Utility functions
│   ├── index.html
│   ├── vite.config.ts
│   └── package.json
│
├── vercel.json                   # Vercel deployment config
└── README.md
```

---

## 🔌 API Reference

### Authentication (Mock)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/auth/status` | Returns `{authenticated: true}` |
| `GET` | `/api/auth/login` | Mock login (always succeeds) |
| `POST` | `/api/auth/logout` | Clears session |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/files` | List all files in data room |
| `GET` | `/api/files/:id` | View/download a file |
| `DELETE` | `/api/files/:id` | Delete a file |
| `GET` | `/api/files/search?q=query` | Search files by name |
| `POST` | `/api/upload` | Upload file (multipart/form-data) |

### Demo Library

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/drive/files` | List mock "Drive" files |
| `POST` | `/api/drive/import` | Import file from demo library |

---

## 🚀 Local Development

### Prerequisites

- Python 3.10+
- Node.js 20+

### Setup

```bash
# Clone and enter project
git clone <repo-url>
cd dataroom-acme

# Start backend
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py               # → http://localhost:5001

# Start frontend (new terminal)
cd frontend
npm install
npm run dev                 # → http://localhost:5173
```

### Environment Variables (Optional)

Create `backend/.env`:

```env
SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:5173
```

---

## 📝 Design Decisions

### Why Mock Authentication?

This is a demo/portfolio project. Real authentication would require:
- OAuth provider setup (Google, Auth0, etc.)
- Environment variables and secrets management
- User database and session handling

The mock auth demonstrates the UI/UX flow without external dependencies.

### Why In-Memory Storage on Vercel?

Vercel serverless functions are stateless. Options for persistence:
- **Vercel KV/Postgres** - Adds complexity and cost
- **External database** - Requires setup and credentials
- **In-memory** - Zero config, perfect for demos

For production use, you'd add a database like Supabase, PlanetScale, or Vercel Postgres.

### Why Two Backend Implementations?

| File | Use Case |
|------|----------|
| `api/index.py` | Vercel production (stdlib only) |
| `backend/app.py` | Local development (Flask + SQLite) |

This allows full-featured local development while keeping production deployment simple and dependency-free.

---

## 📄 License

MIT
