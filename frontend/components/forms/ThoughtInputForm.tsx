'use client'

import { useState, FormEvent, KeyboardEvent } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui'

interface ThoughtInputFormProps {
  onSubmit: (thought: string) => void
  onClear: () => void
  isLoading?: boolean
}

export default function ThoughtInputForm({ 
  onSubmit, 
  onClear, 
  isLoading = false 
}: ThoughtInputFormProps) {
  const [thought, setThought] = useState('')
  const maxLength = 1000

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (thought.trim() && !isLoading) {
      onSubmit(thought.trim())
      setThought('')
    }
  }

  const handleClear = () => {
    setThought('')
    onClear()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && thought.trim() && !isLoading) {
      e.preventDefault()
      onSubmit(thought.trim())
      setThought('')
    }
  }

  const isSubmitDisabled = !thought.trim() || isLoading

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto space-y-4">
      <div className="space-y-2">
        <label 
          htmlFor="thought-input" 
          className="block text-sm font-medium text-gray-700 dark:text-gray-200"
        >
          What&apos;s on your mind?
        </label>
        <textarea
          id="thought-input"
          value={thought}
          onChange={(e) => setThought(e.target.value.slice(0, maxLength))}
          onKeyDown={handleKeyDown}
          placeholder="Describe the thought, feeling, or situation that's troubling you..."
          className={cn(
            "input-base",
            "min-h-[120px] resize-y",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
          disabled={isLoading}
          maxLength={maxLength}
          aria-describedby="character-count"
          required
        />
        <div 
          id="character-count" 
          className="text-sm text-gray-500 dark:text-gray-400 text-right"
          aria-live="polite"
        >
          {thought.length} / {maxLength}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          type="submit"
          disabled={isSubmitDisabled}
          loading={isLoading}
          variant="primary"
          size="medium"
          className="flex-1 sm:flex-none"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Thought'}
        </Button>
        <Button
          type="button"
          onClick={handleClear}
          disabled={isLoading}
          variant="secondary"
          size="medium"
        >
          Clear
        </Button>
      </div>

      {isLoading && (
        <div 
          className="text-sm text-gray-600 dark:text-gray-400 text-center"
          role="status"
          aria-live="polite"
        >
          Processing your thought...
        </div>
      )}
    </form>
  )
}