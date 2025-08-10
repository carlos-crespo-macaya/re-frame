import { NextRequest, NextResponse } from 'next/server'
import crypto from 'node:crypto'

export const runtime = 'nodejs' // ensure Node runtime (we use node:crypto)

const SECRET = process.env.RECAPTCHA_SECRET_KEY
const DISABLED = process.env.RECAPTCHA_DISABLED === '1'
const THRESHOLD = Number(process.env.RECAPTCHA_THRESHOLD ?? '0.5')
const GATE_SECRET = process.env.RECAPTCHA_GATE_SECRET || 'dev-only-secret-change-me'

const COOKIE_BY_ACTION = {
  chat_gate: 'rf_chat_gate',
  feedback_gate: 'rf_feedback_gate',
} as const

export async function POST(req: NextRequest) {
  const { token, action } = await req.json().catch(() => ({ token: '', action: '' }))

  if (!(action in COOKIE_BY_ACTION)) {
    return NextResponse.json({ ok: false, error: 'bad_action' }, { status: 400 })
  }

  // Local/dev bypass
  if (DISABLED) {
    const res = NextResponse.json({ ok: true, disabled: true })
    setGateCookie(res, action as keyof typeof COOKIE_BY_ACTION, 2 * 60 * 60 * 1000)
    return res
  }

  if (!token) {
    return NextResponse.json({ ok: false, error: 'bad_request' }, { status: 400 })
  }
  if (!SECRET) {
    return NextResponse.json({ ok: false, error: 'missing_secret' }, { status: 500 })
  }

  // Verify with Google
  const form = new URLSearchParams({ secret: SECRET, response: token })
  const gRes = await fetch('https://www.google.com/recaptcha/api/siteverify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: form,
  })
  const data = await gRes.json()

  // Check success, action, and score
  if (!data.success || data.action !== action || (data.score ?? 1) < THRESHOLD) {
    return NextResponse.json({ ok: false, error: 'verify_failed', data }, { status: 401 })
  }

  const res = NextResponse.json({ ok: true, score: data.score })
  setGateCookie(res, action as keyof typeof COOKIE_BY_ACTION, 2 * 60 * 60 * 1000) // 2h
  return res
}

function setGateCookie(
  res: NextResponse,
  action: keyof typeof COOKIE_BY_ACTION,
  ttlMs: number
) {
  const exp = Date.now() + ttlMs
  const payload = `${action}.${exp}`
  const sig = crypto.createHmac('sha256', GATE_SECRET).update(payload).digest('base64url')
  const value = `${payload}.${sig}`
  res.cookies.set(COOKIE_BY_ACTION[action], value, {
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    path: '/',
    expires: new Date(exp),
  })
}


