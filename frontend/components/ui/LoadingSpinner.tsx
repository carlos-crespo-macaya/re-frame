import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  variant?: 'inline' | 'centered' | 'fullscreen'
  label?: string
  showLabel?: boolean
  color?: 'default' | 'primary' | 'white'
  className?: string
}

export default function LoadingSpinner({
  size = 'md',
  variant = 'inline',
  label = 'Loading...',
  showLabel = true,
  color = 'default',
  className,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
  }

  const colorClasses = {
    default: 'text-gray-500 dark:text-gray-400',
    primary: 'text-primary-600 dark:text-primary-400',
    white: 'text-white',
  }

  const variantClasses = {
    inline: 'inline-flex items-center gap-2',
    centered: 'flex justify-center items-center p-4',
    fullscreen: 'fixed inset-0 flex justify-center items-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50',
  }

  return (
    <div
      role="status"
      aria-busy="true"
      aria-label={label}
      className={cn(variantClasses[variant], className)}
    >
      <svg
        className={cn(
          'motion-safe:animate-spin',
          sizeClasses[size],
          colorClasses[color]
        )}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className={cn(showLabel ? '' : 'sr-only', 'text-sm')}>
        {label}
      </span>
    </div>
  )
}