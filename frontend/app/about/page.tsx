'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function About() {
  const pathname = usePathname()
  const first = pathname.split('/')[1] || ''
  const locale = first === 'es' ? 'es' : 'en'
  const homeHref = locale === 'en' || locale === 'es' ? `/${locale}` : '/'

  const t = {
    en: {
      subtitle: 'Cognitive reframing support',
      title: 'ℹ️ About re-frame',
      missionLabel: 'Mission',
      missionLead:
        'give people who struggle with avoidant patterns a gentle way to challenge harsh thoughts—without shame, ads, or data mining.',
      whatIs: 'What it is:',
      whatIsBody:
        'a therapeutic framework-informed cognitive restructuring tool that spots thinking traps (catastrophising, mind-reading, etc.) and offers kinder perspectives.',
      whatIsnt: "What it isn't:",
      whatIsntBody:
        'full psychotherapy, medical advice, or a crisis service.',
      who: 'Who builds it:',
      whoBody:
        "just me—Carlos, a software engineer who's lived with AvPD for years and is investing my own time, skills, and will to create the tool I wish I'd had.",
      whyOpen: 'Why open source:',
      whyOpenBody:
        'transparency builds trust; anyone can inspect or improve the code.',
      roadmap: 'Roadmap:',
      roadmapBody:
        'opt-in community peer support, progress journaling, therapist hand-off export.',
      contactQ:
        'Questions? Reach me at ',
      back: '← Return to re-frame'
    },
    es: {
      subtitle: 'Apoyo para el replanteamiento cognitivo',
      title: 'ℹ️ Acerca de re-frame',
      missionLabel: 'Misión',
      missionLead:
        'ofrecer a quienes luchan con patrones evitativos una forma amable de cuestionar pensamientos duros—sin vergüenza, anuncios ni explotación de datos.',
      whatIs: 'Qué es:',
      whatIsBody:
        'una herramienta de reestructuración cognitiva inspirada en marcos terapéuticos que detecta trampas de pensamiento (catastrofismo, lectura de mente, etc.) y propone perspectivas más amables.',
      whatIsnt: 'Qué no es:',
      whatIsntBody:
        'psicoterapia completa, consejo médico ni servicio de crisis.',
      who: 'Quién lo construye:',
      whoBody:
        'solo yo—Carlos, ingeniero de software que convive con TPA y dedica su tiempo y habilidades para crear la herramienta que me hubiera gustado tener.',
      whyOpen: 'Por qué código abierto:',
      whyOpenBody:
        'la transparencia genera confianza; cualquiera puede revisar o mejorar el código.',
      roadmap: 'Hoja de ruta:',
      roadmapBody:
        'apoyo entre pares opcional, diario de progreso, exportación para derivación a terapeuta.',
      contactQ: '¿Dudas? Escríbeme a ',
      back: '← Volver a re-frame'
    }
  }[locale]

  return (
    <>
      {/* Header */}
      <header className="relative bg-gradient-to-b from-[#1D1F1E] to-transparent">
        <div className="container-safe py-8">
          <div className="flex items-start justify-between">
            <div>
              <Link href={homeHref} className="inline-block">
                <h1 className="text-2xl font-heading font-semibold text-brand-green-400 hover:text-brand-green-300 transition-colors">
                  re-frame
                </h1>
              </Link>
              <p className="text-sm text-[#999999] mt-1">
                Cognitive reframing support
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        <div className="container-safe py-8 md:py-12">
          <article className="max-w-3xl mx-auto">
            <h1 className="text-[32px] font-semibold text-[#EDEDED] mb-8">
              ℹ️ About re-frame
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              <strong className="text-[#EDEDED]">Mission</strong> – give people who struggle with avoidant patterns a gentle way to challenge harsh thoughts—without shame, ads, or data mining.
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">What it is:</strong> a therapeutic framework-informed cognitive restructuring tool that spots thinking traps (catastrophising, mind-reading, etc.) and offers kinder perspectives.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">What it isn&apos;t:</strong> full psychotherapy, medical advice, or a crisis service.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Who builds it:</strong> just me—<strong className="text-[#EDEDED]">Carlos</strong>, a software engineer who&apos;s lived with AvPD for years and is investing my own time, skills, and will to create the tool I wish I&apos;d had.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Why open source:</strong> transparency builds trust; anyone can inspect or improve the code.</div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div><strong className="text-[#EDEDED]">Roadmap:</strong> opt-in community peer support, progress journaling, therapist hand-off export.</div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              Questions? Reach me at <a href="mailto:hello@re-frame.social" className="text-[#EDEDED] hover:text-brand-green-400 underline">hello@re-frame.social</a>.
            </p>

            <div className="mt-12 text-center">
              <Link href={homeHref} className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                ← Return to re-frame
              </Link>
            </div>
          </article>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-[#3a3a3a]">
        <div className="container-safe py-8">
          <div className="flex flex-col items-center gap-4">
            <h2 className="text-xl font-heading font-semibold text-brand-green-400">
              re-frame
            </h2>
            <p className="text-xs text-[#999999]">
              © 2024 re-frame.social
            </p>
          </div>
        </div>
      </footer>
    </>
  );
}
