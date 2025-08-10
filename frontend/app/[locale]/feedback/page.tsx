"use client"
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'
import { postFeedbackApiFeedbackPost } from '@/lib/api/generated/sdk.gen'
import { FeedbackIn } from '@/lib/api/generated/types.gen'

export default function FeedbackPage({ params }: { params: { locale: string } }) {
  const router = useRouter()
  const pathname = usePathname()
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [comment, setComment] = useState('')
  const [selected, setSelected] = useState<null | 'up' | 'down'>(null)
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY
  const provider = process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER === 'enterprise' ? 'enterprise' : 'classic'
  const { ready, execute, error } = useRecaptcha(siteKey, provider)
  useEffect(() => { if (error) console.warn('reCAPTCHA init failed:', error) }, [error])

  async function sendFeedback(helpful: boolean) {
    try {
      setSubmitting(true); setMsg(null)
      let token = ''
      try {
        if (!ready) {
          setMsg(params.locale === 'es' ? 'Cargando reCAPTCHA…' : 'Loading reCAPTCHA…')
          return
        }
        token = await execute(`feedback_${helpful ? 'up' : 'down'}`)
      } catch (err) {
        console.error('reCAPTCHA failed:', err)
        setMsg(params.locale === 'es' ? 'No se pudo validar reCAPTCHA.' : 'Could not validate reCAPTCHA.')
        return
      }
      const body = {
        helpful,
        reasons: [],
        session_id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
        lang: params.locale,
        platform: 'web',
        comment: comment || undefined,
        recaptcha_token: token,
          recaptcha_action: `feedback_${helpful ? 'up' : 'down'}`,
        // Enhanced metadata from the page
        source: 'feedback_page',
        page_path: typeof window !== 'undefined' ? window.location.pathname : undefined,
      } as unknown as FeedbackIn
      await postFeedbackApiFeedbackPost({ requestBody: body })
      setMsg(params.locale === 'es' ? '¡Gracias por tu opinión!' : 'Thanks for the feedback!')
    } catch {
      setMsg(params.locale === 'es' ? 'No se pudo enviar la opinión. Inténtalo más tarde.' : 'Could not submit feedback. Please try later.')
    } finally { setSubmitting(false) }
  }

  const t = (key: string) => {
    const dict: Record<string, Record<string, string>> = {
      en: {
        title: 'Feedback',
        helpUs: 'We’d love your thoughts',
        helpUsDesc: 'How was your experience? Leave a quick rating and an optional note.',
        quickFeedback: 'Quick feedback',
        optionalComment: 'Optional note',
        thumbsUp: 'Thumbs up',
        thumbsDown: 'Thumbs down',
        send: 'Send',
        sending: 'Sending…',
      },
      es: {
        title: 'Opinión',
        helpUs: 'Nos encantaría tu opinión',
        helpUsDesc: '¿Cómo fue tu experiencia? Deja una valoración rápida y una nota opcional.',
        quickFeedback: 'Opinión rápida',
        optionalComment: 'Nota opcional',
        thumbsUp: 'Pulgar arriba',
        thumbsDown: 'Pulgar abajo',
        send: 'Enviar',
        sending: 'Enviando…',
      }
    }
    return (dict[params.locale as 'en' | 'es'] || dict.en)[key]
  }

  return (
    <AppLayout
      locale={params.locale}
      showBackButton
      currentLanguage={params.locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const next = pathname.replace(`/${params.locale}`, `/${newLocale}`)
        router.push(next)
      }}
    >
      <main className="max-w-2xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-semibold text-white">{t('title')}</h1>

        <GlassCard className="p-0 overflow-hidden">
          <div className="px-5 py-5 sm:px-6 sm:py-6 bg-gradient-to-br from-[#0A2A30] to-[#102B33] border-b border-white/10">
            <h2 className="text-lg font-medium text-white">{t('helpUs')}</h2>
            <p className="text-sm text-white/70 mt-1">{t('helpUsDesc')}</p>
          </div>

          <div className="p-5 sm:p-6">
            <div className="flex items-center gap-3 mb-4">
              <button
                aria-label={t('thumbsUp')}
                title={t('thumbsUp')}
                onClick={() => { setSelected('up'); sendFeedback(true) }}
                disabled={submitting || !ready}
                className={`w-12 h-12 rounded-2xl flex items-center justify-center ring-1 transition-all ${selected==='up' ? 'bg-[#9BF7EB] text-[#002e34] ring-[#9BF7EB]/40' : 'bg-white/5 text-white ring-white/10 hover:bg-white/10'} disabled:opacity-50`}
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path d="M2 10h4v12H2zM22 11c0-.55-.45-1-1-1h-6.31l1.1-5.27.03-.32c0-.41-.17-.79-.44-1.06L14 2 7.59 8.41C7.22 8.78 7 9.3 7 9.83V20c0 .55.45 1 1 1h9c.4 0 .75-.24.91-.59l3-7c.06-.13.09-.27.09-.41v-2z"/></svg>
              </button>
              <button
                aria-label={t('thumbsDown')}
                title={t('thumbsDown')}
                onClick={() => { setSelected('down'); sendFeedback(false) }}
                disabled={submitting || !ready}
                className={`w-12 h-12 rounded-2xl flex items-center justify-center ring-1 transition-all ${selected==='down' ? 'bg-[#F59E0B] text-[#0b140f] ring-[#F59E0B]/40' : 'bg-white/5 text-white ring-white/10 hover:bg-white/10'} disabled:opacity-50`}
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor"><path d="M2 2h4v12H2zM22 9c0 .55-.45 1-1 1h-6.31l1.1 5.27.03.32c0 .41-.17.79-.44 1.06L14 20l-6.41-6.41C7.22 13.22 7 12.7 7 12.17V2c0-.55.45-1 1-1h9c.4 0 .75.24.91.59l3 7c.06.13.09.27.09.41v2z"/></svg>
              </button>
            </div>

            <label className="block text-sm text-white/80 mb-2" htmlFor="comment">{t('optionalComment')}</label>
            <textarea
              id="comment"
              value={comment}
              onChange={(e)=>setComment(e.target.value)}
              className="w-full mb-3 rounded-2xl bg-white/5 text-white px-4 py-3 border border-white/10 focus:ring-2 focus:ring-[#9BF7EB]/50 placeholder:text-white/40"
              rows={3}
              placeholder={params.locale==='es'?'Comparte algo breve (opcional)':'Share something brief (optional)'}
            />
            {msg && <p className="mt-1 text-sm text-white/80">{msg}</p>}
          </div>
        </GlassCard>
      </main>
    </AppLayout>
  )
}


