import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Sin Cache Components: todas las páginas son privadas y dependen de la
  // sesión, así que se renderizan por petición (modelo dinámico clásico).
  experimental: {
    // El CSV puede pesar hasta 1 MB (límite del backend) más el formulario
    serverActions: { bodySizeLimit: "2mb" },
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
