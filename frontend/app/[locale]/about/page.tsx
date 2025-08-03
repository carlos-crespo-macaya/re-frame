import { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About re-frame',
  description: 'Learn about re-frame cognitive reframing assistant'
}

interface AboutPageProps {
  params: { locale: string }
}

export default async function AboutPage({ params }: AboutPageProps) {
  const t = await getTranslations({locale: params.locale, namespace: 'about'})

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
            <h1 className="text-3xl md:text-4xl font-heading font-medium text-[#EDEDED] mb-6">
              {t('title')}
            </h1>
          </div>

          <div className="space-y-8">
            {/* Mission */}
            <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
              <h2 className="text-xl font-heading font-medium text-brand-green-400 mb-4">
                {t('mission.label')}
              </h2>
              <p className="text-lg text-[#EDEDED] leading-relaxed">
                {t('mission.description')}
              </p>
            </section>

            {/* Details */}
            <div className="grid gap-6">
              {/* What it is */}
              <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {t('details.whatIs.label')}
                </h3>
                <p className="text-[#999999] leading-relaxed">
                  {t('details.whatIs.description')}
                </p>
              </section>

              {/* What it isn't */}
              <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {t('details.whatIsnt.label')}
                </h3>
                <p className="text-[#999999] leading-relaxed">
                  {t('details.whatIsnt.description')}
                </p>
              </section>

              {/* Creator */}
              <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {t('details.creator.title')}
                </h3>
                <p 
                  className="text-[#999999] leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: t('details.creator.content') }}
                />
              </section>

              {/* Why open source */}
              <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {t('details.whyOpen.label')}
                </h3>
                <p className="text-[#999999] leading-relaxed">
                  {t('details.whyOpen.description')}
                </p>
              </section>

              {/* Thank You */}
              <section className="bg-[#2a2a2a] rounded-lg border border-[#3a3a3a] p-6">
                <h3 className="text-lg font-heading font-medium text-[#EDEDED] mb-3">
                  {t('details.thankYou.title')}
                </h3>
                <p className="text-[#999999] leading-relaxed">
                  {t('details.thankYou.content')}
                </p>
              </section>
            </div>

            {/* Contact */}
            <section className="bg-gradient-to-r from-brand-green-600/10 to-brand-green-400/10 rounded-lg border border-brand-green-400/20 p-6">
              <p className="text-[#EDEDED] text-center">
                {t('contact.question')}
                <span className="text-brand-green-400 font-medium">
                  {t('contact.email')}
                </span>
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
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t('footer.support')}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/about`}
                    className="text-brand-green-400 font-medium"
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
