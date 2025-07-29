import Link from 'next/link'
import { locales } from '@/lib/i18n/config'

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }))
}

export default function Support() {
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
              🛟 Support
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              <em>re-frame</em> is a <strong className="text-[#EDEDED]">self-help companion</strong>, not a substitute for professional care.
            </p>

            <div className="space-y-8">
              <div>
                <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                  1. In crisis right now?
                </h2>
                <ul className="space-y-2 text-[#999999] pl-6">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>Call your local emergency number, or</div>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div><strong className="text-[#EDEDED]">988</strong> in the US · <strong className="text-[#EDEDED]">Samaritans 116 123</strong> in the UK & ROI · <strong className="text-[#EDEDED]">Teléfono de la Esperanza 717 003 717</strong> in Spain.</div>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>OpenCounseling – International Suicide Hotlines <a href="https://blog.opencounseling.com/suicide-hotlines/" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">https://blog.opencounseling.com/suicide-hotlines/</a></div>
                  </li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                  2. Need a human ear?
                </h2>
                <ul className="space-y-2 text-[#999999] pl-6">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>Chat with a trained listener at <strong className="text-[#EDEDED]">7 Cups</strong> (free).</div>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>Find a therapist via <strong className="text-[#EDEDED]">psychologytoday.com</strong>.</div>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>If the tool triggers distress, pause and ground yourself—see the breathing exercise link in the footer.</div>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>Find a Helpline: <a href="https://findahelpline.com/" className="text-brand-green-400 hover:text-brand-green-300 underline" target="_blank" rel="noopener noreferrer">https://findahelpline.com/</a></div>
                  </li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                  3. Technical issues or feedback?
                </h2>
                <ul className="space-y-2 text-[#999999] pl-6">
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>Email <a href="mailto:support@re-frame.social" className="text-[#EDEDED] hover:text-brand-green-400 underline">support@re-frame.social</a>. This is a solo project maintained with care — I&apos;ll do my best to respond promptly.</div>
                  </li>
                </ul>
              </div>
            </div>

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