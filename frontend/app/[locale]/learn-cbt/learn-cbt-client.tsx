'use client'

import { useRouter, usePathname } from 'next/navigation'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'

interface LearnCBTClientProps {
  locale: string
  translations: {
    title: string
    quickLink: string
    introduction: string
    navigation: {
      return: string
    }
    whyHelpsAvpd: {
      title: string
      description: string
      tools: string[]
      conclusion: string
    }
    howWeUse: {
      title: string
      description: string
    }
    reminder: {
      prefix: string
      text: string
    }
    references: {
      title: string
      tableHeaders: {
        number: string
        source: string
        keyPoint: string
      }
      entries: Array<{
        number: string
        source: string
        keyPoint: string
      }>
    }
    note: {
      title: string
      text: string
    }
  }
}

export function LearnCBTClient({ locale, translations: t }: LearnCBTClientProps) {
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
            <p className="text-sm text-[#aefcf5] mb-6">
              {t.quickLink}
            </p>
            <p className="text-lg text-white/70 leading-relaxed max-w-3xl mx-auto">
              {t.introduction}
            </p>
          </div>

          <div className="space-y-8">
            {/* Why it helps with AvPD */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.whyHelpsAvpd.title}
              </h2>
              <p className="text-white/70 mb-4">
                {t.whyHelpsAvpd.description}
              </p>
              <ul className="space-y-2 mb-4">
                {t.whyHelpsAvpd.tools.map((tool, index) => (
                  <li key={index} className="text-white/70 flex items-start">
                    <span className="text-[#aefcf5] mr-2">•</span>
                    {tool}
                  </li>
                ))}
              </ul>
              <p className="text-white/70 italic">
                {t.whyHelpsAvpd.conclusion}
              </p>
            </GlassCard>

            {/* How re-frame uses CBT */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.howWeUse.title}
              </h2>
              <p className="text-white/70">
                {t.howWeUse.description}
              </p>
            </GlassCard>

            {/* Reminder */}
            <div className="rounded-[24px] backdrop-blur-[12px] p-8 border border-yellow-500/30"
              style={{
                background: 'rgba(161, 98, 7, 0.1)',
              }}
            >
              <p className="text-white">
                <span className="font-semibold">{t.reminder.prefix}</span> {t.reminder.text}
              </p>
            </div>

            {/* References */}
            <GlassCard>
              <h2 className="text-xl font-heading font-semibold text-white mb-4">
                {t.references.title}
              </h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-white/10">
                      <th className="text-left py-2 pr-4 text-white/70 font-medium">
                        {t.references.tableHeaders.number}
                      </th>
                      <th className="text-left py-2 px-4 text-white/70 font-medium">
                        {t.references.tableHeaders.source}
                      </th>
                      <th className="text-left py-2 pl-4 text-white/70 font-medium">
                        {t.references.tableHeaders.keyPoint}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {t.references.entries.map((entry, index) => (
                      <tr key={index} className="border-b border-white/10">
                        <td className="py-3 pr-4 text-[#aefcf5]">{entry.number}</td>
                        <td className="py-3 px-4 text-white/70">{entry.source}</td>
                        <td className="py-3 pl-4 text-white/70">{entry.keyPoint}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </GlassCard>

            {/* Note */}
            <GlassCard padding="md">
              <p className="text-white/70">
                <span className="font-semibold text-white">{t.note.title}</span> {t.note.text}
              </p>
            </GlassCard>
          </div>

          {/* Footer */}
          <footer className="mt-24 pt-8 border-t border-white/10">
            <div className="flex flex-col items-center gap-4">
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
