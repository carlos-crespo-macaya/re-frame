import Link from 'next/link'

interface FooterProps {
  locale: string
  translations?: {
    privacy: string
    support: string
    about: string
    copyright: string
  }
}

export function Footer({ locale, translations }: FooterProps) {
  // Default translations
  const defaultTranslations = {
    en: {
      privacy: 'Privacy',
      support: 'Support',
      about: 'About',
      copyright: '© 2025 re-frame.social',
    },
    es: {
      privacy: 'Privacidad',
      support: 'Soporte',
      about: 'Acerca de',
      copyright: '© 2025 re-frame.social',
    },
  }

  const t = translations || defaultTranslations[locale as keyof typeof defaultTranslations] || defaultTranslations.en

  return (
    <footer className="mt-24 pt-8 border-t border-white/10">
      <div className="flex flex-col items-center gap-4">
        <nav aria-label="Footer navigation">
          <ul className="flex gap-6 text-sm">
            <li>
              <Link
                href={`/${locale}/privacy`}
                className="text-white/45 hover:text-[#aefcf5] transition-colors"
              >
                {t.privacy}
              </Link>
            </li>
            <li>
              <Link
                href={`/${locale}/support`}
                className="text-white/45 hover:text-[#aefcf5] transition-colors"
              >
                {t.support}
              </Link>
            </li>
            <li>
              <Link
                href={`/${locale}/about`}
                className="text-white/45 hover:text-[#aefcf5] transition-colors"
              >
                {t.about}
              </Link>
            </li>
          </ul>
        </nav>
        <p className="text-xs text-white/45">
          {t.copyright}
        </p>
      </div>
    </footer>
  )
}