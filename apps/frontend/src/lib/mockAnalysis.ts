import type { Risk } from "../types";

/**
 * MOCK — heuristik kata kunci dari prototipe Figma.
 * Akan diganti dengan pemanggilan POST /api/v1/analyses (lihat Arsitektur CERNO §3.4).
 */
export function mockScore(text: string): number {
  const t = text.toLowerCase();
  if (t.includes("otp") || t.includes("klik") || t.includes("transfer")) return 91;
  if (t.includes("segera") || t.includes("promo") || t.includes("bit.ly")) return 58;
  return 22;
}

export const riskFromScore = (score: number): Risk =>
  score >= 70 ? "danger" : score >= 35 ? "suspicious" : "safe";

export const RISK_COPY: Record<Risk, string> = {
  danger: "Risiko tinggi",
  suspicious: "Mencurigakan",
  safe: "Risiko rendah",
};

export const EVIDENCE: Record<Risk, string[]> = {
  danger: ["Tekanan waktu", "Permintaan kredensial", "Domain tidak sesuai", "Iming-iming hadiah", "Jejak komunitas"],
  suspicious: ["Bahasa mendesak", "URL dipersingkat", "Sumber belum jelas"],
  safe: ["Tidak ada desakan", "Domain sesuai", "Tanpa permintaan rahasia"],
};

export const RESULT_HEADLINE: Record<Risk, string> = {
  danger: "Jangan ikuti permintaan dalam pesan ini",
  suspicious: "Verifikasi sebelum melanjutkan",
  safe: "Tetap periksa konteks sebelum bertindak",
};
