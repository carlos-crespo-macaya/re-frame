'use client'

import { ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

interface AppLayoutProps {
  children: ReactNode
  locale: string
  showBackButton?: boolean
  currentLanguage?: string
  onLanguageChange?: (locale: string) => void
}

export function AppLayout({
  children,
  locale,
  showBackButton = true,
  currentLanguage,
  onLanguageChange
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
              <Link
                href={`/${locale}/feedback`}
                className="flex items-center justify-center w-[32px] h-[32px] rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                aria-label={locale === 'es' ? 'Opinión' : 'Feedback'}
                title={locale === 'es' ? 'Opinión' : 'Feedback'}
              >
                <svg className="w-5 h-5 text-white/80" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 8h10M7 12h8m-8 4h5" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20 12c0 5.523-4.477 10-10 10a9.96 9.96 0 01-4.9-1.3L3 21l.3-2.1A9.96 9.96 0 012 12C2 6.477 6.477 2 12 2s8 4.477 8 10z" />
                </svg>
              </Link>
              <button
                className="flex items-center gap-1.5 px-3 h-[32px] rounded-full bg-white/5 hover:bg-white/10 transition-colors"
                style={{ minWidth: '80px' }}
                onClick={handleLanguageToggle}
                aria-label="Change language"
              >
                <svg className="w-5 h-5 text-white/70" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />
                </svg>
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
    </div>
  )
}
