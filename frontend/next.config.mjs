/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Enable resolving TS path aliases like "@/*" at build time
    tsconfigPaths: true,
  },
};

export default nextConfig;
