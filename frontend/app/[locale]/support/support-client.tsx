'use client'

import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'

interface SupportClientProps {
  locale: string
  translations: {
    title: string
    subtitle: string
    sections: {
      technicalSupport: {
        title: string
        description: string
        contact: string
        email: string
        responseTime: string
      }
      mentalHealthResources: {
        title: string
        description: string
        resources: Array<{ name: string; description?: string; url?: string }>
      }
      aboutAvpd: {
        title: string
        description: string
        resources: Array<{ name: string; description?: string; url?: string }>
      }
      privacyAndSafety: {
        title: string
        description: string
        points: string[]
      }
    }
    reminder: { title: string; text: string }
    footer: { privacy: string; support: string; about: string }
  }
}

export function SupportClient({ locale, translations: t }: SupportClientProps) {
  const router = useRouter()
  const pathname = usePathname()

  return (
    <AppLayout
      locale={locale}
      showBackButton={true}
      showFooter={true}
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
            <p className="text-lg text-white/70 leading-relaxed max-w-3xl mx-auto">
              {t.subtitle}
            </p>
          </div>

          <div className="space-y-8">
            {/* Technical Support */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.technicalSupport.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.technicalSupport.description}
              </p>
              <p className="text-white/70 mb-2">
                {t.sections.technicalSupport.contact}
              </p>
              <p className="text-[#aefcf5] text-lg mb-4">
                {t.sections.technicalSupport.email}
              </p>
              <p className="text-sm text-white/45">
                {t.sections.technicalSupport.responseTime}
              </p>
            </GlassCard>

            {/* Mental Health Resources */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.mentalHealthResources.title}
              </h2>
              <p className="text-white/70 mb-6">
                {t.sections.mentalHealthResources.description}
              </p>
              <div className="space-y-4">
                {t.sections.mentalHealthResources.resources.map((resource: any, index: number) => (
                  <div key={index} className="border-l-2 border-[#aefcf5] pl-4">
                    <h3 className="font-semibold text-white mb-1">{resource.name}</h3>
                    <p className="text-white/70 mb-1">{resource.description}</p>
                    {resource.url && (
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-[#aefcf5] hover:text-white transition-colors underline"
                      >
                        {resource.url}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </GlassCard>

            {/* About AvPD */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.aboutAvpd.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.aboutAvpd.description}
              </p>
              <div className="space-y-3">
                {t.sections.aboutAvpd.resources.map((resource: any, index: number) => (
                  <div key={index} className="border-l-2 border-[#aefcf5] pl-4">
                    <h3 className="font-semibold text-white">{resource.name}</h3>
                    {resource.description && (
                      <p className="text-sm text-white/70 mb-1">{resource.description}</p>
                    )}
                    {resource.url && (
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-[#aefcf5] hover:text-white transition-colors underline"
                      >
                        {resource.url}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </GlassCard>

            {/* Privacy & Safety */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.sections.privacyAndSafety.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.sections.privacyAndSafety.description}
              </p>
              <ul className="space-y-2">
                {t.sections.privacyAndSafety.points.map((point: string, index: number) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {point}
                  </li>
                ))}
              </ul>
            </GlassCard>

            {/* Important Reminder */}
            <div className="rounded-[24px] backdrop-blur-[12px] p-8 border border-red-500/30"
              style={{
                background: 'rgba(127, 29, 29, 0.1)',
              }}
            >
              <h2 className="text-xl font-heading font-semibold text-red-400 mb-4">
                {t.reminder.title}
              </h2>
              <p className="text-white leading-relaxed">
                {t.reminder.text}
              </p>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-24 pt-8 border-t border-white/10">
            <div className="flex flex-col items-center gap-4">
              <nav aria-label="Footer navigation">
                <ul className="flex gap-6 text-sm">
                  <li>
                    <Link
                      href={`/${locale}/privacy`}
                      className="text-white/45 hover:text-[#aefcf5] transition-colors"
                    >
                      {t.footer.privacy}
                    </Link>
                  </li>
                  <li>
                    <Link
                      href={`/${locale}/support`}
                      className="text-[#aefcf5] font-medium"
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
