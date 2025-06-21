'use client'

import Link from 'next/link'

interface ErrorFallbackProps {
  error: Error & { digest?: string }
  reset: () => void
}

export default function ErrorFallback({ error, reset }: ErrorFallbackProps) {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="text-center max-w-md">
        <div role="alert">
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            Something went wrong
          </h2>
          <p className="text-neutral-600 dark:text-neutral-400 mb-8">
            We apologize for the inconvenience. This error has been logged and we&apos;ll look into it.
          </p>
        </div>
        
        <div className="space-y-4">
          <button
            onClick={reset}
            className="btn-base bg-primary-600 text-white hover:bg-primary-700 px-6 py-3 rounded-lg focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 transition-colors"
          >
            Try again
          </button>
          <div>
            <Link
              href="/"
              className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 underline focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 rounded px-2 py-1"
            >
              Return to home
            </Link>
          </div>
        </div>
        
        {process.env.NODE_ENV === 'development' && error && (
          <details className="mt-8 text-left">
            <summary className="cursor-pointer text-neutral-500 dark:text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300">
              Error details (development only)
            </summary>
            <pre className="mt-2 whitespace-pre-wrap text-xs bg-neutral-100 dark:bg-neutral-800 p-4 rounded overflow-auto max-h-64">
              {error.message}
              {error.stack && '\n\n' + error.stack}
            </pre>
          </details>
        )}
      </div>
    </main>
  )
}