/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    // Enable experimental features if needed
  },
  // Disable telemetry
  telemetry: false,
  // Configure images if needed
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig