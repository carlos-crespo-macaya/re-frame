'use client'

import { Button } from '@/components/ui'
import { useNaturalConversation } from '@/lib/audio/use-natural-conversation'

interface NaturalConversationProps {
  language?: string
}

export function NaturalConversation({ language = 'en-US' }: NaturalConversationProps) {
  const {
    isActive,
    status,
    error,
    startConversation,
    stopConversation
  } = useNaturalConversation({
    language,
    // Voice mode is audio-only - no transcript display
    onError: (error) => {
      if (process.env.NODE_ENV === 'development') {
        console.error('Conversation error:', error)
      }
    }
  })

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-gray-50 rounded-lg">
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-semibold mb-2">Voice Conversation</h2>
        <p className="text-gray-600">{status}</p>
        {error && (
          <p className="text-red-500 mt-2 text-sm">{error.message}</p>
        )}
      </div>
      
      <Button
        size="large"
        variant={isActive ? 'danger' : 'primary'}
        onClick={isActive ? stopConversation : startConversation}
        className="min-w-[200px]"
      >
        {isActive ? 'Stop Conversation' : 'Start Conversation'}
      </Button>
      
      {isActive && (
        <div className="mt-8 flex items-center space-x-2">
          <div className="animate-pulse flex space-x-1">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          </div>
          <span className="text-sm text-gray-600">Listening...</span>
        </div>
      )}
      
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Speak naturally and pause when you&apos;re done.</p>
        <p>The AI will respond automatically.</p>
      </div>
    </div>
  )
}