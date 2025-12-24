```
     _                         ____        _          ____                       
    / \   ___ _ __ ___   ___  |  _ \  __ _| |_ __ _  |  _ \ ___   ___  _ __ ___  
   / _ \ / __| '_ ` _ \ / _ \ | | | |/ _` | __/ _` | | |_) / _ \ / _ \| '_ ` _ \ 
  / ___ \ (__| | | | | |  __/ | |_| | (_| | || (_| | |  _ < (_) | (_) | | | | | |
 /_/   \_\___|_| |_| |_|\___| |____/ \__,_|\__\__,_| |_| \_\___/ \___/|_| |_| |_|
                                                                                  
                    🇲🇽 Built with ❤️ from Mexico 🇲🇽
```

---

# Acme Data Room

> **Technical Assessment** for **Senior Full Stack Engineer (Python/Flask/React)**
> 
> 📅 Created: December 24, 2025  
> 👨‍💻 Author: **Felix Gabriel Girola**  
> 📍 Location: Mexico City, Mexico 🇲🇽

---

## 📋 Project Overview

A secure **Virtual Data Room** application for document management during M&A due diligence. This project demonstrates a full-stack implementation integrating with Google Drive via OAuth 2.0, allowing users to securely import, view, and manage confidential documents.

### What is a Data Room?

In the world of mergers and acquisitions, a **Data Room** is a secure repository where companies store sensitive documents for review by potential buyers, investors, or partners. Think of it as a fortified Google Drive specifically designed for high-stakes business transactions.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Google OAuth** | Secure authentication with automatic token refresh |
| 📁 **File Browser** | Custom-built Google Drive file picker with search |
| ⬇️ **Smart Import** | Downloads files locally, exports Google Docs to PDF |
| 👁️ **Document Viewer** | View files directly in browser |
| 🔍 **Search** | Filter documents by filename |
| 🗑️ **File Management** | Delete files from the data room |

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  ┌─────────┐ ┌────────────┐ ┌─────────┐ ┌──────┐           │
│  │  React  │ │ TypeScript │ │ Tailwind│ │ Vite │           │
│  │   18    │ │    5.x     │ │   CSS   │ │  7   │           │
│  └─────────┘ └────────────┘ └─────────┘ └──────┘           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│  ┌─────────┐ ┌────────────┐ ┌─────────────┐ ┌──────────┐   │
│  │  Flask  │ │ SQLAlchemy │ │ Google APIs │ │ Python 3 │   │
│  │   3.0   │ │    2.0     │ │   Client    │ │   .9+    │   │
│  └─────────┘ └────────────┘ └─────────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATABASE                               │
│  ┌─────────────────────┐  ┌────────────────────────────┐   │
│  │  SQLite (dev)       │  │  PostgreSQL (production)   │   │
│  └─────────────────────┘  └────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

Before you begin, make sure you have:

- **Python 3.9+** installed
- **Node.js 22+** (or 20.19+)
- A **Google Cloud** account (free tier works perfectly)

### Step 1: Clone & Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Google OAuth

You'll need to create OAuth credentials in Google Cloud Console. Here's how:

<details>
<summary>📖 Click to expand: Google Cloud Setup Guide</summary>

#### 1. Create a Google Cloud Project
1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Click the project dropdown → **New Project**
3. Name it "Acme Data Room" → **Create**

#### 2. Enable Google Drive API
1. Go to **APIs & Services** → **Library**
2. Search "Google Drive API" → **Enable**

#### 3. Configure OAuth Consent Screen
1. Go to **APIs & Services** → **OAuth consent screen**
2. Select **External** → **Create**
3. Fill in:
   - App name: "Acme Data Room"
   - User support email: your email
   - Developer contact: your email
4. Add scopes: `drive.readonly`, `drive.metadata.readonly`
5. Add your email as a **test user**

#### 4. Create Credentials
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Web application**
4. Add redirect URI: `http://localhost:5001/api/auth/callback`
5. **Copy your Client ID and Secret!**

</details>

### Step 3: Set Environment Variables & Run Backend

```bash
# Set your Google OAuth credentials
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"

# Start the backend server
python app.py
```

The backend will be running at `http://localhost:5001`

### Step 4: Setup & Run Frontend

Open a new terminal:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be running at `http://localhost:5173`

### Step 5: Use the Application! 🎉

1. Open http://localhost:5173
2. Click **"Connect Google Drive"**
3. Sign in with your Google account
4. Import files and enjoy!

---

## 📁 Project Structure

```
acme-dataroom/
│
├── 📂 backend/
│   ├── app.py              # Flask application & routes
│   ├── models.py           # Database models (SQLAlchemy)
│   ├── google_auth.py      # OAuth & Drive API helpers
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   └── 📂 uploads/         # Imported files storage
│
├── 📂 frontend/
│   ├── 📂 src/
│   │   ├── App.tsx         # Main React component
│   │   ├── 📂 lib/
│   │   │   ├── api.ts      # Backend API client
│   │   │   └── utils.ts    # Utility functions
│   │   └── 📂 components/
│   │       ├── Button.tsx          # Reusable button
│   │       ├── FileCard.tsx        # File display card
│   │       └── DriveFilePicker.tsx # Google Drive picker
│   ├── index.html
│   └── vite.config.ts      # Vite configuration
│
└── README.md               # You are here! 👋
```

---

## 🔌 API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/auth/status` | Check if user is authenticated |
| `GET` | `/api/auth/login` | Get Google OAuth URL |
| `GET` | `/api/auth/callback` | OAuth callback handler |
| `POST` | `/api/auth/logout` | Clear authentication |

### Google Drive Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/drive/files` | List files from Google Drive |
| `POST` | `/api/drive/import` | Import a file to data room |

### Data Room Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/files` | List all imported files |
| `GET` | `/api/files/:id` | View/download a file |
| `DELETE` | `/api/files/:id` | Delete a file |
| `GET` | `/api/files/search?q=` | Search files by name |

---

## 🎯 Requirements Checklist

| Requirement | Status | Notes |
|-------------|:------:|-------|
| React-based SPA | ✅ | React 18 + TypeScript + Vite |
| Google OAuth UI flow | ✅ | Full OAuth 2.0 with consent screen |
| File picker for Google Drive | ✅ | Custom-built with multi-select & search |
| Import files from Drive | ✅ | Includes Google Docs → PDF export |
| View files in browser | ✅ | Served with proper MIME types |
| Delete files from data room | ✅ | Removes from disk + database |
| Flask/Python backend | ✅ | RESTful API design |
| Database persistence | ✅ | SQLAlchemy with SQLite/PostgreSQL |
| Store files on disk | ✅ | `backend/uploads/` directory |
| Handle expired OAuth tokens | ✅ | Auto-refresh mechanism |
| **Bonus:** Search functionality | ✅ | Filter by filename |

---

## 🧠 Design Decisions

### Why a Custom File Picker?

I built a custom Google Drive file picker instead of using Google's Picker widget because:
- **Better UX control** - Matches our design system perfectly
- **Multi-select support** - Clear visual feedback for batch imports
- **No extra API keys** - Simplifies deployment

### Why Store Files Locally?

Files are downloaded to the server rather than just storing references:
- **Reliable access** - Files available even if Drive connection is lost
- **Future-proof** - Enables search indexing, versioning, permissions
- **Simpler serving** - No Drive API calls needed for viewing

### Token Refresh Strategy

OAuth tokens are automatically refreshed to prevent session interruption:
- Access tokens expire after ~1 hour
- Refresh tokens are stored and used transparently
- Users never need to re-authenticate (unless token is revoked)

---

## 🐛 Troubleshooting

<details>
<summary><strong>❌ "Access blocked: This app's request is invalid"</strong></summary>

Your redirect URI doesn't match. In Google Cloud Console, add exactly:
```
http://localhost:5001/api/auth/callback
```
</details>

<details>
<summary><strong>❌ "Access blocked: App has not completed verification"</strong></summary>

This is normal for development! Make sure:
1. Your app is in "Testing" mode
2. You added your email as a test user in OAuth consent screen
</details>

<details>
<summary><strong>❌ Files not loading from Google Drive</strong></summary>

1. Verify Google Drive API is enabled
2. Check OAuth scopes include `drive.readonly`
3. Look at backend terminal for error messages
</details>

<details>
<summary><strong>❌ Port 5000 in use (macOS)</strong></summary>

Port 5000 is used by AirPlay on macOS. That's why we use port 5001 instead.
</details>

---

## 🚀 Production Deployment (Vercel)

This project is configured for easy deployment on [Vercel](https://vercel.com) (free tier).

### Quick Deploy to Vercel

1. **Push to GitHub**
   ```bash
   cd /path/to/dataroom-acme
   git add .
   git commit -m "Add Vercel deployment config"
   git remote add origin https://github.com/YOUR_USERNAME/dataroom-acme.git
   git push -u origin main
   ```

2. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com) and sign up with GitHub
   - Click **Add New** → **Project**
   - Import your `dataroom-acme` repository
   - Click **Deploy**

3. **Set Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add these variables:
     - `GOOGLE_CLIENT_ID` = your client ID
     - `GOOGLE_CLIENT_SECRET` = your client secret
     - `FRONTEND_URL` = `https://your-project.vercel.app`
   - Redeploy for changes to take effect

4. **Update Google OAuth Redirect URI**
   - In Google Cloud Console → APIs & Services → Credentials
   - Edit your OAuth client and add:
     ```
     https://your-project.vercel.app/api/auth/callback
     ```

5. **Access Your App** 🎉
   - Your app: `https://your-project.vercel.app`

### Alternative: Render Deployment

A `render.yaml` is also included for deployment on Render.com if preferred.

---

## 📊 Environment Variables

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `GOOGLE_CLIENT_ID` | ✅ | - | OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | - | OAuth Client Secret |
| `DATABASE_URL` | ❌ | SQLite | Database connection string |
| `SECRET_KEY` | ❌ | Random | Flask session secret |
| `FRONTEND_URL` | ❌ | localhost:5173 | Frontend URL for CORS |

---

## 📜 License

MIT License - Feel free to use this code for your own projects.

---

<div align="center">

```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   Thank you for reviewing my assessment! 🙏                   ║
║                                                               ║
║   Built with passion for clean code and great UX.            ║
║                                                               ║
║   - Felix Gabriel Girola                                      ║
║     Mexico City 🇲🇽 | December 2025                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

**Questions? Let's connect!**

</div>
