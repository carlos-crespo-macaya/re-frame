'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Privacy() {
  const pathname = usePathname()
  const first = pathname.split('/')[1] || ''
  const locale = first === 'es' ? 'es' : 'en'
  const homeHref = locale === 'en' || locale === 'es' ? `/${locale}` : '/'

  const t = {
    en: {
      subtitle: 'Cognitive reframing support',
      title: '🔒 Privacy',
      leadStart: 'We believe your reflections belong to ',
      leadStrong: 'you alone',
      tail: "We'll never sell or share your words. Read the full policy at ",
      back: '← Return to re-frame'
    },
    es: {
      subtitle: 'Apoyo para el replanteamiento cognitivo',
      title: '🔒 Privacidad',
      leadStart: 'Creemos que tus reflexiones te pertenecen ',
      leadStrong: 'solo a ti',
      tail: 'Nunca venderemos ni compartiremos tus palabras. Lee la política completa en ',
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
                {t.subtitle}
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
              {t.title}
            </h1>
            
            <p className="text-lg text-[#999999] leading-relaxed mb-8">
              {t.leadStart}<strong className="text-[#EDEDED]">{t.leadStrong}</strong>.
            </p>

            <ul className="space-y-3 text-[#999999] mb-8">
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'Sin píxeles de seguimiento, sin anuncios.' : 'No tracking pixels, no ads.'}
                  </strong>
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'Anónimo por defecto.' : 'Anonymous by default.'}
                  </strong>{' '}
                  {locale === 'es'
                    ? 'Si no creas una cuenta, solo almacenamos un ID de sesión aleatorio y tu texto (para que la app pueda responder).'
                    : "If you don't create an account, we store only a random session ID and your text (so the app can respond)."}
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'Cuenta opcional = datos opcionales.' : 'Optional account = optional data.'}
                  </strong>{' '}
                  {locale === 'es'
                    ? 'Regístrate (email o Google) solo si quieres guardar tus entradas entre dispositivos.'
                    : 'Sign up (email or Google) only if you want to save entries across devices.'}
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'Elimina cuando quieras.' : 'Delete anytime.'}
                  </strong>{' '}
                  {locale === 'es'
                    ? 'Un clic en <strong className="text-[#EDEDED]">Ajustes → Eliminar datos</strong> borra cada entrada, embedding vectorial y registro.'
                    : 'One click in <strong className="text-[#EDEDED]">Settings → Delete data</strong> wipes every entry, vector embedding, and log.'}
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'TLS de extremo a extremo.' : 'End-to-end TLS.'}
                  </strong>{' '}
                  {locale === 'es'
                    ? 'El tráfico está cifrado en tránsito; el texto almacenado está cifrado en reposo.'
                    : 'Traffic is encrypted in transit; stored text is encrypted at rest.'}
                </div>
              </li>
              <li className="flex items-start">
                <span className="mr-2">•</span>
                <div>
                  <strong className="text-[#EDEDED]">
                    {locale === 'es' ? 'Código abierto.' : 'Open source.'}
                  </strong>{' '}
                  {locale === 'es'
                    ? 'Nuestro código y modelo de seguridad son públicos para que cualquiera pueda auditarlos.'
                    : 'Our code and security model are public so anyone can audit them.'}
                </div>
              </li>
            </ul>

            <p className="text-base text-[#999999] leading-relaxed">
              {locale === 'es'
                ? 'Nunca venderemos ni compartiremos tus palabras.'
                : "We’ll never sell or share your words."}
            </p>

            <div className="mt-12 text-center">
              <Link href={homeHref} className="inline-flex items-center gap-2 text-brand-green-400 hover:text-brand-green-300 underline">
                {t.back}
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
