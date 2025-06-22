'use client';

import { useTransition } from 'react';
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from '@/i18n/routing';
import { routing } from '@/i18n/routing';

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();
  const [isPending, startTransition] = useTransition();

  const handleChange = (newLocale: string) => {
    startTransition(() => {
      // Use the router from next-intl which handles locale switching
      router.replace(pathname, {locale: newLocale});
    });
  };

  return (
    <div className="relative inline-block">
      <label htmlFor="language-select" className="sr-only">
        Select Language
      </label>
      <select
        id="language-select"
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        disabled={isPending}
        className="
          appearance-none
          bg-surface-secondary
          border border-border-primary
          rounded-lg
          px-3 py-2 pr-8
          text-sm
          cursor-pointer
          focus:outline-none
          focus:ring-2
          focus:ring-accent-primary
          focus:border-transparent
          disabled:opacity-50
          disabled:cursor-not-allowed
          transition-colors
        "
        aria-label="Change language"
      >
        {routing.locales.map((loc) => (
          <option key={loc} value={loc}>
            {loc === 'en' ? 'English' : 'Español'}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-text-secondary">
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
      {isPending && (
        <div className="absolute inset-0 flex items-center justify-center bg-surface-secondary/50 rounded-lg">
          <div className="animate-spin h-4 w-4 border-2 border-accent-primary border-t-transparent rounded-full" />
        </div>
      )}
    </div>
  );
}