'use client'

import { useState } from 'react'
import RootErrorBoundary from '@/components/error/RootErrorBoundary'
import { errorLogger } from '@/lib/error-logger'

// Component that throws an error
const BuggyComponent = ({ shouldCrash }: { shouldCrash: boolean }) => {
  if (shouldCrash) {
    throw new Error('Simulated error for testing error boundary')
  }
  return (
    <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
      <p className="text-green-800 dark:text-green-200">
        Component is working correctly!
      </p>
    </div>
  )
}

// Component that throws async error
const AsyncBuggyComponent = () => {
  const [hasError, setHasError] = useState(false)

  const triggerAsyncError = () => {
    setTimeout(() => {
      setHasError(true)
    }, 1000)
  }

  if (hasError) {
    throw new Error('Simulated async error')
  }

  return (
    <div className="space-y-4">
      <button
        onClick={triggerAsyncError}
        className="btn-base bg-red-600 text-white hover:bg-red-700 px-4 py-2 rounded"
      >
        Trigger Async Error (1 second delay)
      </button>
    </div>
  )
}

export default function ErrorBoundaryDemo() {
  const [shouldCrash, setShouldCrash] = useState(false)
  const [showAsyncComponent, setShowAsyncComponent] = useState(false)
  const [errorCount, setErrorCount] = useState(0)

  const handleError = () => {
    setErrorCount(prev => prev + 1)
  }

  const viewStoredErrors = () => {
    const errors = errorLogger.getStoredErrors()
    console.log('Stored errors:', errors)
    alert(`${errors.length} errors stored in session. Check console for details.`)
  }

  const clearErrors = () => {
    errorLogger.clearStoredErrors()
    alert('Error log cleared')
  }

  return (
    <main className="container-safe py-8">
      <h1 className="text-3xl font-bold mb-8">Error Boundary Demo</h1>

      <div className="space-y-8">
        {/* Error Statistics */}
        <section className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Error Statistics</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Errors caught in this session: <span className="font-bold">{errorCount}</span>
          </p>
          <div className="mt-4 space-x-4">
            <button
              onClick={viewStoredErrors}
              className="btn-base bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded text-sm"
            >
              View Stored Errors
            </button>
            <button
              onClick={clearErrors}
              className="btn-base bg-gray-600 text-white hover:bg-gray-700 px-4 py-2 rounded text-sm"
            >
              Clear Error Log
            </button>
          </div>
        </section>

        {/* Synchronous Error Test */}
        <section className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Synchronous Error Test</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Click the button to simulate a render error. The error boundary will catch it.
          </p>
          
          <RootErrorBoundary onError={handleError}>
            <div className="space-y-4">
              <button
                onClick={() => setShouldCrash(!shouldCrash)}
                className="btn-base bg-red-600 text-white hover:bg-red-700 px-4 py-2 rounded"
              >
                {shouldCrash ? 'Fix Component' : 'Crash Component'}
              </button>
              
              <BuggyComponent shouldCrash={shouldCrash} />
            </div>
          </RootErrorBoundary>
        </section>

        {/* Asynchronous Error Test */}
        <section className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Asynchronous Error Test</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Test error handling for async operations.
          </p>
          
          <button
            onClick={() => setShowAsyncComponent(!showAsyncComponent)}
            className="btn-base bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded mb-4"
          >
            {showAsyncComponent ? 'Hide' : 'Show'} Async Component
          </button>

          {showAsyncComponent && (
            <RootErrorBoundary onError={handleError}>
              <AsyncBuggyComponent />
            </RootErrorBoundary>
          )}
        </section>

        {/* Multiple Error Boundaries */}
        <section className="bg-gray-50 dark:bg-gray-900 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Nested Error Boundaries</h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Each section has its own error boundary, preventing one error from affecting others.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <RootErrorBoundary onError={handleError}>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
                <h3 className="font-medium mb-2">Section A</h3>
                <BuggyComponent shouldCrash={false} />
              </div>
            </RootErrorBoundary>

            <RootErrorBoundary onError={handleError}>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded">
                <h3 className="font-medium mb-2">Section B</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  This section can fail independently
                </p>
              </div>
            </RootErrorBoundary>
          </div>
        </section>

        {/* Instructions */}
        <section className="bg-blue-50 dark:bg-blue-900/20 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">How Error Boundaries Work</h2>
          <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <li>• Error boundaries catch JavaScript errors in child components</li>
            <li>• They log error information and display a fallback UI</li>
            <li>• Users can recover by clicking &quot;Try again&quot;</li>
            <li>• Errors are stored in session storage for debugging</li>
            <li>• In production, errors would be sent to a monitoring service</li>
          </ul>
        </section>
      </div>
    </main>
  )
}