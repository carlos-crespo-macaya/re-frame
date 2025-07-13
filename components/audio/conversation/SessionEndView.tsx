'use client'

import { Button } from '@/components/ui'
import type { SessionEndViewProps } from './types'

export function SessionEndView({ onNewSession, sessionSummary }: SessionEndViewProps) {
  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    return `${minutes} minute${minutes !== 1 ? 's' : ''}`
  }
  
  return (
    <div className="flex flex-col items-center justify-center p-8 max-w-md mx-auto text-center">
      {/* Thank you message */}
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
          Thank you for sharing today
        </h2>
        <p className="text-neutral-600">
          These perspectives are here to support you whenever you need them.
        </p>
      </div>
      
      {/* Session summary if provided */}
      {sessionSummary && (
        <div className="mb-6 p-4 bg-neutral-50 rounded-lg w-full">
          <h3 className="text-lg font-medium text-neutral-900 mb-3">Session Summary</h3>
          
          <div className="space-y-2 text-sm text-neutral-600">
            <p>Duration: {formatDuration(sessionSummary.duration)}</p>
            <p>{sessionSummary.messageCount} messages exchanged</p>
          </div>
          
          {sessionSummary.insights && sessionSummary.insights.length > 0 && (
            <div className="mt-4">
              <h4 className="font-medium text-neutral-700 mb-2">Key Insights:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-neutral-600">
                {sessionSummary.insights.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* Action button */}
      <Button
        onClick={onNewSession}
        size="large"
        aria-label="Start new session"
      >
        Start New Session
      </Button>
    </div>
  )
}