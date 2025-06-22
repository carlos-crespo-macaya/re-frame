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
      common: (await import(`./locales/${locale}/common.json`)),
      home: (await import(`./locales/${locale}/home.json`)),
      reframe: (await import(`./locales/${locale}/reframe.json`)),
      errors: (await import(`./locales/${locale}/errors.json`)),
      about: (await import(`./locales/${locale}/about.json`)),
      'learn-cbt': (await import(`./locales/${locale}/learn-cbt.json`)),
      support: (await import(`./locales/${locale}/support.json`)),
      privacy: (await import(`./locales/${locale}/privacy.json`)),
    }
  };
});