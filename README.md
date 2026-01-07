# Acme Data Room

A secure document repository for due diligence workflows. Self-contained demo application with **no external dependencies** - no Google account, no OAuth, no cloud storage setup required.

## ✨ Features

- 📁 **File Management** - Upload, view, search, and delete documents
- 📤 **Direct Upload** - Upload files from your computer (up to 50MB)
- 📚 **Demo Library** - Sample files to showcase the import workflow
- 🎨 **Modern UI** - Clean, responsive React + Tailwind interface
- ⚡ **Instant Deploy** - One-click Vercel deployment

## 🚀 Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/dataroom-acme)

Or manually:

1. Push this repo to GitHub
2. Import the project in [Vercel](https://vercel.com/new)
3. Deploy - no environment variables needed!

## 🛠️ Local Development

### Prerequisites
- Python 3.10+
- Node.js 20+

### Quick Start

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# → http://localhost:5001

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

## 📁 Project Structure

```
dataroom-acme/
├── api/                 # Vercel serverless functions
│   └── index.py         # API handler (Python stdlib only)
├── backend/             # Local development backend
│   ├── app.py           # Flask server
│   ├── models.py        # SQLAlchemy models
│   └── uploads/         # Uploaded files
├── frontend/            # React + Vite + Tailwind
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── lib/
└── vercel.json          # Vercel deployment config
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/status` | Check auth status (always true in demo) |
| GET | `/api/auth/login` | Mock login |
| POST | `/api/auth/logout` | Clear session |
| GET | `/api/files` | List all files |
| GET | `/api/files/:id` | View/download file |
| DELETE | `/api/files/:id` | Delete file |
| GET | `/api/files/search?q=` | Search files |
| POST | `/api/upload` | Upload file |
| GET | `/api/drive/files` | List demo library files |
| POST | `/api/drive/import` | Import from demo library |

## 📝 Notes

- **Demo Mode**: Authentication is mocked - click "Enter Data Room" to start
- **Vercel Serverless**: Files are stored in memory (reset on cold start)
- **Local Development**: Files persist in `backend/uploads/` with SQLite

## License

MIT
