import * as React from 'react'

interface ThumbsUpIconProps extends React.SVGProps<SVGSVGElement> {
  className?: string
}

export function ThumbsUpIcon({ className = "w-6 h-6", ...props }: ThumbsUpIconProps) {
  return (
    <svg 
      className={className}
      viewBox="0 0 24 24" 
      fill="currentColor"
      aria-hidden="true"
      {...props}
    >
      <path d="M2 10h4v12H2zM22 11c0-.55-.45-1-1-1h-6.31l1.1-5.27.03-.32c0-.41-.17-.79-.44-1.06L14 2 7.59 8.41C7.22 8.78 7 9.3 7 9.83V20c0 .55.45 1 1 1h9c.4 0 .75-.24.91-.59l3-7c.06-.13.09-.27.09-.41v-2z" />
    </svg>
  )
}