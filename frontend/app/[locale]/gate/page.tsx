'use client'

import { useSearchParams, useRouter, useParams } from 'next/navigation'
import Script from 'next/script'
import { useMemo, useState } from 'react'
import { GlassCard } from '@/components/layout/GlassCard'

declare global {
  interface Window { grecaptcha?: any }
}

const SITE_KEY = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY as string | undefined

function sanitizeRedirect(raw: string | null, locale: 'en' | 'es'): string {
  if (!raw) return `/${locale}`
  try {
    const u = new URL(raw, typeof window !== 'undefined' ? window.location.origin : 'https://local')
    let path = u.pathname
    if (!path.startsWith('/')) path = `/${path}`
    const segments = path.split('/')
    const hasLocale = segments[1] === 'en' || segments[1] === 'es'
    if (hasLocale) {
      if (segments[1] !== locale) segments[1] = locale
      path = segments.join('/')
    } else {
      path = `/${locale}${path}`
    }
    return `${path}${u.search}`
  } catch {
    // Fallback for non-URL strings
    if (!raw.startsWith('/')) return `/${locale}`
    const segments = raw.split('/')
    if (segments[1] === 'en' || segments[1] === 'es') {
      segments[1] = locale
      return segments.join('/')
    }
    return `/${locale}${raw}`
  }
}

export default function GatePage() {
  const sp = useSearchParams()
  const router = useRouter()
  const { locale } = useParams<{ locale: 'en' | 'es' }>()
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const action = (sp.get('action') as 'chat_gate' | 'feedback_gate') ?? 'chat_gate'
  const redirect = useMemo(() => {
    const raw = sp.get('redirect')
    let decoded: string | null = raw
    if (raw && /%2F/i.test(raw)) {
      try { decoded = decodeURIComponent(raw) } catch { decoded = raw }
    }
    return sanitizeRedirect(decoded, locale)
  }, [sp, locale])

  async function handleVerify() {
    setErr(null); setLoading(true)
    try {
      // Local/dev bypass: if no site key, just call server (it may be disabled)
      let token = ''
      if (SITE_KEY) {
        await new Promise<void>(resolve => window.grecaptcha.ready(() => resolve()))
        token = await window.grecaptcha.execute(SITE_KEY, { action })
      }
      const r = await fetch('/api/recaptcha/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, action }),
      })
      if (!r.ok) throw new Error('verify_failed')
      // Primary: SPA navigation
      router.replace(redirect)
      // Fallback: ensure navigation even if SPA router stalls (rare)
      setTimeout(() => {
        if (typeof window !== 'undefined' && window.location.pathname !== redirect) {
          try { window.location.assign(redirect) } catch { /* noop */ }
        }
      }, 800)
    } catch {
      setErr(locale === 'es'
        ? 'No se pudo verificar reCAPTCHA. Inténtalo de nuevo.'
        : 'reCAPTCHA check failed. Please try again.')
      setLoading(false)
    }
  }

  const strings = {
    title: locale === 'es' ? 'Comprobación rápida' : 'Quick check',
    body: locale === 'es'
      ? (action === 'feedback_gate'
          ? 'Antes de opinar, verifica que eres una persona.'
          : 'Antes de chatear, verifica que eres una persona.')
      : (action === 'feedback_gate'
          ? 'Before leaving feedback, please verify you’re human.'
          : 'Before starting chat, please verify you’re human.'),
    button: locale === 'es'
      ? (action === 'feedback_gate' ? 'Verificar para opinar' : 'Verificar para chatear')
      : (action === 'feedback_gate' ? 'Verify to give feedback' : 'Verify to chat'),
    checking: locale === 'es' ? 'Comprobando…' : 'Checking…',
    notice: locale === 'es'
      ? <>Este sitio está protegido por reCAPTCHA y se aplican la <a className="underline" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Política de Privacidad</a> y las <a className="underline" href="https://policies.google.com/terms" target="_blank" rel="noopener noreferrer">Condiciones del Servicio</a> de Google.</>
      : <>This site is protected by reCAPTCHA and the Google <a className="underline" href="https://policies.google.com/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a> and <a className="underline" href="https://policies.google.com/terms" target="_blank" rel="noopener noreferrer">Terms of Service</a> apply.</>,
  }

  return (
    <>
      {SITE_KEY && (
        <Script
          src={`https://www.google.com/recaptcha/api.js?render=${SITE_KEY}`}
          strategy="afterInteractive"
        />
      )}
      <div className="max-w-[620px] mx-auto mt-10">
        <GlassCard padding="xl" className="text-center">
          <h1 className="text-xl font-heading font-semibold text-white mb-2">
            {strings.title}
          </h1>
          <p className="text-white/70 mb-4">{strings.body}</p>
          <button
            onClick={handleVerify}
            disabled={loading}
            className="inline-flex items-center justify-center px-4 py-2 rounded-xl bg-[#aefcf5] text-[#03141d] font-medium hover:opacity-90 disabled:opacity-60"
          >
            {loading ? strings.checking : strings.button}
          </button>
          <p className="mt-3 text-xs text-neutral-400">{strings.notice}</p>
        </GlassCard>
      </div>
    </>
  )
}


