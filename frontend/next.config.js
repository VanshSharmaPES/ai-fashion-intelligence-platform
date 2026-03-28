/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        // Proxy all API requests to the Node backend to bypass CORS and mixed-content SSL issues
        source: '/api/:path*',
        destination: 'http://127.0.0.1:8000/api/:path*', 
      },
    ]
  },
}

module.exports = nextConfig
