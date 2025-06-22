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
      setResponse('Your thought has been analyzed. Here are some alternative perspectives to consider based on CBT principles.')
    }, 2000)
  }

  const handleClear = () => {
    setResponse(null)
  }

  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-ui-bg-100 to-transparent dark:from-ui-bg-900 dark:to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-700 dark:text-brand-green-400">
                re-frame
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
          {/* Welcome section with warm messaging */}
          <section className="max-w-3xl mx-auto text-center mb-12 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mb-6">
              Reframe your thoughts
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 mb-4 leading-relaxed">
              We use <strong>CBT</strong> (Cognitive Behavioural Therapy) techniques to highlight unhelpful thought patterns.
            </p>
            <p className="text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
              <span className="text-sm">New to CBT? <a href="/learn-cbt" className="text-brand-green-600 dark:text-brand-green-400 underline hover:text-brand-green-700 dark:hover:text-brand-green-300">Get a 2-minute overview</a>.</span>
            </p>
          </section>

          {/* Form section with organic card shape */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              
              <div className="relative bg-surface dark:bg-surface rounded-2xl shadow-lg border border-border-light dark:border-border-dark p-8 md:p-10" style={{ 
                boxShadow: '0 0 24px rgba(74, 107, 87, 0.1)',
                animation: 'fadeIn 250ms cubic-bezier(0.25, 0.1, 0.25, 1)'
              }}>
                <h3 className="text-xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mb-2">
                  Share your thought
                </h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-8">
                  Describe a situation or thought that you&apos;d like to examine.
                </p>
              
              <ThoughtInputForm 
                onSubmit={handleSubmit}
                onClear={handleClear}
                isLoading={isLoading}
              />

                {response && (
                  <div className="mt-8 p-6 bg-ui-bg-50 dark:bg-ui-bg-900 border border-ui-border-light dark:border-ui-border-dark rounded-xl animate-fade-in">
                    <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed">
                      {response}
                    </p>
                  </div>
                )}

                <p className="mt-6 text-sm text-neutral-500 text-center">
                  Private session. No personal data stored.
                </p>
              </div>
            </div>
          </section>

          {/* How it works section with gentle illustrations */}
          <section className="max-w-3xl mx-auto mt-16 space-y-12">
            <div className="text-center">
              <h3 className="text-2xl font-heading font-medium text-neutral-800 dark:text-neutral-100 mb-12">
                How re-frame works
              </h3>
              <div className="grid md:grid-cols-3 gap-8 mt-6">
                {/* Step 1 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-500 dark:bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">1</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-neutral-800 dark:text-neutral-100 mb-3">
                    Describe what happened
                  </h4>
                  <p className="text-base text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    Use your own words. Take the time you need.
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-500 dark:bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">2</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-neutral-800 dark:text-neutral-100 mb-3">
                    Spot common thinking traps
                  </h4>
                  <p className="text-base text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    We&apos;ll apply CBT principles to highlight alternative perspectives.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-500 dark:bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">3</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-neutral-800 dark:text-neutral-100 mb-3">
                    Choose a perspective that feels true
                  </h4>
                  <p className="text-base text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    Select from alternative ways to view your situation.
                  </p>
                </div>
              </div>
            </div>

            {/* Trust message */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-warm-sand/20 via-soft-sky/20 to-breathing-mint/20 dark:from-warm-sand/10 dark:via-soft-sky/10 dark:to-breathing-mint/10 rounded-2xl blur-2xl" />
              <div className="relative border-t border-b border-neutral-200 dark:border-neutral-800 py-8">
                <p className="text-center text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto leading-relaxed">
                  <span className="block text-lg font-heading font-medium text-brand-green-600 dark:text-brand-green-400 mb-3">
                    Designed for people living with AvPD & social anxiety
                  </span>
                  This tool uses evidence-based CBT techniques. Your privacy is protected - 
                  we don&apos;t store any personal information.
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-ui-border-light dark:border-ui-border-dark">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-700 dark:text-brand-green-400">
              re-frame
            </h2>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    Privacy
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    Support
                  </a>
                </li>
                <li>
                  <a 
                    href="#" 
                    className="text-neutral-600 dark:text-neutral-400 hover:text-brand-green-600 dark:hover:text-brand-green-400 transition-colors"
                  >
                    About
                  </a>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-neutral-500 dark:text-neutral-500">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
