export async function executeRecaptcha(action: string, siteKey: string): Promise<string> {
  await new Promise<void>((resolve) => {
    const w = window as any
    if (w.grecaptcha?.enterprise) return resolve()
    const s = document.createElement('script')
    s.src = 'https://www.google.com/recaptcha/enterprise.js?render=' + siteKey
    s.async = true
    s.defer = true
    s.onload = () => resolve()
    document.head.appendChild(s)
  })
  const w = window as any
  return await w.grecaptcha.enterprise.execute(siteKey, { action })
}


