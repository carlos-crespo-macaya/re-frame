'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { LanguageSelector } from '@/components/ui'

// Translation dictionary
const translations = {
  en: {
    header: {
      title: 're-frame',
      subtitle: 'Cognitive reframing support',
    },
    hero: {
      title: 'Explore a new perspective',
      description: "We'll use evidence-based therapeutic techniques to spot thinking patterns and suggest gentler perspectives.",
      learnMore: 'CBT in 2 minutes:',
      learnMoreLink: 'a clear, high‑level overview ↗',
    },
    cta: {
      title: 'Ready to start?',
      description: 'Begin a private session to explore your thoughts with evidence-based CBT techniques.',
      button: 'Start Your Session',
      privacy: "Private session — we don't store personal data.",
    },
    steps: {
      title: 'How re-frame works',
      step1: {
        title: 'Tell us what happened',
        description: 'Use your own words. Take the time you need.',
      },
      step2: {
        title: 'Notice thinking patterns',
        description: "We'll apply therapeutic frameworks to highlight alternative perspectives.",
      },
      step3: {
        title: 'Pick a perspective that feels true',
        description: 'Select from alternative ways to view your situation.',
      },
    },
    trust: {
      title: 'Designed for people living with AvPD & social anxiety',
      description: "This tool uses evidence-based therapeutic techniques. Your privacy is protected - we don't store any personal information.",
    },
    footer: {
      privacy: 'Privacy',
      support: 'Support',
      about: 'About',
      copyright: '© 2024 re-frame.social',
    },
  },
  es: {
    header: {
      title: 're-frame',
      subtitle: 'Apoyo de reencuadre cognitivo',
    },
    hero: {
      title: 'Explora una nueva perspectiva',
      description: 'Usaremos técnicas terapéuticas basadas en evidencia para identificar patrones de pensamiento y sugerir perspectivas más amables.',
      learnMore: 'TCC en 2 minutos:',
      learnMoreLink: 'una visión general clara ↗',
    },
    cta: {
      title: '¿Listo para comenzar?',
      description: 'Comienza una sesión privada para explorar tus pensamientos con técnicas de TCC basadas en evidencia.',
      button: 'Iniciar Tu Sesión',
      privacy: 'Sesión privada — no almacenamos datos personales.',
    },
    steps: {
      title: 'Cómo funciona re-frame',
      step1: {
        title: 'Cuéntanos qué pasó',
        description: 'Usa tus propias palabras. Tómate el tiempo que necesites.',
      },
      step2: {
        title: 'Identifica patrones de pensamiento',
        description: 'Aplicaremos marcos terapéuticos para resaltar perspectivas alternativas.',
      },
      step3: {
        title: 'Elige una perspectiva que se sienta verdadera',
        description: 'Selecciona entre formas alternativas de ver tu situación.',
      },
    },
    trust: {
      title: 'Diseñado para personas con TPA y ansiedad social',
      description: 'Esta herramienta utiliza técnicas terapéuticas basadas en evidencia. Tu privacidad está protegida - no almacenamos ninguna información personal.',
    },
    footer: {
      privacy: 'Privacidad',
      support: 'Soporte',
      about: 'Acerca de',
      copyright: '© 2024 re-frame.social',
    },
  },
}

