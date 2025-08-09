export async function executeRecaptcha(action: string, siteKey: string): Promise<string> {
  const provider = (process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER || 'enterprise').toLowerCase()

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
    return await w.grecaptcha.execute(siteKey, { action })
  }
  return await w.grecaptcha.enterprise.execute(siteKey, { action })
}


