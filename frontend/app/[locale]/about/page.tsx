'use client'

import Link from 'next/link'

export default function About() {
  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <Link href="/" className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-400 hover:text-brand-green-300 transition-colors">
                  re-frame
                </h1>
              </Link>
              <p className="text-sm text-[#999999] mt-1">
                Cognitive reframing support
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="container-safe py-8 md:py-12">
          <article className="max-w-3xl mx-auto">
            <h1 className="text-[32px] font-semibold text-[#EDEDED] mb-8">
              ℹ️ About re-frame
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              <strong className="text-[#EDEDED]">Mission</strong> – give people who struggle with avoidant patterns a gentle way to challenge harsh thoughts—without shame, ads, or data mining.
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">What it is:</strong> a CBT-informed cognitive-restructuring tool that spots thinking traps (catastrophising, mind-reading, etc.) and offers kinder perspectives.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">What it isn't:</strong> full psychotherapy, medical advice, or a crisis service.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Who builds it:</strong> just me—<strong className="text-[#EDEDED]">Carlos</strong>, a software engineer who's lived with AvPD for years and is investing my own time, skills, and will to create the tool I wish I'd had.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Why open source:</strong> transparency builds trust; anyone can inspect or improve the code.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Roadmap:</strong> opt-in community peer support, progress journaling, therapist hand-off export.</div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              Questions? Reach me at <a href="mailto:macayaven@gmail.com" className="text-[#EDEDED] hover:text-brand-green-400 underline">macayaven@gmail.com</a> or view the roadmap on GitHub → <a href="https://github.com/macayaven/re-frame" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">https://github.com/macayaven/re-frame</a>
            </p>

            <div className="mt-12 text-center">
              <Link href="/" className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                ← Return to re-frame
              </Link>
            </div>
          </article>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <p className="text-xs text-[#999999]">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}