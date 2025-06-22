'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/routing'

export default function LearnCBT() {
  const tCommon = useTranslations('common')
  const t = useTranslations('learn-cbt')
  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <Link href="/" className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-400 hover:text-brand-green-300 transition-colors">
                  {tCommon('site.name')}
                </h1>
              </Link>
              <p className="text-sm text-[#999999] mt-1">
                {tCommon('site.tagline')}
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
              {t('intro.title')}
            </h1>
            
            <p className="text-base text-[#999999] leading-relaxed mb-6">
              {t('intro.content')}
            </p>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('howItWorks.title')}
            </h2>
            
            <p className="text-base text-[#999999] leading-relaxed mb-4">
              {t('howItWorks.description')}
            </p>

            <div className="bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg p-6 mb-6">
              <div className="space-y-3 text-[#999999]">
                <p>→ {t('howItWorks.cycle.thought')}</p>
                <p>→ {t('howItWorks.cycle.feeling')}</p>
                <p>→ {t('howItWorks.cycle.behavior')}</p>
                <p>→ {t('howItWorks.cycle.result')}</p>
              </div>
            </div>

            <p className="text-base text-[#999999] leading-relaxed mb-6">
              {t('howItWorks.breakingCycle')}
            </p>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('techniques.title')}
            </h2>
            
            <div className="space-y-6 mb-8">
              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">{t('techniques.list.cognitive.title')}</h3>
                <p className="text-[#999999]">{t('techniques.list.cognitive.description')}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">{t('techniques.list.evidence.title')}</h3>
                <p className="text-[#999999]">{t('techniques.list.evidence.description')}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">{t('techniques.list.behavioral.title')}</h3>
                <p className="text-[#999999]">{t('techniques.list.behavioral.description')}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">{t('techniques.list.mindfulness.title')}</h3>
                <p className="text-[#999999]">{t('techniques.list.mindfulness.description')}</p>
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('distortions.title')}
            </h2>
            
            <p className="text-base text-[#999999] leading-relaxed mb-4">
              {t('distortions.description')}
            </p>

            <div className="space-y-4 mb-8">
              <div className="pl-4 border-l-2 border-[#3a3a3a]">
                <h3 className="text-base font-semibold text-[#EDEDED]">{t('distortions.list.mindReading.title')}</h3>
                <p className="text-sm text-[#999999] mt-1">{t('distortions.list.mindReading.description')}</p>
              </div>
              <div className="pl-4 border-l-2 border-[#3a3a3a]">
                <h3 className="text-base font-semibold text-[#EDEDED]">{t('distortions.list.catastrophizing.title')}</h3>
                <p className="text-sm text-[#999999] mt-1">{t('distortions.list.catastrophizing.description')}</p>
              </div>
              <div className="pl-4 border-l-2 border-[#3a3a3a]">
                <h3 className="text-base font-semibold text-[#EDEDED]">{t('distortions.list.allOrNothing.title')}</h3>
                <p className="text-sm text-[#999999] mt-1">{t('distortions.list.allOrNothing.description')}</p>
              </div>
              <div className="pl-4 border-l-2 border-[#3a3a3a]">
                <h3 className="text-base font-semibold text-[#EDEDED]">{t('distortions.list.personalization.title')}</h3>
                <p className="text-sm text-[#999999] mt-1">{t('distortions.list.personalization.description')}</p>
              </div>
              <div className="pl-4 border-l-2 border-[#3a3a3a]">
                <h3 className="text-base font-semibold text-[#EDEDED]">{t('distortions.list.filtering.title')}</h3>
                <p className="text-sm text-[#999999] mt-1">{t('distortions.list.filtering.description')}</p>
              </div>
            </div>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('benefits.title')}
            </h2>
            
            <ul className="list-disc list-inside space-y-2 text-[#999999] mb-6 pl-4">
              {t.raw('benefits.list').map((benefit: string, index: number) => (
                <li key={index}>{benefit}</li>
              ))}
            </ul>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('gettingStarted.title')}
            </h2>
            
            <p className="text-base text-[#999999] leading-relaxed mb-6">
              {t('gettingStarted.content')}
            </p>

            <div className="text-center mb-8">
              <Link href="/" className="inline-flex items-center justify-center px-6 py-3 bg-brand-green-500 hover:bg-brand-green-600 text-white rounded-lg transition-colors">
                {t('gettingStarted.cta')}
              </Link>
            </div>

            <h2 className="text-2xl font-semibold text-[#EDEDED] mt-8 mb-4">
              {t('resources.title')}
            </h2>

            <div className="mb-6">
              <h3 className="text-lg font-semibold text-[#EDEDED] mb-3">
                {t('resources.books.title')}
              </h3>
              <ul className="list-disc list-inside space-y-2 text-[#999999] pl-4">
                {t.raw('resources.books.list').map((book: string, index: number) => (
                  <li key={index}>{book}</li>
                ))}
              </ul>
            </div>

            <div className="mt-8 p-6 bg-[#2a2a2a] border border-[#3a3a3a] rounded-lg">
              <p className="text-sm text-[#999999] leading-relaxed">
                {t('resources.note')}
              </p>
            </div>

            <div className="mt-8 text-center">
              <Link href="/" className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                ← {tCommon('actions.back')}
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
              {tCommon('site.name')}
            </h2>
            <p className="text-xs text-[#999999]">
              {tCommon('footer.copyright')}
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}