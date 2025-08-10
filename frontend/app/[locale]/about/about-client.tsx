'use client'

import { useRouter, usePathname } from 'next/navigation'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { ImportantReminder } from '@/components/ui/ImportantReminder'

interface AboutClientProps {
  locale: string
  translations: {
    title: string
    navigation: {
      back: string
    }
    mission: {
      label: string
      description: string
    }
    details: {
      whatIs: {
        label: string
        description: string
      }
      whatIsnt: {
        label: string
        description: string
      }
      creator: {
        title: string
        content: string
      }
      thankYou: {
        title: string
        content: string
      }
    }
    contact: {
      question: string
      email: string
    }
    footer: {
      privacy: string
      support: string
      about: string
    }
  }
}

export function AboutClient({ locale, translations: t }: AboutClientProps) {
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
          {/* Page title */}
          <div className="mb-12 text-center">
            <h1 className="text-3xl md:text-4xl font-heading font-bold text-white">
              {t.title}
            </h1>
          </div>

          <div className="space-y-8">
            {/* Mission */}
            <GlassCard>
              <h3 className="text-lg font-heading font-semibold text-white mb-3">
                {t.mission.label}
              </h3>
              <p className="text-white/70 leading-relaxed">
                {t.mission.description}
              </p>
            </GlassCard>

            {/* Details */}
            <div className="grid gap-6">
              {/* What it is */}
              <GlassCard padding="md">
                <h3 className="text-lg font-heading font-semibold text-white mb-3">
                  {t.details.whatIs.label}
                </h3>
                <p className="text-white/70 leading-relaxed">
                  {t.details.whatIs.description}
                </p>
              </GlassCard>

              {/* What it isn't */}
              <GlassCard padding="md">
                <h3 className="text-lg font-heading font-semibold text-white mb-3">
                  {t.details.whatIsnt.label}
                </h3>
                <p className="text-white/70 leading-relaxed">
                  {t.details.whatIsnt.description}
                </p>
              </GlassCard>

              {/* Creator */}
              <GlassCard padding="md">
                <h3 className="text-lg font-heading font-semibold text-white mb-3">
                  {t.details.creator.title}
                </h3>
                <p
                  className="text-white/70 leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: t.details.creator.content }}
                />
              </GlassCard>

              {/* Thank You */}
              <GlassCard padding="md">
                <h3 className="text-lg font-heading font-semibold text-white mb-3">
                  {t.details.thankYou.title}
                </h3>
                <p className="text-white/70 leading-relaxed">
                  {t.details.thankYou.content}
                </p>
              </GlassCard>
            </div>

            {/* Important reminder */}
            <ImportantReminder locale={locale} variant="default" />

            {/* Contact */}
            <GlassCard className="text-center">
              <p className="text-white">
                {t.contact.question}
                <span className="text-[#aefcf5] font-semibold ml-1">
                  {t.contact.email}
                </span>
              </p>
            </GlassCard>
          </div>
        </div>
      </div>
    </AppLayout>
  )
}
