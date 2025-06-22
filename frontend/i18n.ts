import {getRequestConfig} from 'next-intl/server';
import {routing} from './i18n/routing';

export default getRequestConfig(async ({requestLocale}) => {
  // This typically corresponds to the `[locale]` segment
  let locale = await requestLocale;

  // Ensure that a valid locale is used
  if (!locale || !routing.locales.includes(locale as (typeof routing.locales)[number])) {
    locale = routing.defaultLocale;
  }
  
  console.log('[i18n.ts] getRequestConfig called with locale:', locale);
  console.log('[i18n.ts] Valid locales:', routing.locales);
  console.log('[i18n.ts] typeof locale:', typeof locale);

  return {
    locale,
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