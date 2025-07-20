'use client'

import Link from 'next/link'

export default function Privacy() {
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
              🔒 Privacy
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              We believe your reflections belong to <strong className="text-[#EDEDED]">you alone</strong>.
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">No tracking pixels, no ads.</strong></div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Anonymous by default.</strong> If you don&apos;t create an account, we store only a random session ID and your text (so the app can respond).</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Optional account = optional data.</strong> Sign up (email or Google) only if you want to save entries across devices.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Delete anytime.</strong> One click in <strong className="text-[#EDEDED]">Settings → Delete data</strong> wipes every entry, vector embedding, and log.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">End-to-end TLS.</strong> Traffic is encrypted in transit; stored text is encrypted at rest.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Open source.</strong> Our code and security model are public so anyone can audit them.</div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              We&apos;ll never sell or share your words. Read the full policy at <strong className="text-[#EDEDED]">re-frame.social/privacy</strong>.
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