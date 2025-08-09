'use client'

import { useState, useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { InterfaceSelector } from '@/components/ui'

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
      learnMore: 'Learn about',
      learnMoreLink: 'The approach behind re-frame',
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
      feedback: 'Feedback',
      copyright: '© 2025 re-frame.social',
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
      learnMore: 'Aprende sobre',
      learnMoreLink: 'El enfoque detrás de re-frame',
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
      feedback: 'Opinión',
      copyright: '© 2025 re-frame.social',
    },
  },
}

export default function LocalePage({ params }: { params: { locale: string } }) {
  const router = useRouter()
  const pathname = usePathname()
  const [selectedLanguage, setSelectedLanguage] = useState(params.locale === 'es' ? 'es-ES' : 'en-US')

  const t = translations[params.locale as keyof typeof translations] || translations.en

  useEffect(() => {
    setSelectedLanguage(params.locale === 'es' ? 'es-ES' : 'en-US')
  }, [params.locale])

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
    const newLocale = language.startsWith('es') ? 'es' : 'en'
    const newPath = pathname.replace(`/${params.locale}`, `/${newLocale}`)
    router.push(newPath)
  }

  return (
    <AppLayout
      locale={params.locale}
      showBackButton={false}
      currentLanguage={params.locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const newPath = pathname.replace(`/${params.locale}`, `/${newLocale}`)
        router.push(newPath)
      }}
    >
      <div className="max-w-[1312px] mx-auto w-full">
        {/* Welcome section */}
        <section className="text-center mb-12 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-6">
            {t.hero.title}
          </h2>
          <p className="text-lg text-white/70 mb-4 leading-relaxed max-w-3xl mx-auto">
            {t.hero.description}
          </p>
          <p className="text-white/45 max-w-2xl mx-auto">
            <span className="text-sm">{t.hero.learnMore} <Link href={`/${params.locale}/learn-cbt`} className="text-[#aefcf5] underline hover:text-white transition-colors">{t.hero.learnMoreLink}</Link></span>
          </p>
        </section>

        {/* Interface selection - Enhanced with proper hierarchy */}
        <GlassCard className="max-w-5xl mx-auto mb-12" padding="xl">
          <div className="text-center mb-8">
            <h3 className="text-xl font-heading font-semibold text-white/90 mb-4">
              {t.cta.title}
            </h3>
            <p className="text-[15px] text-[#cdd5d7]/70 mb-2 leading-relaxed max-w-[48ch] mx-auto">
              {t.cta.description}
            </p>
            <p className="text-[13px] text-white/40 mt-2">
              {t.cta.privacy}
            </p>
          </div>
          <InterfaceSelector locale={params.locale} />
        </GlassCard>

        {/* How it works */}
        <section className="max-w-4xl mx-auto mt-16">
          <h3 className="text-2xl font-heading font-bold text-white text-center mb-12">
            {t.steps.title}
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <GlassCard padding="md" className="text-center">
              <div className="mb-4">
                <div className="w-12 h-12 mx-auto bg-[#aefcf5] rounded-full flex items-center justify-center">
                  <span className="text-[#03141d] font-bold">1</span>
                </div>
              </div>
              <h4 className="font-heading font-semibold text-white mb-3">
                {t.steps.step1.title}
              </h4>
              <p className="text-sm text-white/70 leading-relaxed">
                {t.steps.step1.description}
              </p>
            </GlassCard>

            {/* Step 2 */}
            <GlassCard padding="md" className="text-center">
              <div className="mb-4">
                <div className="w-12 h-12 mx-auto bg-[#aefcf5] rounded-full flex items-center justify-center">
                  <span className="text-[#03141d] font-bold">2</span>
                </div>
              </div>
              <h4 className="font-heading font-semibold text-white mb-3">
                {t.steps.step2.title}
              </h4>
              <p className="text-sm text-white/70 leading-relaxed">
                {t.steps.step2.description}
              </p>
            </GlassCard>

            {/* Step 3 */}
            <GlassCard padding="md" className="text-center">
              <div className="mb-4">
                <div className="w-12 h-12 mx-auto bg-[#aefcf5] rounded-full flex items-center justify-center">
                  <span className="text-[#03141d] font-bold">3</span>
                </div>
              </div>
              <h4 className="font-heading font-semibold text-white mb-3">
                {t.steps.step3.title}
              </h4>
              <p className="text-sm text-white/70 leading-relaxed">
                {t.steps.step3.description}
              </p>
            </GlassCard>
          </div>

          {/* Trust message */}
          <div className="mt-16 text-center">
            <GlassCard className="max-w-3xl mx-auto">
              <p className="text-lg font-heading font-semibold text-[#aefcf5] mb-3">
                {t.trust.title}
              </p>
              <p className="text-white/70 leading-relaxed">
                {t.trust.description}
              </p>
            </GlassCard>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-24 pt-8 border-t border-white/10">
          <div className="flex flex-col items-center gap-4">
            <nav aria-label="Footer navigation">
              <ul className="flex gap-6 text-sm">
                <li>
                  <Link
                    href={`/${params.locale}/privacy`}
                    className="text-white/45 hover:text-[#aefcf5] transition-colors"
                  >
                    {t.footer.privacy}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${params.locale}/support`}
                    className="text-white/45 hover:text-[#aefcf5] transition-colors"
                  >
                    {t.footer.support}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${params.locale}/about`}
                    className="text-white/45 hover:text-[#aefcf5] transition-colors"
                  >
                    {t.footer.about}
                  </Link>
                </li>
                <li>
                  <Link
                    href={`/${params.locale}/feedback`}
                    className="text-white/45 hover:text-[#aefcf5] transition-colors"
                  >
                    {t.footer.feedback}
                  </Link>
                </li>
              </ul>
            </nav>
            <p className="text-xs text-white/45">
              {t.footer.copyright}
            </p>
          </div>
        </footer>
      </div>
    </AppLayout>
  );
}
