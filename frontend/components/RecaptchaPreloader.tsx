'use client';
import { useEffect } from 'react';
import { useRecaptcha, prefetchToken } from '@/lib/recaptcha/useRecaptcha';

export default function RecaptchaPreloader() {
  const siteKey = process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY;
  const provider = process.env.NEXT_PUBLIC_RECAPTCHA_PROVIDER === 'enterprise' ? 'enterprise' : 'classic';
  const { ready } = useRecaptcha(siteKey, provider);

  useEffect(() => {
    if (ready && siteKey) prefetchToken(siteKey, provider, 'preload');
  }, [ready, siteKey, provider]);

  return null;
}


