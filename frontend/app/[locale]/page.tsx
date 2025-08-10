'use client'

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
      title: 'Find a kinder perspective',
      description: "With evidence-based CBT, we’ll help you notice thinking patterns and try gentler, more balanced perspectives.",
      learnMore: 'Learn about',
      learnMoreLink: 'The approach behind re-frame',
    },
    cta: {
      title: 'Ready to begin?',
      description: 'Start a private session to explore your thoughts using evidence-based CBT tools.',
      button: 'Start Your Session',
      privacy: "Private session — we don't store personal data.",
    },
    steps: {
      title: 'How re-frame helps',
      step1: {
        title: 'Share what’s on your mind',
        description: 'Use your own words, at your own pace.',
      },
      step2: {
        title: 'Spot common thinking patterns',
        description: "We surface likely patterns and offer perspective-taking prompts.",
      },
      step3: {
        title: 'Choose what feels true and helpful',
        description: 'Pick alternative viewpoints that resonate with you.',
      },
    },
    trust: {
      title: 'Made with care for AvPD & social anxiety',
      description: "Built on evidence-based techniques. Your privacy matters—we don’t store personal information.",
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
      title: 'Encuentra una perspectiva más amable',
      description: 'Con TCC basada en evidencia, te ayudamos a notar patrones de pensamiento y a probar perspectivas más amables y equilibradas.',
      learnMore: 'Aprende sobre',
      learnMoreLink: 'El enfoque detrás de re-frame',
    },
    cta: {
      title: '¿Listo para empezar?',
      description: 'Inicia una sesión privada para explorar tus pensamientos con herramientas de TCC basadas en evidencia.',
      button: 'Iniciar Tu Sesión',
      privacy: 'Sesión privada — no almacenamos datos personales.',
    },
    steps: {
      title: 'Cómo te ayuda re-frame',
      step1: {
        title: 'Comparte lo que tengas en mente',
        description: 'Con tus palabras y a tu ritmo.',
      },
      step2: {
        title: 'Detecta patrones de pensamiento comunes',
        description: 'Mostramos posibles patrones y sugerimos ejercicios de cambio de perspectiva.',
      },
      step3: {
        title: 'Elige lo que se sienta verdadero y útil',
        description: 'Selecciona puntos de vista alternativos que resuenen contigo.',
      },
    },
    trust: {
      title: 'Creado con cuidado para TEP y ansiedad social',
      description: 'Basado en técnicas validadas. Tu privacidad importa: no almacenamos información personal.',
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

  const t = translations[params.locale as keyof typeof translations] || translations.en

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
