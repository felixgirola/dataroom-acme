/**
 * API Client for Acme Data Room
 * 
 * This module provides a typed API client for communicating with the Flask backend.
 * All API calls go through the Vite proxy configured in vite.config.ts, so we use
 * relative paths (/api/...) instead of absolute URLs.
 * 
 * The client is organized into logical groups:
 * - Auth: OAuth flow management
 * - Drive: Google Drive file operations
 * - Files: Data room CRUD operations
 * 
 * @author Felix Gabriel Girola
 */

// In production, API calls go through the Render rewrite rules
// In development, they go through the Vite proxy
const API_BASE = '/api'

// ============================================================================
// Type Definitions
// ============================================================================

/**
 * Represents a file stored in the data room
 */
export interface DataroomFile {
  id: number
  name: string
  mime_type: string | null
  size: number | null
  google_drive_id: string
  created_at: string
}

/**
 * Represents a file from Google Drive (before import)
 */
export interface DriveFile {
  id: string
  name: string
  mimeType: string
  size?: string  // Comes as string from the API
  modifiedTime?: string
  iconLink?: string
  thumbnailLink?: string
}

/**
 * Response from the Google Drive list endpoint
 */
export interface DriveListResponse {
  files: DriveFile[]
  nextPageToken?: string
}

// ============================================================================
// API Client
// ============================================================================

export const api = {
  // --------------------------------------------------------------------------
  // Authentication Endpoints
  // --------------------------------------------------------------------------

  /**
   * Check if the user is authenticated with Google Drive.
   * Called on app load to determine whether to show login screen.
   */
  async getAuthStatus(): Promise<{ authenticated: boolean }> {
    const res = await fetch(`${API_BASE}/auth/status`)
    return res.json()
  },

  /**
   * Get the Google OAuth authorization URL.
   * The frontend redirects the user to this URL to start the OAuth flow.
   */
  async getAuthUrl(): Promise<{ auth_url: string }> {
    const res = await fetch(`${API_BASE}/auth/login`)
    return res.json()
  },

  /**
   * Log out by clearing the stored OAuth tokens.
   */
  async logout(): Promise<void> {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST' })
  },

  // --------------------------------------------------------------------------
  // Google Drive Endpoints
  // --------------------------------------------------------------------------

  /**
   * List files from the user's Google Drive.
   * Supports pagination and search filtering.
   * 
   * @param pageToken - Token for fetching the next page of results
   * @param query - Search string to filter files by name
   */
  async listDriveFiles(pageToken?: string, query?: string): Promise<DriveListResponse> {
    const params = new URLSearchParams()
    if (pageToken) params.set('pageToken', pageToken)
    if (query) params.set('query', query)
    
    const res = await fetch(`${API_BASE}/drive/files?${params}`)
    if (!res.ok) throw new Error('Failed to fetch drive files')
    return res.json()
  },

  /**
   * Import a file from Google Drive into the data room.
   * The backend downloads the file and stores it locally.
   * 
   * @param file - The Google Drive file to import
   */
  async importFile(file: DriveFile): Promise<{ success: boolean; file: DataroomFile }> {
    const res = await fetch(`${API_BASE}/drive/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_id: file.id,
        name: file.name,
        mime_type: file.mimeType,
        size: file.size ? parseInt(file.size) : null,
      }),
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.error || 'Failed to import file')
    }
    return res.json()
  },

  // --------------------------------------------------------------------------
  // Data Room File Endpoints
  // --------------------------------------------------------------------------

  /**
   * List all files stored in the data room.
   */
  async listFiles(): Promise<{ files: DataroomFile[] }> {
    const res = await fetch(`${API_BASE}/files`)
    return res.json()
  },

  /**
   * Search files in the data room by name.
   * 
   * @param query - Search string
   */
  async searchFiles(query: string): Promise<{ files: DataroomFile[] }> {
    const res = await fetch(`${API_BASE}/files/search?q=${encodeURIComponent(query)}`)
    return res.json()
  },

  /**
   * Delete a file from the data room.
   * Note: This does NOT delete the file from Google Drive.
   * 
   * @param fileId - Database ID of the file to delete
   */
  async deleteFile(fileId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/files/${fileId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete file')
  },

  /**
   * Get the URL for viewing/downloading a file.
   * 
   * @param fileId - Database ID of the file
   * @returns URL that can be opened in a new tab to view the file
   */
  getFileUrl(fileId: number): string {
    return `${API_BASE}/files/${fileId}`
  },
}
