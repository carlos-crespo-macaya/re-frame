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
      setResponse('Thank you for sharing. We hear you, and we\'re here to help you explore new perspectives.')
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
              <h1 className="text-2xl font-rounded font-semibold text-primary-700 dark:text-primary-400 flex items-center gap-2">
                <span className="inline-block animate-float">🌱</span>
                re-frame
              </h1>
              <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
                Your companion for gentle perspective shifts
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
            <h2 className="text-3xl md:text-4xl font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-6">
              Welcome, brave soul 💜
            </h2>
            <p className="text-lg text-neutral-600 dark:text-neutral-300 mb-4 leading-relaxed">
              We&apos;re so glad you&apos;re here. This is your safe space to explore thoughts that feel heavy.
            </p>
            <p className="text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto">
              Together, we&apos;ll gently untangle difficult feelings and discover new ways of seeing things. 
              No judgment, just compassion and support.
            </p>
          </section>

          {/* Form section with organic card shape */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              {/* Organic blob background */}
              <div className="absolute -inset-4 bg-gradient-to-r from-primary-100 via-secondary-100 to-accent-100 dark:from-primary-900/20 dark:via-secondary-900/20 dark:to-accent-900/20 rounded-3xl opacity-50 blur-xl animate-breathe" />
              
              <div className="relative bg-surface dark:bg-surface rounded-2xl shadow-lg border border-border-light dark:border-border-dark p-8 md:p-10">
                <h3 className="text-xl font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-2">
                  What&apos;s on your heart today?
                </h3>
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-8">
                  Take a deep breath. There&apos;s no rush. Share when you&apos;re ready.
                </p>
              
              <ThoughtInputForm 
                onSubmit={handleSubmit}
                onClear={handleClear}
                isLoading={isLoading}
              />

                {response && (
                  <div className="mt-8 p-6 bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl animate-fade-in">
                    <div className="flex gap-3">
                      <span className="text-2xl animate-pulse-soft" aria-hidden="true">💚</span>
                      <p className="text-sm text-primary-800 dark:text-primary-200 leading-relaxed">
                        {response}
                      </p>
                    </div>
                  </div>
                )}

                <p className="mt-6 text-sm text-neutral-500 text-center">
                  <span className="inline-block mr-1" aria-hidden="true">🔒</span>
                  Your thoughts are sacred. We don&apos;t store personal information.
                </p>
              </div>
            </div>
          </section>

          {/* How it works section with gentle illustrations */}
          <section className="max-w-3xl mx-auto mt-16 space-y-12">
            <div className="text-center">
              <h3 className="text-2xl font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-12">
                How we journey together
              </h3>
              <div className="grid md:grid-cols-3 gap-8">
                {/* Step 1 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-accent-100 to-accent-200 dark:from-accent-800/30 dark:to-accent-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-4xl" aria-hidden="true">🤗</span>
                    </div>
                    <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-secondary-200 dark:bg-secondary-800/50 rounded-full animate-float" style={{ animationDelay: '0.5s' }} />
                  </div>
                  <h4 className="font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    Share what&apos;s troubling you
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    In your own words, at your own pace. We&apos;re listening with open hearts.
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-800/30 dark:to-primary-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-4xl" aria-hidden="true">🌟</span>
                    </div>
                    <div className="absolute -bottom-2 -left-2 w-10 h-10 bg-accent-200 dark:bg-accent-800/50 rounded-full animate-float" style={{ animationDelay: '1s' }} />
                  </div>
                  <h4 className="font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    We explore together
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    Using gentle CBT techniques, we&apos;ll help you see things from new angles.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="relative mb-6">
                    <div className="w-24 h-24 mx-auto bg-gradient-to-br from-secondary-100 to-secondary-200 dark:from-secondary-800/30 dark:to-secondary-700/30 rounded-full flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                      <span className="text-4xl" aria-hidden="true">🌈</span>
                    </div>
                    <div className="absolute -top-2 -right-2 w-6 h-6 bg-primary-200 dark:bg-primary-800/50 rounded-full animate-float" style={{ animationDelay: '1.5s' }} />
                  </div>
                  <h4 className="font-rounded font-medium text-neutral-800 dark:text-neutral-100 mb-3">
                    Find new perspectives
                  </h4>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">
                    Discover kinder ways to think about yourself and your experiences.
                  </p>
                </div>
              </div>
            </div>

            {/* Trust message */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-warm-sand/20 via-soft-sky/20 to-breathing-mint/20 dark:from-warm-sand/10 dark:via-soft-sky/10 dark:to-breathing-mint/10 rounded-2xl blur-2xl" />
              <div className="relative border-t border-b border-neutral-200 dark:border-neutral-800 py-8">
                <p className="text-center text-neutral-600 dark:text-neutral-400 max-w-2xl mx-auto leading-relaxed">
                  <span className="block text-lg font-rounded font-medium text-primary-600 dark:text-primary-400 mb-3">
                    Built with love for people with social anxiety and AvPD 
                  </span>
                  Your comfort is our priority. Every feature is designed to help you feel safe, 
                  understood, and empowered on your journey toward self-compassion.
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
                © 2024 re-frame. Made with care and compassion.
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
