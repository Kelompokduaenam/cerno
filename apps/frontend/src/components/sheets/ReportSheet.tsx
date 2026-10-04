import { useState } from "react";
import type { FormEvent } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";

type ReportErrors = Partial<Record<"target" | "reason" | "consent", string>>;

export default function ReportSheet({ onClose }: { onClose: () => void }) {
  const [type, setType] = useState<"url" | "text">("url");
  const [target, setTarget] = useState("");
  const [reason, setReason] = useState("");
  const [consent, setConsent] = useState(false);
  const [errors, setErrors] = useState<ReportErrors>({});
  const [ready, setReady] = useState(false);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const next: ReportErrors = {};
    if (type === "url") {
      try {
        const url = new URL(target.trim());
        if (!["http:", "https:"].includes(url.protocol) || !url.hostname) throw new Error("invalid");
      } catch { next.target = "Masukkan URL lengkap yang diawali http:// atau https://."; }
    } else if (target.trim().length < 10) next.target = "Teks pesan minimal 10 karakter.";
    if (reason.trim().length < 10) next.reason = "Jelaskan alasan laporan dalam minimal 10 karakter.";
    if (!consent) next.consent = "Persetujuan diperlukan untuk melanjutkan.";
    setErrors(next);
    if (Object.keys(next).length === 0) setReady(true);
  };

  return <Sheet title="Laporkan secara anonim" eyebrow="Simulasi formulir" onClose={onClose}>
    {ready ? <div className="success-state"><span><Icon name="check" size={28} /></span><h3>Formulir laporan siap</h3><p>Validasi berhasil. Laporan belum dikirim karena pengiriman akan dihubungkan pada tahap integrasi.</p><Button onClick={() => setReady(false)}>Ubah laporan</Button></div> : <form onSubmit={submit} noValidate>
      <div className="segmented" role="group" aria-label="Jenis laporan"><button type="button" aria-pressed={type === "url"} className={type === "url" ? "selected" : ""} onClick={() => { setType("url"); setTarget(""); setErrors({}); }}>URL</button><button type="button" aria-pressed={type === "text"} className={type === "text" ? "selected" : ""} onClick={() => { setType("text"); setTarget(""); setErrors({}); }}>Teks pesan</button></div>
      <label className="field-label" htmlFor="report-value">{type === "url" ? "Alamat URL" : "Salin teks pesan"}</label>
      {type === "url" ? <input id="report-value" className="field" value={target} onChange={(e) => { setTarget(e.target.value); setErrors({ ...errors, target: undefined }); }} aria-invalid={!!errors.target} aria-describedby={errors.target ? "report-target-error" : undefined} placeholder="https://contoh.info" /> : <textarea id="report-value" className="textarea" rows={5} value={target} onChange={(e) => { setTarget(e.target.value); setErrors({ ...errors, target: undefined }); }} aria-invalid={!!errors.target} aria-describedby={errors.target ? "report-target-error" : undefined} placeholder="Tempel teks tanpa data pribadi…" />}
      {errors.target && <p className="field-error" id="report-target-error">{errors.target}</p>}
      <label className="field-label" htmlFor="report-reason">Alasan laporan</label>
      <textarea id="report-reason" className="textarea" rows={3} value={reason} onChange={(e) => { setReason(e.target.value); setErrors({ ...errors, reason: undefined }); }} aria-invalid={!!errors.reason} aria-describedby={errors.reason ? "report-reason-error" : undefined} placeholder="Ceritakan hal yang membuat Anda ragu…" />
      {errors.reason && <p className="field-error" id="report-reason-error">{errors.reason}</p>}
      <label className="check-row"><input type="checkbox" checked={consent} onChange={(e) => { setConsent(e.target.checked); setErrors({ ...errors, consent: undefined }); }} aria-invalid={!!errors.consent} aria-describedby={errors.consent ? "report-consent-error" : undefined} /> <span>Saya setuju bahan ini ditinjau untuk melindungi komunitas.</span></label>
      {errors.consent && <p className="field-error" id="report-consent-error">{errors.consent}</p>}
      <div className="neutral-note"><Icon name="shield" /><p>Simulasi ini belum mengirim laporan. Hapus data pribadi sebelum tahap pengiriman tersedia.</p></div>
      <Button type="submit" className="button--full">Periksa formulir laporan →</Button>
    </form>}
  </Sheet>;
}
