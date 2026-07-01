/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // We can add rewrite rules to proxy api calls to backend FastAPI running on 8000
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
