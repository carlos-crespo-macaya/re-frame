'use client'

import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'

interface PrivacyTranslations {
  title: string
  lastUpdated: string
  introduction: string
  sections: {
    dataCollection: { title: string; description: string; points: string[] }
    technicalData: { title: string; description: string; points: string[]; note: string }
    dataRetention: { title: string; description: string; points: string[] }
    yourRights: { title: string; description: string; points: string[] }
    security: { title: string; description: string; points: string[] }
    changes: { title: string; description: string }
    contact: { title: string; description: string; email: string }
  }
  footer: { privacy: string; support: string; about: string }
}

interface PrivacyClientProps {
  locale: string
  translations: PrivacyTranslations
}

export function PrivacyClient({ locale, translations: t }: PrivacyClientProps) {
  const router = useRouter()
  const pathname = usePathname()

  return (
    <AppLayout
      locale={locale}
      showBackButton={true}
      currentLanguage={locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const newPath = pathname.replace(`/${locale}`, `/${newLocale}`)
        router.push(newPath)
      }}
    >
      <div className="max-w-[1312px] mx-auto w-full">
        <div className="max-w-4xl mx-auto">
          {/* Page title and intro */}
          <div className="mb-12 text-center">
            <h1 className="text-3xl md:text-4xl font-heading font-bold text-white mb-4">
              {t.title}
            </h1>
            <p className="text-sm text-white/45 mb-6">
              {t.lastUpdated}
            </p>
            <p className="text-lg text-white/70 leading-relaxed max-w-3xl mx-auto">
              {t.introduction}
            </p>
          </div>

          <div className="space-y-8">
            {/* Data Collection */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.dataCollection.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.dataCollection.description}
              </p>
              <ul className="space-y-2">
                {t.sections.dataCollection.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Technical Data */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.technicalData.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.technicalData.description}
              </p>
              <ul className="space-y-2 mb-4">
                {t.sections.technicalData.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
              <p className="text-sm text-white/45 italic">
                {t.sections.technicalData.note}
              </p>
            </GlassCard>

            {/* Data Retention */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.dataRetention.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.dataRetention.description}
              </p>
              <ul className="space-y-2">
                {t.sections.dataRetention.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Your Rights */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.yourRights.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.yourRights.description}
              </p>
              <ul className="space-y-2">
                {t.sections.yourRights.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Security */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.security.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.security.description}
              </p>
              <ul className="space-y-2">
                {t.sections.security.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Changes to Policy */}
            <GlassCard padding="md">
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.changes.title}
              </h2>
              <p className="text-white/70">
                {t.sections.changes.description}
              </p>
            </GlassCard>

            {/* Contact */}
            <GlassCard padding="md">
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.contact.title}
              </h2>
              <p className="text-white/70 mb-2">
                {t.sections.contact.description}
              </p>
              <p className="text-[#aefcf5]">
                {t.sections.contact.email}
              </p>
            </GlassCard>
          </div>

          {/* Footer */}
          <footer className="mt-24 pt-8 border-t border-white/10">
            <div className="flex flex-col items-center gap-4">
              <nav aria-label="Footer navigation">
                <ul className="flex gap-6 text-sm">
                  <li>
                    <Link
                      href={`/${locale}/privacy`}
                      className="text-[#aefcf5] font-medium"
                    >
                      {t.footer.privacy}
                    </Link>
                  </li>
                  <li>
                    <Link
                      href={`/${locale}/support`}
                      className="text-white/45 hover:text-[#aefcf5] transition-colors"
                    >
                      {t.footer.support}
                    </Link>
                  </li>
                  <li>
                    <Link
                      href={`/${locale}/about`}
                      className="text-white/45 hover:text-[#aefcf5] transition-colors"
                    >
                      {t.footer.about}
                    </Link>
                  </li>
                </ul>
              </nav>
              <p className="text-xs text-white/45">
                © 2025 re-frame.social
              </p>
            </div>
          </footer>
        </div>
      </div>
    </AppLayout>
  )
}
