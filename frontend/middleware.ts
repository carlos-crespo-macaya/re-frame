import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // A list of all locales that are supported
  locales: ['en', 'es'],
  
  // Used when no locale matches
  defaultLocale: 'en',
  
  // Always use a locale prefix in the URL
  localePrefix: 'always',
  
  // Redirect root to default locale
  localeDetection: true
});

export const config = {
  // Match only internationalized pathnames
  matcher: [
    // Match all pathnames except for
    // - … if they start with `/api`, `/_next` or `/_vercel`
    // - … the ones containing a dot (e.g. `favicon.ico`)
    '/((?!api|_next|_vercel|.*\\..*).*)',
    // However, match all pathnames within `/users`, including the ones containing a dot
    '/([\\w-]+)?/users/(.+)'
  ]
};