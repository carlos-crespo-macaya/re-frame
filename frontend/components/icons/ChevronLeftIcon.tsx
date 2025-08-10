import * as React from 'react'

interface ChevronLeftIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string
}

export function ChevronLeftIcon({ className = "w-6 h-6", ...props }: ChevronLeftIconProps) {
  return (
    <svg 
      className={className}
      fill="none" 
      stroke="currentColor" 
      strokeWidth={1.5} 
      viewBox="0 0 24 24"
      {...props}
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
    </svg>
  )
}