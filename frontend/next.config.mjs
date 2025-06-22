import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  // Disable x-powered-by header for security
  poweredByHeader: false,
  // Strict mode for better React development
  reactStrictMode: true,
};

export default withNextIntl(nextConfig);
