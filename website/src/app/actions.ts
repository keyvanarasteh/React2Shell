"use server";

// ============================================
// TechCorp Server Actions
// CVE-2025-55182 — SALDIRI YÜZEYİ
// ============================================
// Bu dosyadaki her fonksiyon, React Flight
// protokolü üzerinden erişilebilir bir
// endpoint oluşturur.
// ============================================

import { headers } from "next/headers";

// KASITLI GÜVENLİK AÇIĞI: Sunucu tarafı sırları
// (Kaynak kod ifşası demo'su için — CVE-2025-55183)
const DB_CONNECTION = "postgresql://admin:SuperSecret123!@db.techcorp.local:5432/production";
const API_SECRET_KEY = "sk_live_R2S_4f8a9b2c3d4e5f6a7b8c9d0e1f2a3b4c";
const JWT_SIGNING_KEY = "jwt_s3cr3t_k3y_n3v3r_3xp0s3_th1s";
const INTERNAL_API_TOKEN = "tok_internal_9a8b7c6d5e4f3a2b1c0d";

/**
 * Form verisi işleme — İletişim formu Server Action
 * Bu fonksiyon "use server" ile işaretlendiği için
 * Flight protokolü üzerinden doğrudan çağrılabilir.
 */
export async function submitForm(formData: FormData) {
  const name = formData.get("name") as string;
  const email = formData.get("email") as string;
  const subject = formData.get("subject") as string;
  const message = formData.get("message") as string;

  // Basit doğrulama
  if (!name || !email || !message) {
    return {
      success: false,
      error: "Tüm alanları doldurun",
    };
  }

  // Simüle edilmiş veritabanı kaydı
  console.log(`[DB] Yeni mesaj: ${name} <${email}> — ${subject}`);
  console.log(`[DB] Bağlantı: ${DB_CONNECTION}`);

  // Simüle edilmiş gecikme
  await new Promise((resolve) => setTimeout(resolve, 500));

  return {
    success: true,
    message: `Teşekkürler ${name}! Mesajınız alındı.`,
    ticketId: `TCK-${Date.now().toString(36).toUpperCase()}`,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Sunucu bilgisi döndürme
 * Kasıtlı olarak hassas bilgi ifşa eder
 */
export async function getServerInfo() {
  const headersList = await headers();

  return {
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
    uptime: Math.floor(process.uptime()),
    memoryUsage: {
      rss: `${Math.round(process.memoryUsage().rss / 1024 / 1024)} MB`,
      heapUsed: `${Math.round(process.memoryUsage().heapUsed / 1024 / 1024)} MB`,
    },
    env: process.env.NODE_ENV || "development",
    pid: process.pid,
    cwd: process.cwd(),
    userAgent: headersList.get("user-agent") || "unknown",
  };
}

/**
 * Veri işleme fonksiyonu
 * Ek saldırı yüzeyi — deserialization exploit için
 */
export async function processData(data: unknown) {
  // GÜVENSİZ: Gelen veriyi doğrulama olmadan işler
  // Bu, CVE-2025-55182'nin kök nedenidir
  console.log("[PROCESS] Veri işleniyor:", typeof data);

  // Simüle edilmiş veri işleme
  const result = {
    processed: true,
    timestamp: new Date().toISOString(),
    dataType: typeof data,
    serverPid: process.pid,
  };

  return result;
}

/**
 * Kullanıcı arama fonksiyonu
 * Ek saldırı yüzeyi
 */
export async function searchUsers(query: string) {
  // Simüle edilmiş veritabanı sorgusu
  console.log(`[SEARCH] Sorgu: ${query}`);
  console.log(`[SEARCH] DB: ${DB_CONNECTION}`);

  await new Promise((resolve) => setTimeout(resolve, 300));

  const mockUsers = [
    { id: 1, name: "Ahmet Yılmaz", email: "ahmet@techcorp.local", role: "admin" },
    { id: 2, name: "Elif Kaya", email: "elif@techcorp.local", role: "user" },
    { id: 3, name: "Mehmet Demir", email: "mehmet@techcorp.local", role: "user" },
  ];

  return mockUsers.filter((u) =>
    u.name.toLowerCase().includes((query || "").toLowerCase())
  );
}
