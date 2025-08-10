import * as React from 'react'

interface ThumbsDownIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string
}

export function ThumbsDownIcon({ className = "w-6 h-6", ...props }: ThumbsDownIconProps) {
  return (
    <svg 
      className={className}
      viewBox="0 0 24 24" 
      fill="currentColor"
      {...props}
    >
      <path d="M2 2h4v12H2zM22 9c0 .55-.45 1-1 1h-6.31l1.1 5.27.03.32c0 .41-.17.79-.44 1.06L14 20l-6.41-6.41C7.22 13.22 7 12.7 7 12.17V2c0-.55.45-1 1-1h9c.4 0 .75.24.91.59l3 7c.06.13.09.27.09.41v2z" />
    </svg>
  )
}