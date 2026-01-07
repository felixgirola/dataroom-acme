/**
 * API Client for Acme Data Room
 * 
 * Simplified version with mock authentication and direct file uploads.
 * No external service dependencies.
 */

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
  source_id: string
  source_type: string
  created_at: string
}

/**
 * Represents a file from the mock "Drive" (simulated external source)
 */
export interface DriveFile {
  id: string
  name: string
  mimeType: string
  size?: string
  modifiedTime?: string
}

/**
 * Response from the mock Drive list endpoint
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
  // Authentication Endpoints (Mock)
  // --------------------------------------------------------------------------

  /**
   * Check if the user is authenticated.
   * In mock mode, this is always true after "login".
   */
  async getAuthStatus(): Promise<{ authenticated: boolean }> {
    const res = await fetch(`${API_BASE}/auth/status`)
    return res.json()
  },

  /**
   * Mock login - no external OAuth required.
   */
  async login(): Promise<{ success: boolean }> {
    const res = await fetch(`${API_BASE}/auth/login`)
    return res.json()
  },

  /**
   * Log out by clearing the session.
   */
  async logout(): Promise<void> {
    await fetch(`${API_BASE}/auth/logout`, { method: 'POST' })
  },

  // --------------------------------------------------------------------------
  // Mock Drive Endpoints (Simulated external file source)
  // --------------------------------------------------------------------------

  /**
   * List files from the mock "Drive".
   * Returns simulated files for demo purposes.
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
   * Import a file from mock "Drive" into the data room.
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
  // Direct File Upload
  // --------------------------------------------------------------------------

  /**
   * Upload a file directly to the data room.
   */
  async uploadFile(file: File): Promise<{ success: boolean; file: DataroomFile }> {
    const formData = new FormData()
    formData.append('file', file)
    
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    })
    
    if (!res.ok) {
      const error = await res.json()
      throw new Error(error.error || 'Failed to upload file')
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
   */
  async searchFiles(query: string): Promise<{ files: DataroomFile[] }> {
    const res = await fetch(`${API_BASE}/files/search?q=${encodeURIComponent(query)}`)
    return res.json()
  },

  /**
   * Delete a file from the data room.
   */
  async deleteFile(fileId: number): Promise<void> {
    const res = await fetch(`${API_BASE}/files/${fileId}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('Failed to delete file')
  },

  /**
   * Get the URL for viewing/downloading a file.
   */
  getFileUrl(fileId: number): string {
    return `${API_BASE}/files/${fileId}`
  },
}
