'use client'

import { useState, FormEvent, KeyboardEvent } from 'react'
import { cn } from '@/lib/utils'

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
        <button
          type="submit"
          disabled={isSubmitDisabled}
          className={cn(
            "btn-base flex-1 sm:flex-none",
            "bg-primary-600 text-white hover:bg-primary-700",
            "disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed",
            "dark:disabled:bg-gray-700 dark:disabled:text-gray-500",
            "transition-colors duration-200"
          )}
          aria-busy={isLoading}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Thought'}
        </button>
        <button
          type="button"
          onClick={handleClear}
          disabled={isLoading}
          className={cn(
            "btn-base",
            "bg-gray-200 text-gray-700 hover:bg-gray-300",
            "dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "transition-colors duration-200"
          )}
        >
          Clear
        </button>
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