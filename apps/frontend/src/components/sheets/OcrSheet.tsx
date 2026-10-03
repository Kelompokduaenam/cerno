import { useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";

export default function OcrSheet({ onClose, analyze }: { onClose: () => void; analyze: (text: string) => void }) {
  const [text, setText] = useState("Halo, akun Anda akan diblokir hari ini. Klik bca-verifikasi-sekarang.info dan kirim kode OTP untuk membatalkan.");
  return <Sheet title="Tinjau teks hasil OCR" eyebrow="Wajib sebelum analisis" onClose={onClose}>
    <div className="privacy-note"><Icon name="eye" /><div><b>Data sensitif disamarkan</b><p>Nomor rekening dan telepon dideteksi lalu disamarkan otomatis.</p></div></div>
    <label className="field-label" htmlFor="ocr-text">Teks yang terbaca</label>
    <textarea id="ocr-text" className="textarea" value={text} onChange={(e) => setText(e.target.value)} rows={7} />
    <p className="fine-print">Pastikan teks sesuai gambar. Anda dapat menghapus bagian pribadi sebelum melanjutkan.</p>
    <Button className="button--full" onClick={() => analyze(text)}>Analisis risiko <span>→</span></Button>
  </Sheet>;
}
