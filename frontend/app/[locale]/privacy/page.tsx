'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/routing'

export default function Privacy() {
  const t = useTranslations('privacy')
  const tCommon = useTranslations('common')
  
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
                {tCommon('footer.tagline')}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="container-safe py-8 md:py-12">
          <article className="max-w-3xl mx-auto">
            <h1 className="text-[32px] font-semibold text-[#EDEDED] mb-2">
              🔒 {t('page.title')}
            </h1>
            <p className="text-sm text-[#999999] mb-8">
              {t('page.subtitle')}
            </p>

            {/* Intro */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('intro.title')}
              </h2>
              <p className="text-[#999999] leading-relaxed">
                {t('intro.content')}
              </p>
            </section>

            {/* Core Principles */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('principles.title')}
              </h2>
              <ul className="space-y-3 text-[#999999]">
                {(t.raw('principles.list') as string[]).map((principle, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>{principle}</div>
                  </li>
                ))}
              </ul>
            </section>

            {/* Data Collection */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('dataCollection.title')}
              </h2>
              
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">
                  {t('dataCollection.anonymous.title')}
                </h3>
                <p className="text-[#999999] mb-3">
                  {t('dataCollection.anonymous.description')}
                </p>
                <ul className="space-y-2 text-[#999999] pl-6">
                  {(t.raw('dataCollection.anonymous.list') as string[]).map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <div>{item}</div>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">
                  {t('dataCollection.temporary.title')}
                </h3>
                <p className="text-[#999999] mb-3">
                  {t('dataCollection.temporary.description')}
                </p>
                <ul className="space-y-2 text-[#999999] pl-6">
                  {(t.raw('dataCollection.temporary.list') as string[]).map((item, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <div>{item}</div>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* Data Storage */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('dataStorage.title')}
              </h2>
              
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">
                    {t('dataStorage.thoughts.title')}
                  </h3>
                  <p className="text-[#999999]">
                    {t('dataStorage.thoughts.content')}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">
                    {t('dataStorage.analytics.title')}
                  </h3>
                  <p className="text-[#999999]">
                    {t('dataStorage.analytics.content')}
                  </p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-[#EDEDED] mb-2">
                    {t('dataStorage.security.title')}
                  </h3>
                  <p className="text-[#999999]">
                    {t('dataStorage.security.content')}
                  </p>
                </div>
              </div>
            </section>

            {/* Third Parties */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('thirdParties.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('thirdParties.content')}
              </p>
              <ul className="space-y-4 text-[#999999]">
                {(t.raw('thirdParties.list') as Array<{name: string, purpose: string, data: string}>).map((service, index) => (
                  <li key={index}>
                    <strong className="text-[#EDEDED]">{service.name}</strong> - {service.purpose}
                    <br />
                    <span className="text-sm">{service.data}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* Your Rights */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('rights.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('rights.content')}
              </p>
              <ul className="space-y-2 text-[#999999]">
                {(t.raw('rights.list') as string[]).map((right, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>{right}</div>
                  </li>
                ))}
              </ul>
            </section>

            {/* Cookies */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('cookies.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('cookies.content')}
              </p>
              <ul className="space-y-2 text-[#999999]">
                {(t.raw('cookies.list') as string[]).map((cookie, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>{cookie}</div>
                  </li>
                ))}
              </ul>
            </section>

            {/* Contact */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('contact.title')}
              </h2>
              <p className="text-[#999999]">
                {t('contact.content')}
              </p>
              <p className="text-[#999999] mt-2">
                <a href={`mailto:${t('contact.email')}`} className="text-brand-green-400 hover:text-brand-green-300 underline">
                  {t('contact.email')}
                </a>
              </p>
            </section>

            {/* Changes & Compliance */}
            <section className="mb-12">
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                    {t('changes.title')}
                  </h2>
                  <p className="text-[#999999]">
                    {t('changes.content')}
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                    {t('compliance.title')}
                  </h2>
                  <p className="text-[#999999]">
                    {t('compliance.content')}
                  </p>
                </div>
              </div>
            </section>

            <div className="mt-12 text-center">
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