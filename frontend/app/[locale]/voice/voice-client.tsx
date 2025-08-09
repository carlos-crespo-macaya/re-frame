'use client'

import { useRouter } from 'next/navigation'
import { NaturalConversation } from '@/components/audio/NaturalConversation'
import { LanguageSelector } from '@/components/ui'
import { useState, useEffect } from 'react'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'

interface Translations {
  title: string
  subtitle: string
  back: string
}

export function VoiceClient({ locale }: { locale: string }) {
  const router = useRouter()
  const [selectedLanguage, setSelectedLanguage] = useState(locale === 'es' ? 'es-ES' : 'en-US')
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY
  const provider = process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER === 'enterprise' ? 'enterprise' : 'classic'
  const { ready, execute } = useRecaptcha(siteKey, provider)

  // Translations
  const translations: Record<string, Translations> = {
    en: {
      title: 'Voice Conversation',
      subtitle: 'Speak naturally with re-frame',
      back: '← Back to home',
    },
    es: {
      title: 'Conversación por Voz',
      subtitle: 'Habla naturalmente con re-frame',
      back: '← Volver al inicio',
    },
  }

  const t: Translations = translations[locale] || translations.en

  useEffect(() => {
    setSelectedLanguage(locale === 'es' ? 'es-ES' : 'en-US')
  }, [locale])

  // Prefetch a token on voice page mount to avoid first-click race
  useEffect(() => {
    (async () => {
      try {
        if (ready) {
          await execute('voice_start')
        }
      } catch {
        // best effort
      }
    })()
  }, [ready, execute])

  const handleBack = () => {
    router.push(`/${locale}`)
  }

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
    const newLocale = language.startsWith('es') ? 'es' : 'en'
    const newPath = `/${newLocale}/voice`
    router.push(newPath)
  }


  return (
    <div className="min-h-screen bg-dark-charcoal text-[#EDEDED]">
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-400 mb-2">
                re-frame
              </h1>
              <button
                type="button"
                onClick={handleBack}
                className="text-brand-green-400 hover:text-brand-green-300 transition-colors"
              >
                {t.back}
              </button>
            </div>
            <div className="w-48">
              <LanguageSelector 
                value={selectedLanguage}
                onChange={handleLanguageChange}
              />
            </div>
          </div>
        </div>
      </header>


      {/* Main content */}
      <main className="container-safe py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <NaturalConversation language={selectedLanguage} />
        </div>
      </main>
    </div>
  )
}