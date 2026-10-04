import { useEffect, useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";

export default function OcrSheet({ file, onClose, analyze }: { file: File; onClose: () => void; analyze: (text: string) => void }) {
  const [text, setText] = useState("Halo, akun Anda akan diblokir hari ini. Klik bca-verifikasi-sekarang.info dan kirim kode OTP untuk membatalkan.");
  const [preview, setPreview] = useState("");
  useEffect(() => {
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  return <Sheet title="Tinjau teks screenshot" eyebrow="Simulasi OCR" onClose={onClose}>
    <div className="privacy-note"><Icon name="eye" /><div><b>Teks di bawah hanya contoh</b><p>Gambar belum dibaca secara otomatis. Sesuaikan teks dengan screenshot sebelum melanjutkan.</p></div></div>
    {preview && <figure className="screenshot-preview"><img src={preview} alt={`Pratinjau ${file.name}`} /><figcaption>{file.name}</figcaption></figure>}
    <label className="field-label" htmlFor="ocr-text">Teks untuk simulasi analisis</label>
    <textarea id="ocr-text" className="textarea" value={text} onChange={(e) => setText(e.target.value)} rows={7} />
    <p className="fine-print">Hapus data pribadi sebelum melanjutkan. Simulasi ini berjalan lokal di browser.</p>
    <Button className="button--full" onClick={() => analyze(text.trim())} disabled={!text.trim()}>Simulasikan analisis <span>→</span></Button>
  </Sheet>;
}
