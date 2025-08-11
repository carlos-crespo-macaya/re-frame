import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const locales = ['en', 'es']
function escapeRegexSegment(input: string): string {
  return input.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
const LOCALE_GROUP = locales.map(escapeRegexSegment).join('|')
const defaultLocale = 'en'

function getLocale(request: NextRequest): string {
  // Check if there's a locale in the pathname
  const pathname = request.nextUrl.pathname
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  if (pathnameHasLocale) {
    return pathname.split('/')[1]
  }

  // Check Accept-Language header
  const acceptLanguage = request.headers.get('Accept-Language')
  if (acceptLanguage) {
    const languages = acceptLanguage.split(',')
    for (const lang of languages) {
      const locale = lang.split('-')[0].trim()
      if (locales.includes(locale)) {
        return locale
      }
    }
  }

  return defaultLocale
}

export function middleware(request: NextRequest) {
  return handleMiddleware(request)
}

export const config = {
  matcher: [
    // Skip all internal paths (_next, api, etc.)
    '/((?!_next|api|favicon.ico|.*\\..*).*)',
  ],
}

// --- reCAPTCHA gate integration (edge-safe HMAC verification) ---
// Temporary kill-switch: default to disabled unless explicitly set to '0'
const DISABLED = (process.env.RECAPTCHA_DISABLED ?? '1') === '1'
const GATE_SECRET = process.env.RECAPTCHA_GATE_SECRET || 'dev-only-secret-change-me'

function base64url(ab: ArrayBuffer) {
  let str = ''
  const bytes = new Uint8Array(ab)
  for (let i = 0; i < bytes.length; i++) str += String.fromCharCode(bytes[i])
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '')
}

async function hmac(payload: string) {
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(GATE_SECRET),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )
  const sig = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(payload))
  return base64url(sig)
}

async function validGate(value: string | undefined, expected: 'chat_gate' | 'feedback_gate') {
  if (!value) return false
  const parts = value.split('.')
  if (parts.length !== 3) return false
  const [action, expStr, sig] = parts
  if (action !== expected) return false
  const exp = Number(expStr)
  if (!Number.isFinite(exp) || Date.now() > exp) return false
  const payload = `${action}.${exp}`
  const expect = await hmac(payload)
  return sig === expect
}

async function handleMiddleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname

  // Check if the pathname already has a locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  )

  // Redirect if no locale
  if (!pathnameHasLocale) {
    const locale = getLocale(request)
    const newUrl = new URL(`/${locale}${pathname}`, request.url)
    return NextResponse.redirect(newUrl)
  }

  // Normalize cross-locale redirect on gate page itself to avoid language flips
  {
    const url = request.nextUrl
    const locale = pathname.split('/')[1] || 'en'
    if (new RegExp(`^\/(${LOCALE_GROUP})\/gate$`).test(pathname)) {
      const r = url.searchParams.get('redirect')
      if (r && r.startsWith('/')) {
        const segs = r.split('/')
        const hasLocale = segs[1] && locales.includes(segs[1])
        if (hasLocale && segs[1] !== locale) {
          segs[1] = locale
          const dest = request.nextUrl.clone()
          dest.searchParams.set('redirect', segs.join('/'))
          return NextResponse.redirect(dest)
        }
        if (!hasLocale) {
          const dest = request.nextUrl.clone()
          dest.searchParams.set('redirect', `/${locale}${r}`)
          return NextResponse.redirect(dest)
        }
      }
    }
  }

  // reCAPTCHA gate checks (skip when disabled)
  if (!DISABLED) {
    const url = request.nextUrl
    const locale = pathname.split('/')[1] || 'en'
    const search = url.searchParams.toString()

    // Gate /chat
    if (new RegExp(`^\/(${LOCALE_GROUP})\/chat(\/|$)`).test(pathname)) {
      const ok = await validGate(request.cookies.get('rf_chat_gate')?.value, 'chat_gate')
      if (!ok) {
        return createGateRedirect(request, locale, pathname, search, 'chat_gate')
      }
    }

    // Gate /feedback
    if (new RegExp(`^\/(${LOCALE_GROUP})\/feedback(\/|$)`).test(pathname)) {
      const ok = await validGate(request.cookies.get('rf_feedback_gate')?.value, 'feedback_gate')
      if (!ok) {
        return createGateRedirect(request, locale, pathname, search, 'feedback_gate')
      }
    }
  }

  return NextResponse.next()
}

function createGateRedirect(
  req: NextRequest,
  locale: string,
  pathname: string,
  search: string,
  action: 'chat_gate' | 'feedback_gate'
) {
  const dest = req.nextUrl.clone()
  dest.pathname = `/${locale}/gate`
  dest.searchParams.set('action', action)
  dest.searchParams.set('redirect', pathname + (search ? `?${search}` : ''))
  return NextResponse.redirect(dest)
}