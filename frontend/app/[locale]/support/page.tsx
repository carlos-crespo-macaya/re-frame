import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Support & Help - re-frame',
  description: 'Get help with re-frame or find mental health resources'
}

interface SupportPageProps {
  params: { locale: string }
}

export default async function SupportPage({ params }: SupportPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'support'})

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
              {t('navigation.back')}
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
            <p className="text-lg text-[#999999] leading-relaxed">
              {t('subtitle')}
            </p>
          </div>

          <div className="space-y-8">
            {/* Technical Support */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.technicalSupport.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.technicalSupport.description')}
              </p>
              <p className="text-[#999999] mb-2">
                {t('sections.technicalSupport.contact')}
              </p>
              <p className="text-brand-green-400 text-lg mb-4">
                {t('sections.technicalSupport.email')}
              </p>
              <p className="text-sm text-[#999999]">
                {t('sections.technicalSupport.responseTime')}
              </p>
            </section>

            {/* Mental Health Resources */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.mentalHealthResources.title')}
              </h2>
              <p className="text-[#999999] mb-6">
                {t('sections.mentalHealthResources.description')}
              </p>
              <div className="space-y-4">
                {(t.raw('sections.mentalHealthResources.resources') as any[]).map((resource, index) => (
                  <div key={index} className="border-l-2 border-brand-green-400 pl-4">
                    <h3 className="font-medium text-[#EDEDED] mb-1">{resource.title}</h3>
                    <p className="text-[#999999] mb-1">{resource.description}</p>
                    <p className="text-sm text-brand-green-400">{resource.availability}</p>
                    {resource.link && (
                      <p className="text-sm text-brand-green-400 mt-1">{resource.link}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* About AvPD */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.aboutAvpd.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.aboutAvpd.description')}
              </p>
              <div className="space-y-3">
                {(t.raw('sections.aboutAvpd.resources') as any[]).map((resource, index) => (
                  <div key={index} className="border-l-2 border-brand-green-400 pl-4">
                    <h3 className="font-medium text-[#EDEDED]">{resource.title}</h3>
                    {resource.description && (
                      <p className="text-sm text-[#999999]">{resource.description}</p>
                    )}
                    {resource.link && (
                      <p className="text-sm text-brand-green-400">{resource.link}</p>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* Privacy & Safety */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.privacyAndSafety.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.privacyAndSafety.description')}
              </p>
              <ul className="space-y-2">
                {(t.raw('sections.privacyAndSafety.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </section>

            {/* Important Reminder */}
            <section className="bg-red-900/20 border border-red-500/30 rounded-lg p-6">
              <h2 className="text-xl font-heading font-medium text-red-400 mb-4">
                {t('reminder.title')}
              </h2>
              <p className="text-[#EDEDED] leading-relaxed">
                {t('reminder.text')}
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
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <Link 
                    href={`/${params.locale}/privacy`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t('footer.privacy')}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/support`}
                    className="text-brand-green-400 font-medium"
                  >
                    {t('footer.support')}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/about`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t('footer.about')}
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
    </div>
  )
}
