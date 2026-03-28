/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Keep Windows builds from over-spawning workers during page-data collection.
    cpus: 4,
  },
};

module.exports = nextConfig;
