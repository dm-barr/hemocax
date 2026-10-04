import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // Presentación interactiva (archivo estático en public/pitch.html) disponible en /pitch
  async rewrites() {
    return [{ source: '/pitch', destination: '/pitch.html' }];
  },
};
export default nextConfig;
