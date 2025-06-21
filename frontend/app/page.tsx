'use client'

import { useState } from 'react'
import ThoughtInputForm from '@/components/forms/ThoughtInputForm'
import { ThemeToggle } from '@/components/ui'

export default function Home() {
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<string | null>(null)

  const handleSubmit = async (thought: string) => {
    setIsLoading(true)
    setResponse(null)
    
    // Simulate API call for now
    // TODO: Replace with actual API call when backend is ready
    console.log('Submitted thought:', thought)
    setTimeout(() => {
      setIsLoading(false)
      setResponse('Thank you for sharing. Backend integration coming soon.')
    }, 2000)
  }

  const handleClear = () => {
    setResponse(null)
  }

  return (
    <>
      {/* Header */}
      <header className="border-b border-neutral-200 dark:border-neutral-800">
        <div className="container-safe py-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100">
                re-frame.social
              </h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                Cognitive reframing support
              </p>
            </div>
            <ThemeToggle className="ml-4" />
          </div>
        </div>
      </header>

      {/* Main content */}
      <main id="main-content" className="flex-1">
        <div className="container-safe py-8 md:py-12">
          {/* Welcome section */}
          <section className="max-w-2xl mx-auto text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 dark:text-neutral-100 mb-4">
              Welcome to re-frame
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-400 mb-2">
              A safe space for cognitive reframing
            </p>
            <p className="text-neutral-600 dark:text-neutral-400">
              We use transparent AI assistance to help you explore different perspectives on challenging situations.
            </p>
          </section>

          {/* Form section */}
          <section className="max-w-2xl mx-auto">
            <div className="bg-white dark:bg-neutral-900 rounded-lg shadow-sm border border-neutral-200 dark:border-neutral-800 p-6 md:p-8">
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">
                Share your thoughts
              </h3>
              
              <ThoughtInputForm 
                onSubmit={handleSubmit}
                onClear={handleClear}
                isLoading={isLoading}
              />

              {response && (
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                  <p className="text-sm text-blue-800 dark:text-blue-200">
                    {response}
                  </p>
                </div>
              )}

              <p className="mt-4 text-sm text-neutral-500 text-center">
                Your privacy is important. We don&apos;t store any personal information.
              </p>
            </div>
          </section>

          {/* Information section */}
          <section className="max-w-2xl mx-auto mt-12 space-y-8">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
                How it works
              </h3>
              <div className="grid md:grid-cols-3 gap-6 text-sm">
                <div className="space-y-2">
                  <div className="text-4xl mb-3" aria-hidden="true">💭</div>
                  <h4 className="font-medium text-neutral-900 dark:text-neutral-100">
                    Share your thoughts
                  </h4>
                  <p className="text-neutral-600 dark:text-neutral-400">
                    Describe a situation that&apos;s causing you distress
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-4xl mb-3" aria-hidden="true">🔍</div>
                  <h4 className="font-medium text-neutral-900 dark:text-neutral-100">
                    AI analysis
                  </h4>
                  <p className="text-neutral-600 dark:text-neutral-400">
                    Our system applies CBT techniques transparently
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-4xl mb-3" aria-hidden="true">💡</div>
                  <h4 className="font-medium text-neutral-900 dark:text-neutral-100">
                    New perspectives
                  </h4>
                  <p className="text-neutral-600 dark:text-neutral-400">
                    Receive alternative viewpoints with clear reasoning
                  </p>
                </div>
              </div>
            </div>

            <div className="border-t border-neutral-200 dark:border-neutral-800 pt-8">
              <p className="text-sm text-neutral-500 text-center">
                Built with care for people with social anxiety and AvPD. 
                Your comfort and privacy are our priorities.
              </p>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-neutral-200 dark:border-neutral-800 mt-auto">
        <div className="container-safe py-6">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-sm text-neutral-600 dark:text-neutral-400">
              © 2024 re-frame.social. All rights reserved.
            </p>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 transition-colors"
                  >
                    Privacy
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 transition-colors"
                  >
                    Terms
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 transition-colors"
                  >
                    About
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </footer>
    </>
  );
}
