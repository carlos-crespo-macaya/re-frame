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

  // Status messages based on input length
  const getStatusMessage = () => {
    if (thought.length === 0) return ""
    if (thought.length < 50) return "Continue if you'd like to add more context."
    if (thought.length < 200) return "Good amount of detail."
    if (thought.length < 500) return "Comprehensive description."
    return "Maximum detail captured."
  }

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-6">
      <div className="space-y-3">
        <label 
          htmlFor="thought-input" 
          className="block text-base font-rounded font-medium text-neutral-700 dark:text-neutral-200"
        >
          Describe your thought
        </label>
        <div className="relative">
          <textarea
            id="thought-input"
            value={thought}
            onChange={(e) => setThought(e.target.value.slice(0, maxLength))}
            onKeyDown={handleKeyDown}
            placeholder="What situation or thought would you like to examine?"
            className={cn(
              "w-full min-h-[140px] resize-y rounded-xl",
              "bg-white dark:bg-neutral-900",
              "border-2 border-neutral-200 dark:border-neutral-700",
              "focus:border-primary-400 dark:focus:border-primary-500",
              "focus:ring-4 focus:ring-primary-400/20 dark:focus:ring-primary-500/20",
              "px-5 py-4",
              "text-base text-neutral-800 dark:text-neutral-100",
              "placeholder:text-neutral-400 dark:placeholder:text-neutral-500",
              "transition-all duration-200",
              isLoading && "opacity-60 cursor-not-allowed"
            )}
            disabled={isLoading}
            maxLength={maxLength}
            aria-describedby="character-count encouraging-message"
            required
          />
          {/* Decorative element */}
          <div className="absolute -bottom-2 -right-2 w-16 h-16 bg-gradient-to-br from-primary-200/30 to-secondary-200/30 dark:from-primary-800/20 dark:to-secondary-800/20 rounded-full blur-xl pointer-events-none" />
        </div>
        
        <div className="flex justify-between items-end">
          <p 
            id="encouraging-message"
            className="text-sm text-neutral-600 dark:text-neutral-400 italic"
            aria-live="polite"
          >
            {getStatusMessage()}
          </p>
          <div 
            id="character-count" 
            className="text-sm text-neutral-500 dark:text-neutral-400"
            aria-live="polite"
          >
            {thought.length} / {maxLength}
          </div>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <Button
          type="submit"
          disabled={isSubmitDisabled}
          loading={isLoading}
          variant="primary"
          size="large"
          className="flex-1 sm:flex-none group relative overflow-hidden"
        >
          {isLoading ? (
              <span>Processing...</span>
            ) : (
              <span>Reframe this thought</span>
            )}
        </Button>
        <Button
          type="button"
          onClick={handleClear}
          disabled={isLoading}
          variant="secondary"
          size="large"
          className="group"
        >
          <span className="flex items-center gap-2">
            <span className="group-hover:rotate-180 transition-transform duration-300">
              ↻
            </span>
            <span>Clear</span>
          </span>
        </Button>
      </div>

      {isLoading && (
        <div 
          className="text-center space-y-2"
          role="status"
          aria-live="polite"
        >
          <div className="flex justify-center gap-2">
            <span className="inline-block w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="inline-block w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="inline-block w-2 h-2 bg-accent-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">
            Analyzing your input...
          </p>
        </div>
      )}

      {/* Tip for keyboard shortcut */}
      <p className="text-xs text-neutral-500 dark:text-neutral-400 text-center">
        <kbd className="px-2 py-1 bg-neutral-100 dark:bg-neutral-800 rounded text-xs">Ctrl</kbd> + 
        <kbd className="px-2 py-1 bg-neutral-100 dark:bg-neutral-800 rounded text-xs ml-1">Enter</kbd>
        <span className="ml-2">to submit</span>
      </p>
    </form>
  )
}