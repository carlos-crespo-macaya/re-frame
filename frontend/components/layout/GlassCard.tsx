import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  variant?: 'glass' | 'elevated'
  interactive?: boolean
}

export function GlassCard({
  children,
  className = '',
  padding = 'lg',
  variant = 'glass',
  interactive = false
}: GlassCardProps) {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-12'
  }

  const baseClasses = cn(
    "rounded-[24px] relative transition-all duration-300",
    paddingClasses[padding],
    interactive && "hover:translate-y-[-2px] hover:backdrop-blur-[16px] cursor-pointer",
    className
  )

  if (variant === 'elevated') {
    return (
      <div
        className={cn(
          baseClasses,
          "bg-[#131e24] ring-1 ring-[#2dd4bf]/5 shadow-inner"
        )}
      >
        {children}
      </div>
    )
  }

  return (
    <div
      className={cn(
        baseClasses,
        "backdrop-blur-[12px] ring-1 ring-white/5"
      )}
      style={{
        background: 'rgba(8, 20, 28, 0.55)',
      }}
    >
      {children}
    </div>
  )
}
