'use client'

import { ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { FeedbackIcon, GlobeIcon } from '@/components/icons'
import { Footer } from './Footer'

interface AppLayoutProps {
  children: ReactNode
  locale: string
  showBackButton?: boolean
  showFeedbackButton?: boolean
  showFooter?: boolean
  currentLanguage?: string
  onLanguageChange?: (locale: string) => void
  footerTranslations?: {
    privacy: string
    support: string
    about: string
    copyright: string
  }
}

export function AppLayout({
  children,
  locale,
  showBackButton = true,
  showFeedbackButton = true,
  showFooter = false,
  currentLanguage,
  onLanguageChange,
  footerTranslations
}: AppLayoutProps) {
  const router = useRouter()

  const handleBack = () => {
    router.push(`/${locale}`)
  }

  const handleLanguageToggle = () => {
    const newLocale = locale === 'es' ? 'en' : 'es'
    if (onLanguageChange) {
      onLanguageChange(newLocale)
    } else {
      const currentPath = window.location.pathname.replace(`/${locale}`, `/${newLocale}`)
      router.push(currentPath)
    }
  }

  return (
    <div
      className="flex flex-col min-h-screen text-white relative overflow-hidden"
      style={{
        background: 'radial-gradient(ellipse at center, #0a2a3a 0%, #062633 25%, #03141d 50%, #020c12 100%)',
      }}
    >
      {/* Header */}
      <header className="flex-shrink-0 relative z-10">
        <div className="px-4 sm:px-8 lg:px-16 py-4 sm:py-6">
          <div className="flex items-center justify-between max-w-[1312px] mx-auto">
            <div className="flex items-center gap-3">
              {showBackButton && (
                <button
                  type="button"
                  onClick={handleBack}
                  className="text-[#aefcf5] hover:text-white transition-colors"
                  aria-label="Back to home"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
              )}
              <Link href={`/${locale}`} className="flex items-center gap-3 no-underline">
                <div className="w-8 h-8 rounded-full bg-[#aefcf5] flex items-center justify-center">
                  <span className="text-[#03141d] font-bold text-sm">R</span>
                </div>
                <h1 className="text-[20px] sm:text-[24px] font-semibold" style={{ color: '#aefcf5' }}>
                  re-frame
                </h1>
              </Link>
            </div>
            <div className="flex items-center gap-2">
            {showFeedbackButton && (
              <Link
                href={`/${locale}/feedback`}
                className="flex items-center justify-center px-3 h-[32px] rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                style={{ minWidth: '80px' }}
                aria-label={locale === 'es' ? 'Opinión' : 'Feedback'}
                title={locale === 'es' ? 'Opinión' : 'Feedback'}
              >
                <FeedbackIcon />
              </Link>
            )}
              <button
                className="flex items-center gap-1.5 px-3 h-[32px] rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                style={{ minWidth: '80px' }}
                onClick={handleLanguageToggle}
                aria-label="Change language"
              >
                <GlobeIcon />
                <span className="text-xs text-white/70">{currentLanguage || (locale === 'es' ? 'ES' : 'EN')}</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col px-4 sm:px-8 lg:px-16 pb-8" style={{ paddingTop: '32px' }}>
        {children}
      </main>
      
      {/* Footer */}
      {showFooter && (
        <div className="px-4 sm:px-8 lg:px-16">
          <Footer locale={locale} translations={footerTranslations} />
        </div>
      )}
    </div>
  )
}
