"use client"
import { useEffect, useState } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { ThumbsUpIcon, ThumbsDownIcon } from '@/components/icons'
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
      // Clear form state after successful submission
      setComment('')
      setSelected(null)
    } catch {
      setMsg(params.locale === 'es' ? 'No se pudo enviar la opinión. Inténtalo más tarde.' : 'Could not submit feedback. Please try later.')
    } finally { setSubmitting(false) }
  }

  const t = (key: string) => {
    const dict: Record<'en' | 'es', Record<string, string>> = {
      en: {
        title: 'Feedback',
        helpUs: 'Help shape what’s next',
        optionalComment: 'Add a note… (optional)',
        thumbsUp: 'Thumbs up',
        thumbsDown: 'Thumbs down',
        send: 'Send feedback',
        sending: 'Sending…',
      },
      es: {
        title: 'Opinión',
        helpUs: 'Ayúdanos a mejorar',
        optionalComment: 'Añade una nota… (opcional)',
        thumbsUp: 'Pulgar arriba',
        thumbsDown: 'Pulgar abajo',
        send: 'Enviar opinión',
        sending: 'Enviando…',
      },
    }
    return (dict[params.locale as 'en' | 'es'] || dict.en)[key] ?? key
  }

  return (
    <AppLayout
      locale={params.locale}
      showBackButton
      showFeedbackButton={false}
      showFooter={true}
      currentLanguage={params.locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={(newLocale) => {
        const next = pathname.replace(`/${params.locale}`, `/${newLocale}`)
        router.push(next)
      }}
    >
      <div className="max-w-md mx-auto w-full px-4 sm:px-6">
        <div className="text-center mb-8 mt-8 sm:mt-12">
          <h1 className="text-3xl sm:text-4xl font-heading font-bold text-white mb-3">{t('title')}</h1>
        </div>

        <GlassCard className="p-0 overflow-hidden">
          <div className="px-6 py-5 sm:px-8 sm:py-6 bg-gradient-to-br from-white/5 to-white/[0.02] border-b border-white/10">
            <h2 className="text-base font-medium text-center text-white">{t('helpUs')}</h2>
          </div>

          <div className="p-6 sm:p-8 space-y-6">
            {/* Feedback buttons */}
            <div className="flex justify-center gap-4">
              <button
                type="button"
                aria-label={t('thumbsUp')}
                title={t('thumbsUp')}
                onClick={() => { setSelected('up'); sendFeedback(true) }}
                disabled={submitting || !ready}
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center 
                  transition-all duration-200 transform
                  ${selected === 'up'
                    ? 'bg-[#aefcf5] text-[#03141d] scale-110 shadow-lg shadow-[#aefcf5]/20'
                    : 'bg-white/5 text-white/70 hover:bg-white/10 hover:scale-105 hover:text-white'
                  } 
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
              >
                <ThumbsUpIcon className="w-8 h-8 sm:w-10 sm:h-10" />
              </button>

              <button
                type="button"
                aria-label={t('thumbsDown')}
                title={t('thumbsDown')}
                onClick={() => { setSelected('down'); sendFeedback(false) }}
                disabled={submitting || !ready}
                className={`
                  w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center 
                  transition-all duration-200 transform
                  ${selected === 'down'
                    ? 'bg-red-500/80 text-white scale-110 shadow-lg shadow-red-500/20'
                    : 'bg-white/5 text-white/70 hover:bg-white/10 hover:scale-105 hover:text-white'
                  } 
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
              >
                <ThumbsDownIcon className="w-8 h-8 sm:w-10 sm:h-10" />
              </button>
            </div>

            {/* Optional comment */}
            <div className="space-y-2">
              <textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className={`
                  w-full rounded-xl bg-white/5 text-white px-4 py-3 
                  border transition-all duration-200
                  ${comment
                    ? 'border-[#aefcf5]/30 bg-white/[0.07]'
                    : 'border-white/10 focus:border-[#aefcf5]/30'
                  }
                  focus:outline-none focus:ring-2 focus:ring-[#aefcf5]/20 focus:bg-white/[0.07]
                  placeholder:text-white/30 resize-none
                `}
                rows={4}
                placeholder={t('optionalComment')}
              />
            </div>

            {/* Status message */}
            {msg && (
              <div className={`
                text-center py-3 px-4 rounded-xl text-sm font-medium
                ${msg.includes('Gracias') || msg.includes('Thanks')
                  ? 'bg-[#aefcf5]/10 text-[#aefcf5] border border-[#aefcf5]/20'
                  : 'bg-red-500/10 text-red-400 border border-red-500/20'
                }
              `}>
                {msg}
              </div>
            )}
          </div>
        </GlassCard>
      </div>
    </AppLayout>
  )
}


