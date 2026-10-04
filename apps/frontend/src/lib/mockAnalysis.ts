import type { InputMode, Risk } from "../types";

export type MockFinding = { title: string; description: string; weight: number };
export type MockAnalysis = {
  source: InputMode;
  score: number;
  risk: Risk;
  findings: MockFinding[];
  hosts: string[];
};

export const riskFromScore = (score: number): Risk =>
  score >= 70 ? "danger" : score >= 30 ? "suspicious" : "safe";

/** Local prototype only. These rules are examples, not a security assessment. */
export function mockAnalyze(input: string, source: InputMode): MockAnalysis {
  const findings: MockFinding[] = [];
  const add = (pattern: RegExp, title: string, description: string, weight: number) => {
    if (pattern.test(input)) findings.push({ title, description, weight });
  };

  add(/\b(otp|pin|password|kata sandi|kode verifikasi)\b/i, "Permintaan data rahasia", "Pesan menyebut kode atau kata sandi. Jangan membagikannya kepada siapa pun.", 40);
  add(/\b(segera|hari ini juga|akan diblokir|terblokir|terakhir)\b/i, "Tekanan waktu", "Ada bahasa yang mendorong keputusan cepat. Beri waktu untuk memeriksa sumbernya.", 25);
  add(/\b(transfer|bayar|rekening|biaya admin)\b/i, "Permintaan transaksi", "Pesan menyebut pembayaran atau rekening. Verifikasi lewat kanal resmi.", 15);
  add(/\b(klik|buka tautan)\b/i, "Ajakan membuka tautan", "Periksa alamat dan konteks sebelum membuka tautan.", 10);

  const urls = source === "url" ? [input.trim()] : input.match(/https?:\/\/[^\s<>"']+/gi) ?? [];
  const hosts = urls.flatMap((raw) => {
    try { return [new URL(raw.replace(/[.,;!?)]+$/, "")).hostname]; }
    catch { return []; }
  });
  if (hosts.some((host) => /(^|\.)(xn--)/i.test(host) || host.split(".").length > 3 || /(login|verify|validasi|hadiah)/i.test(host))) {
    findings.push({ title: "Struktur alamat perlu ditinjau", description: "Nama domain memiliki pola yang patut diperiksa manual. Ini bukan hasil pemeriksaan reputasi.", weight: 15 });
  }

  const score = Math.min(100, findings.reduce((total, finding) => total + finding.weight, 0));
  return { source, score, risk: riskFromScore(score), findings, hosts };
}

export const RISK_COPY: Record<Risk, string> = {
  danger: "Risiko tinggi",
  suspicious: "Perlu diwaspadai",
  safe: "Belum ada pola kuat",
};

export const RESULT_HEADLINE: Record<Risk, string> = {
  danger: "Jangan ikuti permintaan dalam pesan ini",
  suspicious: "Verifikasi sebelum melanjutkan",
  safe: "Tetap periksa konteks sebelum bertindak",
};
