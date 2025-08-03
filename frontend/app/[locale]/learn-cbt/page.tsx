import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Learn about CBT - re-frame',
  description: 'Learn about Cognitive Behavioral Therapy and how it helps with avoidant patterns'
}

interface LearnCBTPageProps {
  params: { locale: string }
}

export default async function LearnCBTPage({ params }: LearnCBTPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'learn-cbt'})

  return (
    <div className="min-h-screen bg-dark-charcoal">
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8 px-4 sm:px-6 lg:px-8">
          <div>
            <h1 className="text-2xl font-heading font-semibold text-brand-green-400 mb-2">
              re-frame
            </h1>
            <Link 
              href={`/${params.locale}`}
              className="inline-flex items-center text-brand-green-400 hover:text-brand-green-300 transition-colors"
            >
              {t('navigation.return')}
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-safe py-8 md:py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl md:text-4xl font-heading font-medium text-[#EDEDED] mb-4">
              {t('title')}
            </h1>
            <p className="text-sm text-brand-green-400 mb-6">
              {t('quickLink')}
            </p>
            <p className="text-lg text-[#999999] leading-relaxed">
              {t('introduction')}
            </p>
          </div>

          <div className="space-y-8">
            {/* Why it helps with AvPD */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('whyHelpsAvpd.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('whyHelpsAvpd.description')}
              </p>
              <ul className="space-y-2 mb-4">
                {(t.raw('whyHelpsAvpd.tools') as string[]).map((tool, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {tool}
                  </li>
                ))}
              </ul>
              <p className="text-[#999999] italic">
                {t('whyHelpsAvpd.conclusion')}
              </p>
            </section>

            {/* How re-frame uses CBT */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('howWeUse.title')}
              </h2>
              <p className="text-[#999999]">
                {t('howWeUse.description')}
              </p>
            </section>

            {/* Further Reading */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('furtherReading.title')}
              </h2>
              <div className="space-y-4">
                {(t.raw('furtherReading.resources') as any[]).map((resource, index) => (
                  <div key={index} className="border-l-2 border-brand-green-400 pl-4">
                    <h3 className="font-medium text-[#EDEDED]">{resource.title}</h3>
                    <p className="text-sm text-[#999999]">{resource.source}</p>
                    <p className="text-sm text-brand-green-400">{resource.link}</p>
                  </div>
                ))}
              </div>
            </section>

            {/* Reminder */}
            <section className="bg-yellow-900/20 border border-yellow-500/30 rounded-lg p-6">
              <p className="text-[#EDEDED]">
                <span className="font-medium">{t('reminder.prefix')}</span> {t('reminder.text')}
              </p>
            </section>

            {/* References */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('references.title')}
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[#3a3a3a]">
                      <th className="text-left py-2 pr-4 text-[#999999] font-medium">
                        {t('references.tableHeaders.number')}
                      </th>
                      <th className="text-left py-2 px-4 text-[#999999] font-medium">
                        {t('references.tableHeaders.source')}
                      </th>
                      <th className="text-left py-2 pl-4 text-[#999999] font-medium">
                        {t('references.tableHeaders.keyPoint')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {(t.raw('references.entries') as any[]).map((entry, index) => (
                      <tr key={index} className="border-b border-[#3a3a3a]">
                        <td className="py-3 pr-4 text-brand-green-400">{entry.number}</td>
                        <td className="py-3 px-4 text-[#999999]">{entry.source}</td>
                        <td className="py-3 pl-4 text-[#999999]">{entry.keyPoint}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Note */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <p className="text-[#999999]">
                <span className="font-medium text-[#EDEDED]">{t('note.title')}</span> {t('note.text')}
              </p>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-[#3a3a3a]">
        <div className="container-safe py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <p className="text-xs text-[#999999]">
              © 2025 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}