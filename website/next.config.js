/** @type {import('next').NextConfig} */
const nextConfig = {
  // Server Actions etkin — bu, saldırı yüzeyini oluşturur
  experimental: {
    serverActions: {
      enabled: true,
    },
  },
  // Kasıtlı olarak güvenlik header'ları devre dışı (eğitim amaçlı)
  poweredByHeader: true, // X-Powered-By header'ı açık bırak (parmak izi tespiti için)
};

module.exports = nextConfig;
