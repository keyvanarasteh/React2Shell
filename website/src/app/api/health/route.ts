import { NextResponse } from "next/server";

/**
 * Health Check Endpoint
 * Saldırı scriptlerinin hedefin çalışıp çalışmadığını kontrol etmesi için
 */
export async function GET() {
  return NextResponse.json({
    status: "ok",
    timestamp: new Date().toISOString(),
    service: "TechCorp Portal",
    version: {
      next: "15.0.3",
      react: "19.0.0",
      node: process.version,
    },
    uptime: Math.floor(process.uptime()),
    rsc: true,
    serverActions: true,
  });
}
