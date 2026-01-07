/**
 * Acme Data Room - Main Application Component
 * 
 * Simplified version with mock authentication.
 * No external service dependencies (Google, etc.)
 * 
 * Features:
 * - Auto-login (mock auth)
 * - File listing and search
 * - Import from mock "Drive" or direct upload
 */

import { useState, useEffect } from 'react'
import { FolderOpen, Plus, Search, LogOut, Loader2, Upload } from 'lucide-react'
import { api, type DataroomFile } from './lib/api'
import { Button } from './components/Button'
import { FileCard } from './components/FileCard'
import { DriveFilePicker } from './components/DriveFilePicker'

function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null)
  const [files, setFiles] = useState<DataroomFile[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [showPicker, setShowPicker] = useState(false)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const { authenticated } = await api.getAuthStatus()
      setAuthenticated(authenticated)
      if (authenticated) {
        fetchFiles()
      } else {
        setLoading(false)
      }
    } catch {
      setAuthenticated(false)
      setLoading(false)
    }
  }

  const fetchFiles = async () => {
    setLoading(true)
    try {
      const { files } = searchQuery
        ? await api.searchFiles(searchQuery)
        : await api.listFiles()
      setFiles(files)
    } catch (error) {
      console.error('Failed to fetch files:', error)
    } finally {
      setLoading(false)
    }
  }

  /**
   * Mock login - no external OAuth
   */
  const handleLogin = async () => {
    try {
      await api.login()
      setAuthenticated(true)
      fetchFiles()
    } catch {
      alert('Failed to login. Please try again.')
    }
  }

  const handleLogout = async () => {
    await api.logout()
    setAuthenticated(false)
    setFiles([])
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchFiles()
  }

  // Still checking authentication status
  if (authenticated === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[hsl(220,90%,98%)] to-[hsl(220,30%,95%)]">
        <Loader2 className="w-10 h-10 animate-spin text-[hsl(var(--primary))]" />
      </div>
    )
  }

  // Not authenticated - show login screen
  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[hsl(220,90%,98%)] to-[hsl(220,30%,95%)]">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full mx-4 text-center">
          <div className="w-16 h-16 bg-[hsl(var(--primary))]/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <FolderOpen className="w-8 h-8 text-[hsl(var(--primary))]" />
          </div>
          
          <h1 className="text-2xl font-bold text-[hsl(var(--foreground))] mb-2">
            Acme Data Room
          </h1>
          <p className="text-[hsl(var(--muted-foreground))] mb-6">
            Secure document repository for due diligence. Click below to get started.
          </p>
          
          <Button size="lg" onClick={handleLogin} className="w-full">
            <Upload className="w-5 h-5" />
            Enter Data Room
          </Button>
          
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-4">
            Demo mode - no external accounts required
          </p>
        </div>
      </div>
    )
  }

  // Authenticated - show main application
  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(220,90%,98%)] to-[hsl(220,30%,95%)]">
      {/* Header Bar */}
      <header className="bg-white border-b border-[hsl(var(--border))] sticky top-0 z-40">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[hsl(var(--primary))]/10 rounded-xl flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-[hsl(var(--primary))]" />
            </div>
            <h1 className="text-xl font-bold text-[hsl(var(--foreground))]">Acme Data Room</h1>
          </div>
          
          <div className="flex items-center gap-3">
            <form onSubmit={handleSearch} className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 w-64 rounded-lg border border-[hsl(var(--border))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] focus:border-transparent"
              />
            </form>
            
            <Button onClick={() => setShowPicker(true)}>
              <Plus className="w-4 h-4" />
              Add Files
            </Button>
            
            <Button variant="ghost" onClick={handleLogout} title="Sign out">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-10 h-10 animate-spin text-[hsl(var(--primary))]" />
          </div>
        ) : files.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-[hsl(var(--secondary))] rounded-2xl flex items-center justify-center mx-auto mb-6">
              <FolderOpen className="w-10 h-10 text-[hsl(var(--muted-foreground))]" />
            </div>
            <h2 className="text-xl font-semibold text-[hsl(var(--foreground))] mb-2">
              {searchQuery ? 'No files found' : 'No files in your data room'}
            </h2>
            <p className="text-[hsl(var(--muted-foreground))] mb-6">
              {searchQuery
                ? 'Try a different search term'
                : 'Add files by uploading or importing from the demo library'}
            </p>
            {!searchQuery && (
              <Button onClick={() => setShowPicker(true)}>
                <Plus className="w-4 h-4" />
                Add Files
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {files.map((file) => (
              <FileCard key={file.id} file={file} onDelete={fetchFiles} />
            ))}
          </div>
        )}
      </main>

      {/* File Picker Modal */}
      {showPicker && (
        <DriveFilePicker onClose={() => setShowPicker(false)} onImport={fetchFiles} />
      )}
    </div>
  )
}

export default App
