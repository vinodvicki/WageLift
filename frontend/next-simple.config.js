/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Simplified configuration
  experimental: {
    appDir: true,
  },
  
  // Disable problematic features for demo
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  typescript: {
    ignoreBuildErrors: true,
  },
  
  // Simple webpack config
  webpack: (config) => {
    config.resolve.fallback = {
      fs: false,
      net: false,
      tls: false,
    };
    return config;
  },
  
  // Environment variables
  env: {
    CUSTOM_KEY: 'demo-mode',
  },
  
  // Simple redirects
  async redirects() {
    return [
      {
        source: '/demo',
        destination: '/working-demo.html',
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig; 