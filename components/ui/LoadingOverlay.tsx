import { ReactNode } from 'react'
import { cn } from '@/lib/utils'
import LoadingSpinner from './LoadingSpinner'

interface LoadingOverlayProps {
  isLoading: boolean
  label?: string
  spinnerSize?: 'sm' | 'md' | 'lg'
  variant?: 'fullscreen' | 'contained' | 'inline'
  blur?: boolean
  className?: string
  zIndex?: string
  opacity?: string
  children?: ReactNode
}

export default function LoadingOverlay({
  isLoading,
  label = 'Loading...',
  spinnerSize = 'md',
  variant = 'fullscreen',
  blur = true,
  className,
  zIndex = 'z-40',
  opacity = 'bg-opacity-50',
  children,
}: LoadingOverlayProps) {
  if (!isLoading) return null

  const variantStyles = {
    fullscreen: 'fixed inset-0',
    contained: 'absolute inset-0',
    inline: 'relative',
  }

  return (
    <div
      className={cn(
        variantStyles[variant],
        'pointer-events-none',
        zIndex,
        className
      )}
    >
      <div
        className={cn(
          'pointer-events-auto',
          'flex items-center justify-center',
          'w-full h-full',
          'bg-white dark:bg-gray-900',
          opacity,
          blur && 'backdrop-blur-sm'
        )}
      >
        <LoadingSpinner
          size={spinnerSize}
          label={label}
          color="primary"
          variant="inline"
        />
      </div>
      {children}
    </div>
  )
}