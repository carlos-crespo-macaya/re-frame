/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
  // Disable x-powered-by header for security
  poweredByHeader: false,
  // Strict mode for better React development
  reactStrictMode: true,
};

export default nextConfig;