export default function LocalePage({ params }: { params: { locale: string } }) {
  const router = useRouter()
  const pathname = usePathname()
  const [selectedLanguage, setSelectedLanguage] = useState(params.locale === 'es' ? 'es-ES' : 'en-US')
  
  const t = translations[params.locale as keyof typeof translations] || translations.en

  useEffect(() => {
    // Update language when locale changes
    setSelectedLanguage(params.locale === 'es' ? 'es-ES' : 'en-US')
  }, [params.locale])

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
    const newLocale = language.startsWith('es') ? 'es' : 'en'
    const newPath = pathname.replace(`/${params.locale}`, `/${newLocale}`)
    router.push(newPath)
  }

  const handleStartSession = () => {
    router.push(`/${params.locale}/chat`)
  }

  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-heading font-semibold text-brand-green-400">
                {t.header.title}
              </h1>
              <p className="text-sm text-[#999999] mt-1">
                {t.header.subtitle}
              </p>
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
      <main id="main-content" className="flex-1">
        <div className="container-safe py-8 md:py-12">
          {/* Welcome section with warm messaging */}
          <section className="max-w-3xl mx-auto text-center mb-12 animate-fade-in">
            <h2 className="text-3xl md:text-4xl font-heading font-medium text-[#EDEDED] mb-6">
              {t.hero.title}
            </h2>
            <p className="text-lg text-[#999999] mb-4 leading-relaxed">
              {t.hero.description}
            </p>
            <p className="text-[#999999] max-w-2xl mx-auto">
              <span className="text-sm">{t.hero.learnMore} <a href={`/${params.locale}/learn-cbt`} className="text-brand-green-400 underline hover:text-brand-green-300">{t.hero.learnMoreLink}</a></span>
            </p>
          </section>

          {/* Start session section */}
          <section className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="relative bg-[#2a2a2a] rounded-2xl shadow-lg border border-[#3a3a3a] p-8 md:p-10" style={{ 
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                animation: 'fadeIn 250ms cubic-bezier(0.25, 0.1, 0.25, 1)'
              }}>
                <div className="text-center">
                  <h3 className="text-xl font-heading font-medium text-[#EDEDED] mb-4">
                    {t.cta.title}
                  </h3>
                  <p className="text-[#999999] mb-8">
                    {t.cta.description}
                  </p>
                  <button
                    onClick={handleStartSession}
                    className="px-8 py-3 bg-brand-green-600 text-white rounded-full font-medium hover:bg-brand-green-700 transition-colors"
                  >
                    {t.cta.button}
                  </button>
                  <p className="mt-6 text-sm text-[#999999]">
                    {t.cta.privacy}
                  </p>
                </div>
              </div>
            </div>
          </section>

          {/* How it works section with gentle illustrations */}
          <section className="max-w-3xl mx-auto mt-16 space-y-12">
            <div className="text-center">
              <h3 className="text-2xl font-heading font-medium text-[#EDEDED] mb-12">
                {t.steps.title}
              </h3>
              <div className="grid md:grid-cols-3 gap-8 mt-6">
                {/* Step 1 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">1</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    {t.steps.step1.title}
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    {t.steps.step1.description}
                  </p>
                </div>

                {/* Step 2 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">2</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    {t.steps.step2.title}
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    {t.steps.step2.description}
                  </p>
                </div>

                {/* Step 3 */}
                <div className="group">
                  <div className="mb-6">
                    <div className="w-16 h-16 mx-auto bg-brand-green-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-semibold">3</span>
                    </div>
                  </div>
                  <h4 className="font-heading font-medium text-base text-[#EDEDED] mb-3">
                    {t.steps.step3.title}
                  </h4>
                  <p className="text-base text-[#999999] leading-relaxed">
                    {t.steps.step3.description}
                  </p>
                </div>
              </div>
            </div>

            {/* Trust message */}
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-warm-sand/10 via-soft-sky/10 to-breathing-mint/10 rounded-2xl blur-2xl" />
              <div className="relative border-t border-b border-[#3a3a3a] py-8">
                <p className="text-center text-[#999999] max-w-2xl mx-auto leading-relaxed">
                  <span className="block text-lg font-heading font-medium text-brand-green-400 mb-3">
                    {t.trust.title}
                  </span>
                  {t.trust.description}
                </p>
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              {t.header.title}
            </h2>
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <Link 
                    href={`/${params.locale}/privacy`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t.footer.privacy}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/support`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t.footer.support}
                  </Link>
                </li>
                <li>
                  <Link 
                    href={`/${params.locale}/about`}
                    className="text-[#999999] hover:text-brand-green-400 transition-colors"
                  >
                    {t.footer.about}
                  </Link>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-[#999999]">
              {t.footer.copyright}
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
