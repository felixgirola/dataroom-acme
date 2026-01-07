/**
 * File Picker Component
 * 
 * A modal dialog with two tabs:
 * 1. Upload: Direct file upload from your computer
 * 2. Demo Library: Mock "Drive" files for demo purposes
 * 
 * This replaces the Google Drive picker with a simplified,
 * dependency-free alternative.
 */

import { useState, useEffect, useRef } from 'react'
import { X, Search, Import, Loader2, Upload, FolderOpen, Check } from 'lucide-react'
import { api, type DriveFile } from '../lib/api'
import { cn, formatFileSize, getFileIcon } from '../lib/utils'
import { Button } from './Button'

interface DriveFilePickerProps {
  onClose: () => void
  onImport: () => void
}

type TabType = 'upload' | 'library'

export function DriveFilePicker({ onClose, onImport }: DriveFilePickerProps) {
  const [activeTab, setActiveTab] = useState<TabType>('upload')
  
  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  // Library (mock Drive) state
  const [files, setFiles] = useState<DriveFile[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const [importing, setImporting] = useState(false)

  // Fetch mock Drive files when library tab is shown
  useEffect(() => {
    if (activeTab === 'library') {
      fetchFiles()
    }
  }, [activeTab])

  const fetchFiles = async (query?: string) => {
    setLoading(true)
    try {
      const result = await api.listDriveFiles(undefined, query)
      setFiles(result.files || [])
    } catch (error) {
      console.error('Failed to fetch files:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchFiles(searchQuery)
  }

  const toggleSelect = (fileId: string) => {
    const newSelected = new Set(selectedFiles)
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId)
    } else {
      newSelected.add(fileId)
    }
    setSelectedFiles(newSelected)
  }

  /**
   * Handle direct file upload
   */
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files
    if (!fileList || fileList.length === 0) return

    setUploading(true)
    setUploadProgress([])
    
    const filesToUpload = Array.from(fileList)
    
    for (const file of filesToUpload) {
      try {
        setUploadProgress(prev => [...prev, `Uploading ${file.name}...`])
        await api.uploadFile(file)
        setUploadProgress(prev => 
          prev.map(p => p === `Uploading ${file.name}...` ? `✓ ${file.name}` : p)
        )
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error)
        setUploadProgress(prev => 
          prev.map(p => p === `Uploading ${file.name}...` ? `✗ ${file.name} (failed)` : p)
        )
      }
    }
    
    setUploading(false)
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    
    // Notify parent and close after a short delay
    setTimeout(() => {
      onImport()
      onClose()
    }, 1000)
  }

  /**
   * Import selected mock Drive files
   */
  const handleImport = async () => {
    const filesToImport = files.filter((f) => selectedFiles.has(f.id))
    if (filesToImport.length === 0) return

    setImporting(true)
    let successCount = 0
    let errorCount = 0

    for (const file of filesToImport) {
      try {
        await api.importFile(file)
        successCount++
      } catch {
        errorCount++
      }
    }

    setImporting(false)
    
    if (errorCount > 0) {
      alert(`Imported ${successCount} file(s). ${errorCount} file(s) failed or already exist.`)
    }
    
    onImport()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[hsl(var(--border))]">
          <h2 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Add Files
          </h2>
          <button 
            onClick={onClose} 
            className="p-2 hover:bg-[hsl(var(--secondary))] rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-[hsl(var(--border))]">
          <button
            onClick={() => setActiveTab('upload')}
            className={cn(
              'flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2',
              activeTab === 'upload'
                ? 'text-[hsl(var(--primary))] border-b-2 border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
            )}
          >
            <Upload className="w-4 h-4" />
            Upload Files
          </button>
          <button
            onClick={() => setActiveTab('library')}
            className={cn(
              'flex-1 px-4 py-3 text-sm font-medium transition-colors flex items-center justify-center gap-2',
              activeTab === 'library'
                ? 'text-[hsl(var(--primary))] border-b-2 border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]'
            )}
          >
            <FolderOpen className="w-4 h-4" />
            Demo Library
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          {activeTab === 'upload' ? (
            // Upload Tab
            <div className="p-6">
              <div
                className={cn(
                  'border-2 border-dashed rounded-xl p-8 text-center transition-colors',
                  'border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]',
                  'hover:bg-[hsl(var(--primary))]/5'
                )}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                  id="file-upload"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.jpg,.jpeg,.png,.gif,.zip"
                />
                
                {uploading ? (
                  <div className="space-y-3">
                    <Loader2 className="w-10 h-10 animate-spin text-[hsl(var(--primary))] mx-auto" />
                    <div className="text-left max-w-sm mx-auto space-y-1">
                      {uploadProgress.map((msg, i) => (
                        <p 
                          key={i} 
                          className={cn(
                            'text-sm',
                            msg.startsWith('✓') ? 'text-green-600' : 
                            msg.startsWith('✗') ? 'text-red-600' : 
                            'text-[hsl(var(--muted-foreground))]'
                          )}
                        >
                          {msg}
                        </p>
                      ))}
                    </div>
                  </div>
                ) : (
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-12 h-12 text-[hsl(var(--muted-foreground))] mx-auto mb-4" />
                    <p className="text-lg font-medium text-[hsl(var(--foreground))] mb-1">
                      Drop files here or click to upload
                    </p>
                    <p className="text-sm text-[hsl(var(--muted-foreground))]">
                      Supports PDF, DOC, XLS, PPT, images, and more
                    </p>
                  </label>
                )}
              </div>
              
              <p className="text-xs text-[hsl(var(--muted-foreground))] text-center mt-4">
                Maximum file size: 50MB
              </p>
            </div>
          ) : (
            // Library Tab (Mock Drive)
            <div className="p-4">
              {/* Search */}
              <div className="flex gap-2 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
                  <input
                    type="text"
                    placeholder="Search demo files..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                    className="w-full pl-10 pr-4 py-2 rounded-lg border border-[hsl(var(--border))] focus:outline-none focus:ring-2 focus:ring-[hsl(var(--primary))] focus:border-transparent"
                  />
                </div>
                <Button onClick={handleSearch} variant="secondary">
                  Search
                </Button>
              </div>

              {/* Demo notice */}
              <div className="bg-[hsl(var(--secondary))] rounded-lg p-3 mb-4 text-sm text-[hsl(var(--muted-foreground))]">
                💡 These are sample files for demo purposes. In a real app, this would connect to Google Drive or another cloud storage.
              </div>

              {/* File list */}
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
                </div>
              ) : files.length === 0 ? (
                <div className="text-center py-12 text-[hsl(var(--muted-foreground))]">
                  No files found
                </div>
              ) : (
                <div className="space-y-2">
                  {files.map((file) => (
                    <label
                      key={file.id}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors',
                        selectedFiles.has(file.id)
                          ? 'bg-[hsl(var(--primary))]/10 border-2 border-[hsl(var(--primary))]'
                          : 'hover:bg-[hsl(var(--secondary))] border-2 border-transparent'
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.id)}
                        onChange={() => toggleSelect(file.id)}
                        className="w-4 h-4 rounded border-[hsl(var(--border))] text-[hsl(var(--primary))] focus:ring-[hsl(var(--primary))]"
                      />
                      
                      <span className="text-2xl">{getFileIcon(file.mimeType)}</span>
                      
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-[hsl(var(--foreground))] truncate">
                          {file.name}
                        </p>
                        <p className="text-sm text-[hsl(var(--muted-foreground))]">
                          {formatFileSize(file.size ? parseInt(file.size) : null)}
                        </p>
                      </div>

                      {selectedFiles.has(file.id) && (
                        <Check className="w-5 h-5 text-[hsl(var(--primary))]" />
                      )}
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t border-[hsl(var(--border))] bg-[hsl(var(--secondary))]/50">
          {activeTab === 'library' ? (
            <>
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                {selectedFiles.size} file(s) selected
              </span>
              <div className="flex gap-2">
                <Button variant="secondary" onClick={onClose}>
                  Cancel
                </Button>
                <Button
                  onClick={handleImport}
                  disabled={selectedFiles.size === 0 || importing}
                >
                  {importing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Importing...
                    </>
                  ) : (
                    <>
                      <Import className="w-4 h-4" />
                      Import Selected
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <>
              <span className="text-sm text-[hsl(var(--muted-foreground))]">
                Upload files from your computer
              </span>
              <Button variant="secondary" onClick={onClose}>
                Close
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
