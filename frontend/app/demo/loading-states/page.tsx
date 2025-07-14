'use client'

import { useState } from 'react'
import { LoadingSpinner, LoadingSkeleton, LoadingOverlay } from '@/components/ui'

export default function LoadingStatesDemo() {
  const [showOverlay, setShowOverlay] = useState(false)

  return (
    <main className="container-safe py-8">
      <h1 className="text-3xl font-bold mb-8">Loading States Demo</h1>

      {/* Loading Spinners */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Loading Spinners</h2>
        <div className="space-y-4">
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Sizes</h3>
            <div className="flex items-center gap-8">
              <LoadingSpinner size="sm" />
              <LoadingSpinner size="md" />
              <LoadingSpinner size="lg" />
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Colors</h3>
            <div className="flex items-center gap-8">
              <LoadingSpinner color="default" />
              <LoadingSpinner color="primary" />
              <div className="bg-gray-800 p-2 rounded">
                <LoadingSpinner color="white" />
              </div>
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">With Custom Labels</h3>
            <div className="space-y-2">
              <LoadingSpinner label="Processing..." />
              <LoadingSpinner label="Saving changes..." />
              <LoadingSpinner label="Hidden label" showLabel={false} />
            </div>
          </div>
        </div>
      </section>

      {/* Loading Skeletons */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Loading Skeletons</h2>
        <div className="space-y-4">
          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Text Variants</h3>
            <div className="space-y-2">
              <LoadingSkeleton variant="text" />
              <LoadingSkeleton variant="title" />
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Paragraph</h3>
            <LoadingSkeleton variant="paragraph" lines={4} />
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Avatar & Card</h3>
            <div className="flex items-start gap-4">
              <LoadingSkeleton variant="avatar" />
              <LoadingSkeleton variant="card" />
            </div>
          </div>

          <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
            <h3 className="font-medium mb-2">Multiple Items</h3>
            <LoadingSkeleton variant="text" count={3} gap="md" />
          </div>
        </div>
      </section>

      {/* Loading Overlay */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">Loading Overlay</h2>
        <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
          <button
            onClick={() => {
              setShowOverlay(true)
              setTimeout(() => setShowOverlay(false), 3000)
            }}
            className="btn-base bg-primary-600 text-white hover:bg-primary-700 px-4 py-2"
          >
            Show Loading Overlay (3 seconds)
          </button>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Click to see a fullscreen loading overlay
          </p>
        </div>

        <div className="mt-4 relative h-32 bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
          <p>This is a contained loading overlay example</p>
          <LoadingOverlay 
            isLoading={showOverlay} 
            variant="contained"
            label="Loading content..."
          />
        </div>
      </section>

      {/* Global Overlay */}
      <LoadingOverlay 
        isLoading={showOverlay} 
        variant="fullscreen"
        label="Please wait..."
      />
    </main>
  )
}