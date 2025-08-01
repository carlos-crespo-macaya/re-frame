import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Temporarily disabled static export for i18n development
  // output: 'export',
  trailingSlash: true,
  images: {
    domains: process.env.ALLOWED_IMAGE_DOMAINS?.split(',') || [],
  },
  poweredByHeader: false,
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  experimental: {
    optimizePackageImports: ['@headlessui/react'],
  },
  // Disable problematic features in development
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }
    return config
  },
};

export default withNextIntl(nextConfig);
