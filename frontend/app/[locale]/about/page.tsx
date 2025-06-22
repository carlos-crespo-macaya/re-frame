'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/routing'

export default function About() {
  const t = useTranslations('about')
  
  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <Link href="/" className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-400 hover:text-brand-green-300 transition-colors">
                  {t('header.title')}
                </h1>
              </Link>
              <p className="text-sm text-[#999999] mt-1">
                {t('header.subtitle')}
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
              {t('page.title')}
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              <strong className="text-[#EDEDED]">{t('page.mission')}</strong> – {t('page.missionText')}
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('list.whatItIs')}</strong> {t('list.whatItIsText')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('list.whatItIsnt')}</strong> {t('list.whatItIsntText')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('list.whoBuilds')}</strong> {t('list.whoBuildsText')}<strong className="text-[#EDEDED]">{t('list.carlos')}</strong>{t('list.whoBuildsTextEnd')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('list.whyOpenSource')}</strong> {t('list.whyOpenSourceText')}</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">{t('list.roadmap')}</strong> {t('list.roadmapText')}</div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              {t('contact.text')} <a href={`mailto:${t('contact.email')}`} className="text-[#EDEDED] hover:text-brand-green-400 underline">{t('contact.email')}</a>
            </p>

            <div className="mt-12 text-center">
              <Link href="/" className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                {t('footer.return')}
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
              {t('header.title')}
            </h2>
            <p className="text-xs text-[#999999]">
              {t('footer.copyright')}
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}