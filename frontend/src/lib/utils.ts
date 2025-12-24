/**
 * Utility Functions for Acme Data Room
 * 
 * This module contains helper functions used throughout the frontend:
 * - CSS class merging with Tailwind
 * - File size and date formatting
 * - File type icon mapping
 */

import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Merge CSS class names with Tailwind CSS conflict resolution.
 * 
 * This combines clsx for conditional classes with tailwind-merge
 * to properly handle Tailwind class conflicts.
 * 
 * Example:
 *   cn('p-4', 'p-2') // Returns 'p-2' (last padding wins)
 *   cn('text-red-500', isActive && 'text-blue-500')
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a file size in bytes to a human-readable string.
 * 
 * @param bytes - File size in bytes
 * @returns Formatted string like "1.5 MB"
 */
export function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return 'Unknown size'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

/**
 * Format an ISO date string to a human-readable format.
 * 
 * @param dateString - ISO date string
 * @returns Formatted string like "Dec 24, 2024"
 */
export function formatDate(dateString: string | null | undefined): string {
  if (!dateString) return ''
  
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Get an emoji icon for a file based on its MIME type.
 * 
 * This provides visual differentiation for different file types
 * without needing to load additional icon assets.
 * 
 * @param mimeType - MIME type of the file
 * @returns Emoji character representing the file type
 */
export function getFileIcon(mimeType: string | null | undefined): string {
  if (!mimeType) return '📄'
  
  // Check MIME type patterns and return appropriate icon
  if (mimeType.includes('pdf')) return '📕'
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) return '📊'
  if (mimeType.includes('document') || mimeType.includes('word')) return '📝'
  if (mimeType.includes('presentation') || mimeType.includes('powerpoint')) return '📽️'
  if (mimeType.includes('image')) return '🖼️'
  if (mimeType.includes('video')) return '🎬'
  if (mimeType.includes('audio')) return '🎵'
  if (mimeType.includes('zip') || mimeType.includes('archive')) return '📦'
  if (mimeType.includes('folder')) return '📁'
  
  // Default icon for unknown types
  return '📄'
}
