'use client';

import { useEffect, useRef, useState } from 'react';

export type RecaptchaProvider = 'classic' | 'enterprise';
type W = Window & { grecaptcha?: any };

function loadOnce(src: string, id: string) {
  return new Promise<void>((resolve, reject) => {
    if (document.getElementById(id)) return resolve();
    const s = document.createElement('script');
    s.id = id;
    s.async = true;
    s.defer = true;
    s.src = src;
    s.onload = () => resolve();
    s.onerror = () => reject(new Error('Failed to load reCAPTCHA script'));
    document.head.appendChild(s);
  });
}

export function useRecaptcha(siteKey?: string, provider: RecaptchaProvider = 'classic') {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loader = useRef<Promise<void> | null>(null);

  useEffect(() => {
    if (!siteKey) {
      setError('Missing reCAPTCHA site key');
      return;
    }
    setError(null);

    if (!loader.current) {
      const src =
        provider === 'enterprise'
          ? `https://www.google.com/recaptcha/enterprise.js?render=${encodeURIComponent(siteKey)}`
          : `https://www.google.com/recaptcha/api.js?render=${encodeURIComponent(siteKey)}`;

      loader.current = loadOnce(src, provider === 'enterprise' ? 'rc-enterprise' : 'rc-classic')
        .then(() => {
          const g = (window as W).grecaptcha;
          const api = provider === 'enterprise' ? g?.enterprise : g;
          if (!api) throw new Error('grecaptcha API missing on window');
          api.ready(() => setReady(true));
        })
        .catch((e) => setError(e instanceof Error ? e.message : String(e)));
    }
  }, [siteKey, provider]);

  const execute = async (action: string) => {
    if (!siteKey) throw new Error('Missing reCAPTCHA site key');
    if (!loader.current) throw new Error('reCAPTCHA not initialized');
    await loader.current;
    const g = (window as W).grecaptcha;
    const api = provider === 'enterprise' ? g?.enterprise : g;
    if (!api?.execute) throw new Error('reCAPTCHA not ready');
    return api.execute(siteKey, { action });
  };

  return { ready, execute, error };
}

export async function prefetchToken(siteKey: string, provider: RecaptchaProvider, action = 'prefetch') {
  const g = (window as W).grecaptcha;
  const api = provider === 'enterprise' ? g?.enterprise : g;
  if (!api?.execute) return;
  try { await api.execute(siteKey, { action }); } catch {/* best effort */}
}


