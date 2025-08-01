import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Privacy Policy - re-frame',
  description: 'Privacy policy for re-frame cognitive reframing assistant'
}

interface PrivacyPageProps {
  params: { locale: string }
}

export default async function PrivacyPage({ params }: PrivacyPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'privacy'})

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
            <p className="text-sm text-[#999999] mb-6">
              {t('lastUpdated')}
            </p>
            <p className="text-lg text-[#999999] leading-relaxed">
              {t('introduction')}
            </p>
          </div>

          <div className="space-y-8">
            {/* Data Collection */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.dataCollection.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.dataCollection.description')}
              </p>
              <ul className="space-y-2">
                {(t.raw('sections.dataCollection.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </section>

            {/* Technical Data */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.technicalData.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.technicalData.description')}
              </p>
              <ul className="space-y-2 mb-4">
                {(t.raw('sections.technicalData.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
              <p className="text-sm text-[#999999] italic">
                {t('sections.technicalData.note')}
              </p>
            </section>

            {/* Cookies */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.cookies.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.cookies.description')}
              </p>
              <ul className="space-y-2 mb-4">
                {(t.raw('sections.cookies.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
              <p className="text-sm text-[#999999]">
                {t('sections.cookies.control')}
              </p>
            </section>

            {/* Third Party Services */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.thirdPartyServices.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.thirdPartyServices.description')}
              </p>
              <div className="space-y-4">
                {(t.raw('sections.thirdPartyServices.services') as any[]).map((service, index) => (
                  <div key={index} className="border-l-2 border-brand-green-400 pl-4">
                    <h3 className="font-medium text-[#EDEDED]">{service.name}</h3>
                    <p className="text-sm text-[#999999]">
                      <strong>Purpose:</strong> {service.purpose}
                    </p>
                    <p className="text-sm text-[#999999]">
                      <strong>Data sharing:</strong> {service.dataSharing}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Data Retention */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.dataRetention.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.dataRetention.description')}
              </p>
              <ul className="space-y-2">
                {(t.raw('sections.dataRetention.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </section>

            {/* Your Rights */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.yourRights.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.yourRights.description')}
              </p>
              <ul className="space-y-2">
                {(t.raw('sections.yourRights.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </section>

            {/* Security */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.security.title')}
              </h2>
              <p className="text-[#999999] mb-4">
                {t('sections.security.description')}
              </p>
              <ul className="space-y-2">
                {(t.raw('sections.security.points') as string[]).map((point, index) => (
                  <li key={index} className="text-[#999999] flex items-start">
                    <span className="text-brand-green-400 mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </section>

            {/* Changes to Policy */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.changes.title')}
              </h2>
              <p className="text-[#999999]">
                {t('sections.changes.description')}
              </p>
            </section>

            {/* Contact */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                {t('sections.contact.title')}
              </h2>
              <p className="text-[#999999] mb-2">
                {t('sections.contact.description')}
              </p>
              <p className="text-brand-green-400">
                {t('sections.contact.email')}
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
                    className="text-brand-green-400 font-medium"
                  >
                    {t('footer.privacy')}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/support`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
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
