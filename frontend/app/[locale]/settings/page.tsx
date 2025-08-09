"use client"
import { useEffect, useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { useRecaptcha } from '@/lib/recaptcha/useRecaptcha'
import { postFeedbackApiFeedbackPost } from '@/lib/api/generated/sdk.gen'
import { FeedbackIn } from '@/lib/api/generated/types.gen'

export default function SettingsPage({ params }: { params: { locale: string } }) {
  const [optIn, setOptIn] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!
  const provider = process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER === 'enterprise' ? 'enterprise' : 'classic'
  const { ready, execute } = useRecaptcha(siteKey, provider)

  useEffect(() => {
    const v = localStorage.getItem('telemetry_opt_in')
    setOptIn(v === 'true')
  }, [])

  function saveOptIn(v: boolean) {
    setOptIn(v)
    localStorage.setItem('telemetry_opt_in', v ? 'true' : 'false')
  }

  async function sendFeedback(helpful: boolean) {
    try {
      setSubmitting(true); setMsg(null)
      if (!ready) {
        setMsg(params.locale === 'es' ? 'Cargando reCAPTCHA…' : 'Loading reCAPTCHA…')
        return
      }
      const token = await execute(`settings_${helpful ? 'yes' : 'no'}`)
      const body: FeedbackIn = {
        helpful,
        reasons: [],
        session_id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
        lang: params.locale,
        platform: 'web',
        recaptcha_token: token,
        recaptcha_action: `settings_${helpful ? 'yes' : 'no'}`,
      }
      await postFeedbackApiFeedbackPost({ requestBody: body, xObservabilityOptIn: optIn ? '1' : undefined })
      setMsg(params.locale === 'es' ? '¡Gracias por tu opinión!' : 'Thanks for the feedback!')
    } catch (e) {
      setMsg(params.locale === 'es' ? 'No se pudo enviar la opinión. Inténtalo más tarde.' : 'Could not submit feedback. Please try later.')
    } finally { setSubmitting(false) }
  }

  const t = (key: string) => {
    const dict: Record<string, Record<string, string>> = {
      en: {
        settings: 'Settings',
        helpUs: 'Help us improve anonymously',
        helpUsDesc: 'We measure anonymous technical signals (timing, error rates). No message content is stored.',
        toggle: 'Enable anonymous telemetry',
        quickFeedback: 'Quick feedback',
        yes: 'Yes',
        no: 'Not really',
        thanks: 'Thanks for the feedback!',
        failed: 'Could not submit feedback. Please try later.'
      },
      es: {
        settings: 'Ajustes',
        helpUs: 'Ayúdanos a mejorar de forma anónima',
        helpUsDesc: 'Medimos señales técnicas anónimas (tiempos, errores). No se guarda contenido de mensajes.',
        toggle: 'Activar telemetría anónima',
        quickFeedback: 'Opinión rápida',
        yes: 'Sí',
        no: 'No mucho',
        thanks: '¡Gracias por tu opinión!',
        failed: 'No se pudo enviar la opinión. Inténtalo más tarde.'
      }
    }
    return (dict[params.locale as 'en' | 'es'] || dict.en)[key]
  }

  return (
    <AppLayout
      locale={params.locale}
      showBackButton
      currentLanguage={params.locale === 'es' ? 'ES' : 'EN'}
      onLanguageChange={() => {}}
    >
      <main className="max-w-2xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-semibold text-white">{t('settings')}</h1>

        <GlassCard className="p-4">
          <h2 className="text-lg font-medium text-white mb-2">{t('helpUs')}</h2>
          <p className="text-sm text-white/70 mb-3">{t('helpUsDesc')}</p>
          <label className="inline-flex items-center gap-3 text-white">
            <input type="checkbox" checked={optIn} onChange={(event) => saveOptIn(event.target.checked)} />
            <span>{t('toggle')}</span>
          </label>
        </GlassCard>

        <GlassCard className="p-4">
          <h2 className="text-lg font-medium text-white mb-2">{t('quickFeedback')}</h2>
          <div className="flex gap-3">
            <button className="px-3 py-2 rounded bg-white/10 text-white disabled:opacity-50" disabled={submitting || !ready} onClick={() => sendFeedback(true)}>{t('yes')}</button>
            <button className="px-3 py-2 rounded bg-white/10 text-white disabled:opacity-50" disabled={submitting || !ready} onClick={() => sendFeedback(false)}>{t('no')}</button>
          </div>
          {msg && <p className="mt-3 text-sm text-white/80">{msg}</p>}
        </GlassCard>
      </main>
    </AppLayout>
  )
}


