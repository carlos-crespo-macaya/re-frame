/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: process.env.ALLOWED_IMAGE_DOMAINS?.split(',') || [],
  },
  // Disable x-powered-by header for security
  poweredByHeader: false,
  // Strict mode for better React development
  reactStrictMode: true,
  // Experimental features for better performance
  experimental: {
    optimizeCss: true,
  },
  // Environment variables that will be available in the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

export default nextConfig;