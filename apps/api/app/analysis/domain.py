"""Pure rules for the first, explicitly untrained risk baseline."""

import re


RULES = [
    (r"\b(otp|pin|password|kata sandi|kode verifikasi)\b", 40, "Permintaan kredensial"),
    (r"\b(segera|dalam \d+ menit|hari ini juga|terakhir|akan diblokir|terblokir)\b", 25, "Tekanan waktu"),
    (r"\b(admin|bank|kurir|pajak|polisi|dukungan resmi)\b", 10, "Klaim identitas lembaga"),
    (r"\b(transfer|bayar|rekening|biaya admin)\b", 15, "Permintaan transaksi"),
]


def redact(text: str) -> str:
    text = re.sub(r"https?://[^\s<>'\"]+", "[URL_REDACTED]", text, flags=re.I)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL_REDACTED]", text)
    text = re.sub(r"(?<!\w)(?:\+?62|0)[\d\s-]{8,15}\d(?!\w)", "[PHONE_REDACTED]", text)
    text = re.sub(r"(?i)\b(otp|pin|password|kata sandi)\s*[:=]?\s*\d{4,8}\b", r"\1 [SENSITIVE_CREDENTIAL]", text)
    return text[:4000]


def text_evidence(text: str) -> tuple[int, list[dict]]:
    score = 0
    evidence = []
    for pattern, weight, label in RULES:
        if re.search(pattern, text, re.I):
            score += weight
            evidence.append({"code": label.lower().replace(" ", "_"), "title": label, "description": "Pola ini muncul pada masukan dan perlu diverifikasi melalui kanal resmi.", "weight": weight})
    return score, evidence


def risk_level(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 30 else "low"


def recommendations(level: str, has_url: bool) -> list[str]:
    actions = ["Jangan berikan OTP, PIN, atau kata sandi.", "Verifikasi melalui situs atau nomor resmi yang dicari sendiri."] if level != "low" else ["Tetap verifikasi identitas pengirim sebelum bertindak."]
    if has_url:
        actions.insert(0, "Jangan buka tautan sebelum alamatnya diverifikasi.")
    return actions
