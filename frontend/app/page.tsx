'use client'

import { useState } from 'react'
import Link from 'next/link'
import ThoughtInputForm from '@/components/forms/ThoughtInputForm'

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
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-400">
                re-frame
              </h1>
              <p className="text-sm text-[#999999] mt-1">
                Cognitive reframing support
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main id="main-content" className="flex-1">
        <div className="container-safe py-8 md:py-12">
          {/* Welcome section with warm messaging */}
          <section className="max-w-3xl mx-auto text-center mb-12 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-heading font-medium text-[#EDEDED] mb-6">
              Explore a new perspective
            </h2>
            <p className="text-lg text-[#999999] mb-4 leading-relaxed">
              We'll use <strong>CBT</strong>-informed cognitive restructuring to spot thinking patterns and suggest gentler perspectives.
            </p>
            <p className="text-[#999999] max-w-2xl mx-auto">
              <span className="text-sm">Curious about CBT? <a href="/learn-cbt" className="text-brand-green-400 underline hover:text-brand-green-300">Learn the basics in 2 minutes ↗</a></span>
            </p>
          </section>

          {/* Form section with organic card shape */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              
              <div className="relative bg-[#F7F4F2] rounded-2xl shadow-lg border border-[#2a2a2a] p-8 md:p-10" style={{ 
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.1)',
                animation: 'fadeIn 250ms cubic-bezier(0.25, 0.1, 0.25, 1)'
              }}>
                <h3 className="text-xl font-heading font-medium text-neutral-800 mb-2">
                  Tell us about the situation
                </h3>
                <p className="text-sm text-neutral-600 mb-8">
                  A few sentences are enough — share what feels right.
                </p>
              
              <ThoughtInputForm 
                onSubmit={handleSubmit}
                onClear={handleClear}
                isLoading={isLoading}
              />

                {response && (
                  <div className="mt-8 p-6 bg-[#2a2a2a] border border-[#3a3a3a] rounded-xl animate-fade-in">
                    <p className="text-sm text-[#EDEDED] leading-relaxed">
                      {response}
                    </p>
                  </div>
                )}

                <p className="mt-6 text-sm text-neutral-500 text-center">
                  Private session — we don't store personal data.
                </p>
              </div>
            </div>
          </section>

          {/* How it works section with gentle illustrations */}
          <section className="max-w-3xl mx-auto mt-16 space-y-12">
            <div className="text-center">
              <h3 className="text-2xl font-heading font-medium text-[#EDEDED] mb-12">
                How re-frame works
              </h3>
              <div className="grid md:grid-cols-3 gap-8 mt-6">
                {/* Step 1 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">1</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Tell us what happened
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    Use your own words. Take the time you need.
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">2</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Notice thinking patterns
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    We&apos;ll apply CBT principles to highlight alternative perspectives.
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">3</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    Pick a perspective that feels true
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    Select from alternative ways to view your situation.
                  </p>
                </div>
              </div>
            </div>

            {/* Trust message */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-warm-sand/10 via-soft-sky/10 to-breathing-mint/10 rounded-2xl blur-2xl" />
              <div className="relative border-t border-b border-[#3a3a3a] py-8">
                <p className="text-center text-[#999999] max-w-2xl mx-auto leading-relaxed">
                  <span className="block text-lg font-heading font-medium text-brand-green-400 mb-3">
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
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <Link 
                    href="/privacy" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    Privacy
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/support" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    Support
                  </Link>
                </li>
                <li>
                  <Link 
                    href="/about" 
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    About
                  </Link>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-[#999999]">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
