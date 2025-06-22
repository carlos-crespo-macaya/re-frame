import {notFound} from 'next/navigation';
import {getRequestConfig} from 'next-intl/server';

// Can be imported from a shared config
export const locales = ['en', 'es'] as const;
export type Locale = (typeof locales)[number];

export default getRequestConfig(async ({locale}) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as any)) notFound();

  return {
    messages: {
      common: (await import(`./locales/${locale}/common.json`)).default,
      home: (await import(`./locales/${locale}/home.json`)).default,
      reframe: (await import(`./locales/${locale}/reframe.json`)).default,
      errors: (await import(`./locales/${locale}/errors.json`)).default,
      about: (await import(`./locales/${locale}/about.json`)).default,
      'learn-cbt': (await import(`./locales/${locale}/learn-cbt.json`)).default,
      support: (await import(`./locales/${locale}/support.json`)).default,
      privacy: (await import(`./locales/${locale}/privacy.json`)).default,
    }
  };
});