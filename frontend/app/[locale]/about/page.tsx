import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { locales } from '@/lib/i18n/config'

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }))
}

export default async function About() {
  const t = await getTranslations()
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
              {t('about.title')}
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              <strong className="text-[#EDEDED]">{t('about.mission')}</strong>
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('about.what_it_is')}</strong> {t('about.what_it_is_desc')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('about.what_it_isnt')}</strong> {t('about.what_it_isnt_desc')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('about.who_builds')}</strong> {t('about.who_builds_desc')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('about.why_open_source')}</strong> {t('about.why_open_source_desc')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Roadmap:</strong> opt-in community peer support, progress journaling, therapist hand-off export.</div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              Questions? Reach me at <a href="mailto:hello@re-frame.social" className="text-[#EDEDED] hover:text-brand-green-400 underline">hello@re-frame.social</a>.
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