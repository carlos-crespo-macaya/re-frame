'use client'

import { useTranslations } from 'next-intl'
import { Link } from '@/i18n/routing'

export default function Support() {
  const t = useTranslations('support')
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
              🛟 {t('page.title')}
            </h1>
            <p className="text-lg text-[#999999] leading-relaxed mb-12">
              {t('page.subtitle')}
            </p>

            {/* Crisis Section */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('crisis.title')}
              </h2>
              <p className="text-[#999999] mb-6">
                {t('crisis.content')}
              </p>
              
              <div className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-6 mb-6">
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-4">
                  {t('crisis.hotlines.title')}
                </h3>
                <ul className="space-y-4">
                  <li>
                    <strong className="text-brand-green-400">{t('crisis.hotlines.us.number')}</strong>
                    <br />
                    <span className="text-[#999999]">{t('crisis.hotlines.us.name')}</span>
                    <br />
                    <span className="text-sm text-[#999999]">{t('crisis.hotlines.us.description')}</span>
                  </li>
                  <li>
                    <strong className="text-brand-green-400">{t('crisis.hotlines.text.number')}</strong>
                    <br />
                    <span className="text-[#999999]">{t('crisis.hotlines.text.name')}</span>
                    <br />
                    <span className="text-sm text-[#999999]">{t('crisis.hotlines.text.description')}</span>
                  </li>
                  <li>
                    <a href={`https://${t('crisis.hotlines.international.link')}`} 
                       className="text-brand-green-400 hover:text-brand-green-300 underline"
                       target="_blank" 
                       rel="noopener noreferrer">
                      {t('crisis.hotlines.international.name')}
                    </a>
                    <br />
                    <span className="text-sm text-[#999999]">{t('crisis.hotlines.international.description')}</span>
                  </li>
                </ul>
              </div>
            </section>

            {/* Therapy Section */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('therapy.title')}
              </h2>
              <p className="text-[#999999] mb-6">
                {t('therapy.content')}
              </p>

              <div className="grid gap-6 mb-8">
                <div className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-4">
                  <h3 className="font-semibold text-[#EDEDED] mb-2">
                    {t('therapy.options.inPerson.title')}
                  </h3>
                  <p className="text-sm text-[#999999]">
                    {t('therapy.options.inPerson.description')}
                  </p>
                </div>
                <div className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-4">
                  <h3 className="font-semibold text-[#EDEDED] mb-2">
                    {t('therapy.options.online.title')}
                  </h3>
                  <p className="text-sm text-[#999999]">
                    {t('therapy.options.online.description')}
                  </p>
                </div>
                <div className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-4">
                  <h3 className="font-semibold text-[#EDEDED] mb-2">
                    {t('therapy.options.group.title')}
                  </h3>
                  <p className="text-sm text-[#999999]">
                    {t('therapy.options.group.description')}
                  </p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-4">
                  {t('therapy.findingHelp.title')}
                </h3>
                <ul className="space-y-2 text-[#999999]">
                  {(t.raw('therapy.findingHelp.tips') as string[]).map((tip, index) => (
                    <li key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <div>{tip}</div>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* Self-Help Section */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-6">
                {t('selfHelp.title')}
              </h2>

              <div className="mb-8">
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-4">
                  {t('selfHelp.books.title')}
                </h3>
                <div className="space-y-4">
                  {(t.raw('selfHelp.books.list') as Array<{title: string, author: string, description: string}>).map((book, index) => (
                    <div key={index} className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-4">
                      <h4 className="font-semibold text-[#EDEDED]">{book.title}</h4>
                      <p className="text-sm text-[#999999]">by {book.author}</p>
                      <p className="text-sm text-[#999999] mt-2">{book.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-[#EDEDED] mb-4">
                  {t('selfHelp.apps.title')}
                </h3>
                <div className="grid gap-4">
                  {(t.raw('selfHelp.apps.list') as Array<{name: string, description: string}>).map((app, index) => (
                    <div key={index} className="flex items-start">
                      <span className="mr-2">•</span>
                      <div>
                        <strong className="text-[#EDEDED]">{app.name}</strong> - {app.description}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            {/* Community Section */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('community.title')}
              </h2>
              <p className="text-[#999999] mb-6">
                {t('community.content')}
              </p>
              <div className="space-y-4">
                {(t.raw('community.list') as Array<{name: string, platform: string, description: string}>).map((community, index) => (
                  <div key={index} className="bg-[#1D1F1E] border border-[#3a3a3a] rounded-lg p-4">
                    <h4 className="font-semibold text-[#EDEDED]">{community.name}</h4>
                    <p className="text-sm text-brand-green-400">{community.platform}</p>
                    <p className="text-sm text-[#999999] mt-2">{community.description}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Tips Section */}
            <section className="mb-12">
              <h2 className="text-xl font-semibold text-[#EDEDED] mb-4">
                {t('tips.title')}
              </h2>
              <ul className="space-y-3 text-[#999999]">
                {(t.raw('tips.list') as string[]).map((tip, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-2">•</span>
                    <div>{tip}</div>
                  </li>
                ))}
              </ul>
            </section>

            {/* Reminder */}
            <section className="bg-gradient-to-r from-brand-green-900/20 to-brand-green-800/20 border border-brand-green-700/30 rounded-lg p-6 mb-12">
              <h2 className="text-lg font-semibold text-brand-green-400 mb-3">
                {t('reminder.title')}
              </h2>
              <p className="text-[#999999]">
                {t('reminder.content')}
              </p>
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