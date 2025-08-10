import * as React from 'react'

interface FeedbackIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string
}

export function FeedbackIcon({ className = "w-14 h-6", ...props }: FeedbackIconProps) {
  return (
    <svg
      className={`text-white/70 ${className}`}
      viewBox="0 0 56 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.5}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...props}
    >
      <path d="M8 2h40a4 4 0 014 4v7a4 4 0 01-4 4H30l-10 7v-7H8a4 4 0 01-4-4V6a4 4 0 014-4z" />
      {/* Check mark */}
      <path d="M15 9.5l3 3 5-6" strokeWidth={1.5} />
      {/* Slash */}
      <path d="M28 6l0 8" strokeWidth={1.2} opacity={0.5} />
      {/* X mark */}
      <path d="M34 6l6 6M40 6l-6 6" strokeWidth={1.5} />
    </svg>
  )
}