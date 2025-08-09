"use client"
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { executeRecaptcha } from '@/lib/recaptcha'
import { postFeedbackApiFeedbackPost } from '@/lib/api/generated/sdk.gen'
import { FeedbackIn } from '@/lib/api/generated/types.gen'

export default function FeedbackPage({ params }: { params: { locale: string } }) {
  const router = useRouter()
  const pathname = usePathname()
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [comment, setComment] = useState('')
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!

  useEffect(() => {}, [])

  async function sendFeedback(helpful: boolean) {
    try {
      setSubmitting(true); setMsg(null)
      let token = ''
      try {
        token = await executeRecaptcha('submit_feedback', siteKey)
      } catch (err) {
        console.error('reCAPTCHA failed:', err)
        setMsg(params.locale === 'es' ? 'No se pudo validar reCAPTCHA.' : 'Could not validate reCAPTCHA.')
        return
      }
      const body: FeedbackIn = {
        helpful,
        reasons: [],
        session_id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
        lang: params.locale,
        platform: 'web',
        comment: comment || undefined,
        recaptcha_token: token,
        recaptcha_action: 'submit_feedback',
      }
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
        helpUs: 'Quick feedback',
        helpUsDesc: 'Share a brief thought (optional) and tap a thumb to send.',
        quickFeedback: 'Quick feedback',
        optionalComment: 'Optional comment',
        thumbsUp: 'Thumbs up',
        thumbsDown: 'Thumbs down',
      },
      es: {
        title: 'Opinión',
        helpUs: 'Opinión rápida',
        helpUsDesc: 'Comparte algo breve (opcional) y pulsa un pulgar para enviar.',
        quickFeedback: 'Opinión rápida',
        optionalComment: 'Comentario opcional',
        thumbsUp: 'Pulgar arriba',
        thumbsDown: 'Pulgar abajo',
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

        <GlassCard className="p-4">
          <h2 className="text-lg font-medium text-white mb-2">{t('quickFeedback')}</h2>
          <p className="text-sm text-white/70 mb-3">{t('helpUsDesc')}</p>
          <label className="block text-sm text-white/80 mb-2" htmlFor="comment">{t('optionalComment')}</label>
          <textarea id="comment" value={comment} onChange={(e)=>setComment(e.target.value)} className="w-full mb-3 rounded bg-white/5 text-white p-2 border border-white/10 focus:ring-2 focus:ring-[#aefcf5]/50" rows={3} placeholder={params.locale==='es'?'Comparte algo breve (opcional)':'Share something brief (optional)'} />
          <div className="flex gap-3">
            <button aria-label={t('thumbsUp')} title={t('thumbsUp')} className="px-3 py-2 rounded bg-[#aefcf5]/10 hover:bg-[#aefcf5]/20 text-[#aefcf5] border border-[#aefcf5]/30" disabled={submitting} onClick={() => sendFeedback(true)}>
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M2 10h4v12H2zM22 11c0-.55-.45-1-1-1h-6.31l1.1-5.27.03-.32c0-.41-.17-.79-.44-1.06L14 2 7.59 8.41C7.22 8.78 7 9.3 7 9.83V20c0 .55.45 1 1 1h9c.4 0 .75-.24.91-.59l3-7c.06-.13.09-.27.09-.41v-2z"/></svg>
            </button>
            <button aria-label={t('thumbsDown')} title={t('thumbsDown')} className="px-3 py-2 rounded bg-[#aefcf5]/10 hover:bg-[#aefcf5]/20 text-[#aefcf5] border border-[#aefcf5]/30" disabled={submitting} onClick={() => sendFeedback(false)}>
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M2 2h4v12H2zM22 9c0 .55-.45 1-1 1h-6.31l1.1 5.27.03.32c0 .41-.17.79-.44 1.06L14 20l-6.41-6.41C7.22 13.22 7 12.7 7 12.17V2c0-.55.45-1 1-1h9c.4 0 .75.24.91.59l3 7c.06.13.09.27.09.41v2z"/></svg>
            </button>
          </div>
          {msg && <p className="mt-3 text-sm text-white/80">{msg}</p>}
        </GlassCard>
      </main>
    </AppLayout>
  )
}


