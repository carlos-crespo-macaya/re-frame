'use client'

import { useState } from 'react'
import { Button } from './Button'

interface PdfDownloadButtonProps {
  sessionId: string
  className?: string
  disabled?: boolean
}

export function PdfDownloadButton({ sessionId, className, disabled }: PdfDownloadButtonProps) {
  const [isDownloading, setIsDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDownload = async () => {
    setIsDownloading(true)
    setError(null)

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api'
      const response = await fetch(`${apiUrl}/pdf/${sessionId}`)
      
      if (!response.ok) {
        throw new Error('Failed to download summary')
      }

      // Get the blob from the response
      const blob = await response.blob()
      
      // Create a download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `session-summary-${sessionId}.txt`
      
      // Trigger download
      document.body.appendChild(link)
      link.click()
      
      // Cleanup
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Failed to download summary. Please try again.')
      console.error('Summary download error:', err)
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <div className="flex flex-col items-center gap-2">
      <Button
        onClick={handleDownload}
        disabled={disabled || isDownloading}
        variant="secondary"
        className={className}
        aria-label={isDownloading ? 'Downloading summary' : 'Download session summary as text file'}
        aria-busy={isDownloading}
      >
        {isDownloading ? (
          <>
            <span className="inline-block animate-spin mr-2" aria-hidden="true">⏳</span>
            Downloading...
          </>
        ) : (
          <>
            <span className="mr-2" aria-hidden="true">📄</span>
            Download Summary (Text)
          </>
        )}
      </Button>
      
      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
    </div>
  )
}