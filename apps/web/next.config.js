/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {
    // Enable experimental features if needed
  },
  // Configure images if needed
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig