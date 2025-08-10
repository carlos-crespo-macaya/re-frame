'use client'

import { useRouter, usePathname } from 'next/navigation'
import Link from 'next/link'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { InterfaceSelector } from '@/components/ui'
import { ImportantReminder } from '@/components/ui/ImportantReminder'

// Translation dictionary
const translations = {
  en: {
    header: {
      title: 're-frame',
      subtitle: 'Cognitive reframing support',
    },
    hero: {
      title: 'Find a kinder perspective',
      description: 'Made with care for people navigating avoidant patterns.',
      body: 'Using ideas from Cognitive Behavioral Therapy (CBT), we help you notice thinking traps and try gentler, more balanced perspectives. You choose what fits.',
      learnMoreLink: 'The approach behind re-frame',
    },
    cta: {
      title: 'Start a private session',
      button: 'Start Your Session',
      privacy: "Private session — we don't store personal data.",
    },
    steps: {
      title: 'How re-frame helps',
      step1: {
        title: 'Share in your words',
        description: 'Short is fine.',
      },
      step2: {
        title: 'Notice patterns',
        description: 'We surface likely traps.',
      },
      step3: {
        title: 'Try a kinder view',
        description: 'Pick what feels true.',
      },
    },
    reminder: {
      title: 'Important reminder',
      description: "re-frame is a self-help companion that uses ideas from CBT. It isn’t psychotherapy, medical advice, or a crisis service.",
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
      description: 'Creado con cuidado para personas que transitan patrones evitativos.',
      body: 'Con ideas de la Terapia Cognitivo-Conductual (TCC), te ayudamos a notar trampas de pensamiento y a probar perspectivas más amables y equilibradas. Tú eliges lo que te sirva.',
      learnMoreLink: 'El enfoque detrás de re-frame',
    },
    cta: {
      title: '¿Listo para empezar?',
      button: 'Iniciar tu sesión',
      privacy: 'Sesión privada — no almacenamos datos personales.',
    },
    steps: {
      title: 'Cómo te ayuda re-frame',
      step1: {
        title: 'Comparte con tus palabras',
        description: 'Breve también vale.',
      },
      step2: {
        title: 'Detecta patrones',
        description: 'Mostramos trampas probables.',
      },
      step3: {
        title: 'Prueba una mirada más amable',
        description: 'Elige lo que te resulte verdadero.',
      },
    },
    reminder: {
      title: 'Recordatorio importante',
      description: 're-frame es un acompañante de autoayuda que utiliza ideas de TCC. No es psicoterapia, consejo médico ni un servicio de crisis.',
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
      showFooter={true}
      footerTranslations={t.footer}
      currentLanguage={params.locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const newPath = pathname.replace(`/${params.locale}`, `/${newLocale}`)
        router.push(newPath)
      }}
    >
      <div className="max-w-[1312px] mx-auto w-full">
        {/* Welcome section */}
        <section className="text-center mb-8 animate-fade-in">
          <h2 className="text-3xl md:text-4xl font-heading font-bold text-white mb-6">
            {t.hero.title}
          </h2>
          <p className="text-lg text-white/70 mb-4 leading-relaxed max-w-3xl mx-auto">
            {t.hero.description}
          </p>
          {/* Hero body — mobile friendly layout */}
          <p className="mx-auto text-white/70 text-[14px] leading-snug tracking-tight max-w-[36ch] sm:text-[15px] sm:leading-relaxed sm:max-w-[60ch]">
            {t.hero.body
              .split(/\.\s+/)
              .map((s: string, i: number, arr: string[]) => (
                <span key={i} className="block sm:inline">
                  {s}
                  {i < arr.length - 1 ? '. ' : ''}
                </span>
              ))}
          </p>
          <p className="text-white/45 max-w-2xl mx-auto">
            <span className="text-sm">
              <Link href={`/${params.locale}/learn-cbt`} className="text-[#aefcf5] underline hover:text-white transition-colors">{t.hero.learnMoreLink}</Link>
            </span>
          </p>
        </section>

        {/* Interface selection - Enhanced with proper hierarchy */}
        <GlassCard className="max-w-5xl mx-auto mb-12" padding="xl">
          <div className="text-center mb-8">
            <h3 className="sr-only">
              {t.cta.title}
            </h3>
          </div>
          <InterfaceSelector locale={params.locale} />
          <p className="text-[13px] text-white/40 mt-6 text-center">
            {t.cta.privacy}
          </p>
        </GlassCard>

        {/* Important reminder with crisis warning */}
        <div className="mt-8">
          <ImportantReminder locale={params.locale} variant="default" className="max-w-3xl mx-auto" />
        </div>

        {/* How it works */}
        <section className="max-w-4xl mx-auto mt-12">
          <h3 className="text-2xl font-heading font-bold text-white text-center mb-8">
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
        </section>
      </div>
    </AppLayout>
  );
}
