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
          bg-[#1a1a1a]
          border border-[#3a3a3a]
          rounded-md
          px-3 py-1.5 pr-8
          text-sm
          text-[#999999]
          cursor-pointer
          hover:border-[#4a4a4a]
          hover:text-[#EDEDED]
          focus:outline-none
          focus:ring-1
          focus:ring-brand-green-400/50
          focus:border-brand-green-400/50
          disabled:opacity-50
          disabled:cursor-not-allowed
          transition-all duration-200
        "
        aria-label="Change language"
      >
        {routing.locales.map((loc) => (
          <option key={loc} value={loc} className="bg-[#1a1a1a]">
            {loc === 'en' ? 'EN' : 'ES'}
          </option>
        ))}
      </select>
      <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2">
        <svg 
          className="h-3.5 w-3.5 text-[#666666]" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M19 9l-7 7-7-7" 
          />
        </svg>
      </div>
      {isPending && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#1a1a1a]/80 rounded-md backdrop-blur-sm">
          <div className="animate-spin h-3 w-3 border border-brand-green-400 border-t-transparent rounded-full" />
        </div>
      )}
    </div>
  );
}