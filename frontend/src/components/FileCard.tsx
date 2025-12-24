/**
 * FileCard Component
 * 
 * Displays a file from the data room with its metadata and action buttons.
 * Features:
 * - File icon based on MIME type
 * - File name with truncation for long names
 * - Size and date information
 * - Hover actions for view and delete
 * 
 * The card uses a hover reveal pattern for action buttons to keep
 * the UI clean while still making actions easily accessible.
 */

import { Trash2, ExternalLink } from 'lucide-react'
import { cn, formatFileSize, formatDate, getFileIcon } from '../lib/utils'
import { api, type DataroomFile } from '../lib/api'
import { Button } from './Button'

interface FileCardProps {
  /** The file to display */
  file: DataroomFile
  /** Callback when the file is deleted */
  onDelete: () => void
}

export function FileCard({ file, onDelete }: FileCardProps) {
  /**
   * Handle file deletion with confirmation
   */
  const handleDelete = async () => {
    // Confirm before deleting
    if (!confirm(`Delete "${file.name}" from the dataroom?`)) return
    
    try {
      await api.deleteFile(file.id)
      onDelete() // Refresh the file list
    } catch (error) {
      alert('Failed to delete file. Please try again.')
    }
  }

  /**
   * Open the file in a new browser tab
   */
  const handleView = () => {
    window.open(api.getFileUrl(file.id), '_blank')
  }

  return (
    <div
      className={cn(
        // Base card styles
        'group relative bg-white rounded-xl border border-[hsl(var(--border))] p-4',
        // Hover effects
        'hover:shadow-lg hover:border-[hsl(var(--primary))] transition-all duration-200'
      )}
    >
      {/* File info section */}
      <div className="flex items-start gap-3">
        {/* File type icon */}
        <span className="text-3xl" role="img" aria-label="file type">
          {getFileIcon(file.mime_type)}
        </span>
        
        {/* File details */}
        <div className="flex-1 min-w-0">
          <h3 
            className="font-medium text-[hsl(var(--foreground))] truncate" 
            title={file.name}
          >
            {file.name}
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
            {formatFileSize(file.size)} • {formatDate(file.created_at)}
          </p>
        </div>
      </div>
      
      {/* Action buttons - visible on hover */}
      <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button variant="ghost" size="sm" onClick={handleView} title="View file">
          <ExternalLink className="w-4 h-4" />
        </Button>
        <Button variant="ghost" size="sm" onClick={handleDelete} title="Delete file">
          <Trash2 className="w-4 h-4 text-[hsl(var(--destructive))]" />
        </Button>
      </div>
    </div>
  )
}
