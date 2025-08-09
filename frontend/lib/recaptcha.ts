export async function executeRecaptcha(action: string, siteKey: string): Promise<string> {
  if (typeof window === 'undefined') {
    throw new Error('executeRecaptcha must be called in the browser')
  }
  if (!siteKey) {
    throw new Error('Missing NEXT_PUBLIC_RECAPTCHA_SITE_KEY')
  }
  const rawProvider = (process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER || 'enterprise').toLowerCase()
  const provider: 'enterprise' | 'classic' = rawProvider === 'classic' ? 'classic' : 'enterprise'

  await new Promise<void>((resolve) => {
    const w = window as any
    if (provider === 'classic') {
      if (w.grecaptcha) return resolve()
      const s = document.createElement('script')
      s.src = 'https://www.google.com/recaptcha/api.js?render=' + siteKey
      s.async = true
      s.defer = true
      s.onload = () => resolve()
      document.head.appendChild(s)
      return
    }
    // enterprise
    if (w.grecaptcha?.enterprise) return resolve()
    const s = document.createElement('script')
    s.src = 'https://www.google.com/recaptcha/enterprise.js?render=' + siteKey
    s.async = true
    s.defer = true
    s.onload = () => resolve()
    document.head.appendChild(s)
  })

  const w = window as any
  if (provider === 'classic') {
    if (!w.grecaptcha?.ready || !w.grecaptcha?.execute) {
      throw new Error('reCAPTCHA v3 (classic) not available on window')
    }
    await new Promise<void>((resolve) => w.grecaptcha.ready(resolve))
    return w.grecaptcha.execute(siteKey, { action })
  }
  if (!w.grecaptcha?.enterprise?.ready || !w.grecaptcha?.enterprise?.execute) {
    throw new Error('reCAPTCHA Enterprise not available on window')
  }
  await new Promise<void>((resolve) => w.grecaptcha.enterprise.ready(resolve))
  return w.grecaptcha.enterprise.execute(siteKey, { action })
}


