import { cn } from '@/lib/utils'

interface LoadingSkeletonProps {
  variant?: 'text' | 'title' | 'paragraph' | 'avatar' | 'card'
  width?: string | number
  height?: string | number
  className?: string
  lines?: number
  count?: number
  gap?: 'sm' | 'md' | 'lg'
}

export default function LoadingSkeleton({
  variant = 'text',
  width,
  height,
  className,
  lines = 3,
  count = 1,
  gap = 'sm',
}: LoadingSkeletonProps) {
  const variantStyles = {
    text: 'h-4 rounded',
    title: 'h-8 rounded',
    paragraph: 'space-y-2',
    avatar: 'h-12 w-12 rounded-full',
    card: 'h-32 rounded-lg p-4',
  }

  const gapStyles = {
    sm: 'gap-2',
    md: 'gap-4',
    lg: 'gap-6',
  }

  const renderSkeleton = () => {
    if (variant === 'paragraph') {
      return (
        <div
          role="status"
          aria-busy="true"
          aria-label="Loading content"
          className={cn('space-y-2', className)}
          style={{ width, height }}
        >
          {Array.from({ length: lines }).map((_, index) => (
            <div
              key={index}
              className={cn(
                'motion-safe:animate-pulse bg-gray-200 dark:bg-gray-700 h-4 rounded',
                index === lines - 1 && 'w-3/4'
              )}
            />
          ))}
        </div>
      )
    }

    return (
      <div
        role="status"
        aria-busy="true"
        aria-label="Loading content"
        className={cn(variantStyles[variant], className)}
        style={{ width, height }}
      >
        <div className="motion-safe:animate-pulse bg-gray-200 dark:bg-gray-700 w-full h-full rounded-inherit" />
      </div>
    )
  }

  if (count > 1) {
    return (
      <div className={cn('flex flex-col', gapStyles[gap])}>
        {Array.from({ length: count }).map((_, index) => (
          <div key={index}>{renderSkeleton()}</div>
        ))}
      </div>
    )
  }

  return renderSkeleton()
}