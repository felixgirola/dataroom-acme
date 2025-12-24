/**
 * Button Component
 * 
 * A reusable button component with multiple style variants.
 * Built with Tailwind CSS and designed to match the application's
 * design system using CSS custom properties for theming.
 * 
 * Usage:
 *   <Button variant="primary" size="md" onClick={handleClick}>
 *     Click me
 *   </Button>
 */

import { cn } from '../lib/utils'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style variant */
  variant?: 'primary' | 'secondary' | 'ghost' | 'destructive'
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Button content */
  children: ReactNode
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        // Base styles
        'inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-all',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        
        // Variant styles
        {
          // Primary - main action button
          'bg-[hsl(var(--primary))] text-white hover:bg-[hsl(220,90%,48%)] focus:ring-[hsl(var(--primary))]':
            variant === 'primary',
          
          // Secondary - alternative action
          'bg-[hsl(var(--secondary))] text-[hsl(var(--foreground))] hover:bg-[hsl(220,14%,90%)] focus:ring-[hsl(var(--secondary))]':
            variant === 'secondary',
          
          // Ghost - minimal visual emphasis
          'hover:bg-[hsl(var(--secondary))] focus:ring-[hsl(var(--secondary))]':
            variant === 'ghost',
          
          // Destructive - danger/delete actions
          'bg-[hsl(var(--destructive))] text-white hover:bg-[hsl(0,84%,50%)] focus:ring-[hsl(var(--destructive))]':
            variant === 'destructive',
        },
        
        // Size styles
        {
          'px-3 py-1.5 text-sm': size === 'sm',
          'px-4 py-2 text-sm': size === 'md',
          'px-6 py-3 text-base': size === 'lg',
        },
        
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
