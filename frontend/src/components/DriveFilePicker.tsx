/**
 * DriveFilePicker Component
 * 
 * A modal dialog for browsing and selecting files from Google Drive.
 * This is a custom implementation rather than using Google's Picker widget,
 * giving us more control over the UI and user experience.
 * 
 * Features:
 * - File listing with pagination
 * - Search functionality
 * - Multi-select for batch imports
 * - Filters out folders (only shows files)
 * - Shows file size or "Google Doc" label appropriately
 * 
 * @author Felix Gabriel Girola
 */

import { useState, useEffect } from 'react'
import { X, Search, Import, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { api, type DriveFile } from '../lib/api'
import { cn, formatFileSize, getFileIcon } from '../lib/utils'
import { Button } from './Button'

interface DriveFilePickerProps {
  /** Called when the modal is closed */
  onClose: () => void
  /** Called after successful import to refresh the file list */
  onImport: () => void
}

export function DriveFilePicker({ onClose, onImport }: DriveFilePickerProps) {
  // File list state
  const [files, setFiles] = useState<DriveFile[]>([])
  const [loading, setLoading] = useState(true)
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('')
  
  // Selection state - using Set for O(1) lookups
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  
  // Import state
  const [importing, setImporting] = useState(false)
  
  // Pagination state
  const [nextPageToken, setNextPageToken] = useState<string | undefined>()
  const [prevTokens, setPrevTokens] = useState<string[]>([])

  /**
   * Fetch files from Google Drive
   */
  const fetchFiles = async (pageToken?: string, query?: string) => {
    setLoading(true)
    try {
      const result = await api.listDriveFiles(pageToken, query)
      setFiles(result.files || [])
      setNextPageToken(result.nextPageToken)
    } catch (error) {
      console.error('Failed to fetch drive files:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch files on mount
  useEffect(() => {
    fetchFiles()
  }, [])

  /**
   * Handle search - reset pagination and fetch with query
   */
  const handleSearch = () => {
    setPrevTokens([])
    fetchFiles(undefined, searchQuery)
  }

  /**
   * Navigate to next page of results
   */
  const handleNextPage = () => {
    if (nextPageToken) {
      // Store empty string as placeholder for "first page"
      setPrevTokens([...prevTokens, ''])
      fetchFiles(nextPageToken, searchQuery)
    }
  }

  /**
   * Navigate to previous page of results
   */
  const handlePrevPage = () => {
    if (prevTokens.length > 0) {
      const newPrevTokens = [...prevTokens]
      const token = newPrevTokens.pop()
      setPrevTokens(newPrevTokens)
      fetchFiles(token || undefined, searchQuery)
    }
  }

  /**
   * Toggle file selection
   */
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
   * Import all selected files
   */
  const handleImport = async () => {
    const filesToImport = files.filter((f) => selectedFiles.has(f.id))
    if (filesToImport.length === 0) return

    setImporting(true)
    let successCount = 0
    let errorCount = 0

    // Import files sequentially to avoid overwhelming the server
    for (const file of filesToImport) {
      try {
        await api.importFile(file)
        successCount++
      } catch (error) {
        errorCount++
        console.error(`Failed to import ${file.name}:`, error)
      }
    }

    setImporting(false)
    
    // Show summary if there were errors
    if (errorCount > 0) {
      alert(`Imported ${successCount} file(s). ${errorCount} file(s) failed or already exist.`)
    }
    
    onImport() // Refresh the data room file list
    onClose()
  }

  // Helper functions for MIME type checking
  const isGoogleDoc = (mimeType: string) => 
    mimeType.startsWith('application/vnd.google-apps.')
  
  const isFolder = (mimeType: string) => 
    mimeType === 'application/vnd.google-apps.folder'

  return (
    // Modal backdrop
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      {/* Modal content */}
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl max-h-[80vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[hsl(var(--border))]">
          <h2 className="text-xl font-semibold text-[hsl(var(--foreground))]">
            Import from Google Drive
          </h2>
          <button 
            onClick={onClose} 
            className="p-2 hover:bg-[hsl(var(--secondary))] rounded-lg transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search bar */}
        <div className="p-4 border-b border-[hsl(var(--border))]">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <input
                type="text"
                placeholder="Search files..."
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
        </div>

        {/* File list */}
        <div className="flex-1 overflow-y-auto p-4">
          {loading ? (
            // Loading state
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-[hsl(var(--primary))]" />
            </div>
          ) : files.length === 0 ? (
            // Empty state
            <div className="text-center py-12 text-[hsl(var(--muted-foreground))]">
              No files found
            </div>
          ) : (
            // File list
            <div className="space-y-2">
              {files
                .filter((f) => !isFolder(f.mimeType)) // Filter out folders
                .map((file) => (
                  <label
                    key={file.id}
                    className={cn(
                      'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors',
                      selectedFiles.has(file.id)
                        ? 'bg-[hsl(var(--primary))]/10 border-2 border-[hsl(var(--primary))]'
                        : 'hover:bg-[hsl(var(--secondary))] border-2 border-transparent'
                    )}
                  >
                    {/* Checkbox */}
                    <input
                      type="checkbox"
                      checked={selectedFiles.has(file.id)}
                      onChange={() => toggleSelect(file.id)}
                      className="w-4 h-4 rounded border-[hsl(var(--border))] text-[hsl(var(--primary))] focus:ring-[hsl(var(--primary))]"
                    />
                    
                    {/* File icon */}
                    <span className="text-2xl">{getFileIcon(file.mimeType)}</span>
                    
                    {/* File info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-[hsl(var(--foreground))] truncate">
                        {file.name}
                      </p>
                      <p className="text-sm text-[hsl(var(--muted-foreground))]">
                        {isGoogleDoc(file.mimeType) 
                          ? 'Google Doc' 
                          : formatFileSize(file.size ? parseInt(file.size) : null)}
                      </p>
                    </div>
                  </label>
                ))}
            </div>
          )}
        </div>

        {/* Pagination controls */}
        <div className="flex items-center justify-center gap-2 p-2 border-t border-[hsl(var(--border))]">
          <Button
            variant="ghost"
            size="sm"
            onClick={handlePrevPage}
            disabled={prevTokens.length === 0}
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNextPage}
            disabled={!nextPageToken}
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        {/* Footer with selection count and action buttons */}
        <div className="flex items-center justify-between p-4 border-t border-[hsl(var(--border))] bg-[hsl(var(--secondary))]/50">
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
        </div>
      </div>
    </div>
  )
}
