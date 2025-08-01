import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './lib/i18n/config';

export default createMiddleware({
  // A list of all locales that are supported
  locales,
  
  // Used when no locale matches
  defaultLocale,
  
  // Never redirect to default locale
  localePrefix: 'as-needed'
});

export const config = {
  // Match only internationalized pathnames
  matcher: [
    // Match all pathnames except for:
    // - API routes (/api)
    // - Static files (_next, favicon.ico, etc.)
    // - Public files (files with extensions)
    '/((?!api|_next|.*\\..*).*)'
  ]
}; 