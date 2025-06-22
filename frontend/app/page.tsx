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
      {/* Header with organic wave shape */}
      <header className="relative bg-gradient-to-br from-primary-50 via-secondary-50 to-accent-50 dark:from-surface dark:via-surface-raised dark:to-surface">
        {/* Organic wave SVG */}
        <div className="absolute bottom-0 left-0 right-0 overflow-hidden">
          <svg viewBox="0 0 1440 120" className="w-full h-16 md:h-24 fill-background">
            <path d="M0,64 C240,96 480,32 720,48 C960,64 1200,96 1440,64 L1440,120 L0,120 Z" />
          </svg>
        </div>
        
        <div className="container-safe py-8 relative z-10">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-primary-700 dark:text-primary-400">
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
            <h2 className="text-3xl md:text-4xl font-medium text-neutral-800 dark:text-neutral-100 mb-6">
              Reframe your thoughts
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 mb-4 leading-relaxed">
              This tool uses CBT principles to help you examine thoughts from different perspectives.
            </p>
            <p className="text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
              Share a thought that&apos;s troubling you, and we&apos;ll work through it together using evidence-based techniques.
            </p>
          </section>

          {/* Form section with organic card shape */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              {/* Organic blob background */}
              <div className="absolute -inset-4 bg-gradient-to-r from-primary-100 via-secondary-100 to-accent-100 dark:from-primary-900/20 dark:via-secondary-900/20 dark:to-accent-900/20 rounded-3xl opacity-50 blur-xl animate-breathe" />
              
              <div className="relative bg-surface dark:bg-surface rounded-2xl shadow-lg border border-border-light dark:border-border-dark p-8 md:p-10">
                <h3 className="text-xl font-medium text-neutral-800 dark:text-neutral-100 mb-2">
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
                  <div className="mt-8 p-6 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl animate-fade-in">
                    <p className="text-sm text-primary-800 dark:text-primary-200 leading-relaxed">
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
              <h3 className="text-2xl font-medium text-neutral-800 dark:text-neutral-100 mb-12">
                How re-frame works
              </h3>
              <div className="grid md:grid-cols-3 gap-8">
                {/* Step 1 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-accent-100 to-accent-200 dark:from-accent-800/30 dark:to-accent-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-sm font-semibold text-accent-700 dark:text-accent-300">1</span>
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-secondary-200 dark:bg-secondary-800/50 rounded-full animate-float" style={{ animationDelay: '0.5s' }} />
                  </div>
                  <h4 className="font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    Describe what happened
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    Use your own words. Take the time you need.
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-800/30 dark:to-primary-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-sm font-semibold text-primary-700 dark:text-primary-300">2</span>
                    </div>
                    <div className="absolute -bottom-2 -left-2 w-10 h-10 bg-accent-200 dark:bg-accent-800/50 rounded-full animate-float" style={{ animationDelay: '1s' }} />
                  </div>
                  <h4 className="font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    Spot common thinking traps
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    We&apos;ll apply CBT principles to highlight alternative perspectives.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-secondary-100 to-secondary-200 dark:from-secondary-800/30 dark:to-secondary-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-sm font-semibold text-secondary-700 dark:text-secondary-300">3</span>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary-200 dark:bg-primary-800/50 rounded-full animate-float" style={{ animationDelay: '1.5s' }} />
                  </div>
                  <h4 className="font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    Choose a perspective that feels true
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
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
                  <span className="block text-lg font-medium text-primary-600 dark:text-primary-400 mb-3">
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

      {/* Footer with gentle wave */}
      <footer className="relative mt-auto">
        {/* Organic wave SVG */}
        <svg viewBox="0 0 1440 60" className="w-full h-12 fill-neutral-100 dark:fill-neutral-900">
          <path d="M0,20 C360,60 720,0 1080,30 C1260,45 1380,35 1440,20 L1440,60 L0,60 Z" />
        </svg>
        
        <div className="bg-neutral-100 dark:bg-neutral-900">
          <div className="container-safe py-6">
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
              <p className="text-sm text-neutral-600 dark:text-neutral-400">
                © 2024 re-frame.social
              </p>
              <nav aria-label="Footer navigation">
                <ul className="flex gap-6 text-sm">
                  <li>
                    <a 
                      href="#" 
                      className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
                    >
                      Privacy
                    </a>
                  </li>
                  <li>
                    <a 
                      href="#" 
                      className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
                    >
                      Support
                    </a>
                  </li>
                  <li>
                    <a 
                      href="#" 
                      className="text-neutral-600 dark:text-neutral-400 hover:text-primary-500 dark:hover:text-primary-400 transition-colors"
                    >
                      About our approach
                    </a>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </footer>
    </>
  );
}
