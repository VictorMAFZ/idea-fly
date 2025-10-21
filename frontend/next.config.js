/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    // Type checking is handled by CI/CD pipeline
    ignoreBuildErrors: false,
  },
  eslint: {
    // ESLint is handled by CI/CD pipeline
    ignoreDuringBuilds: false,
  },
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },
  async headers() {
    return [
      {
        // Security headers for authentication pages
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig