"use client"
import { useEffect, useState } from 'react'
import { AppLayout } from '@/components/layout/AppLayout'
import { GlassCard } from '@/components/layout/GlassCard'
import { executeRecaptcha } from '@/lib/recaptcha'
import { getTranslations } from 'next-intl/server'

export default function SettingsPage({ params }: { params: { locale: string } }) {
  const [optIn, setOptIn] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY!

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
      const token = await executeRecaptcha('submit_feedback', siteKey)
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(optIn ? { 'X-Observability-Opt-In': '1' } : {}),
        },
        body: JSON.stringify({
          helpful,
          reasons: [],
          session_id: crypto.getRandomValues(new Uint32Array(1))[0].toString(16),
          lang: params.locale,
          platform: 'web',
          recaptcha_token: token,
          recaptcha_action: 'submit_feedback',
        })
      })
      if (!res.ok) throw new Error(await res.text())
      setMsg('Thanks for the feedback!')
    } catch (e) {
      setMsg('Could not submit feedback. Please try later.')
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
            <input type="checkbox" checked={optIn} onChange={(e) => saveOptIn(e.target.checked)} />
            <span>{t('toggle')}</span>
          </label>
        </GlassCard>

        <GlassCard className="p-4">
          <h2 className="text-lg font-medium text-white mb-2">{t('quickFeedback')}</h2>
          <div className="flex gap-3">
            <button className="px-3 py-2 rounded bg-white/10 text-white" disabled={submitting} onClick={() => sendFeedback(true)}>{t('yes')}</button>
            <button className="px-3 py-2 rounded bg-white/10 text-white" disabled={submitting} onClick={() => sendFeedback(false)}>{t('no')}</button>
          </div>
          {msg && <p className="mt-3 text-sm text-white/80">{msg}</p>}
        </GlassCard>
      </main>
    </AppLayout>
  )
}


