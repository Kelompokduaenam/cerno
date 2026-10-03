import { useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";
import { StatusChip } from "../StatusChip";
import type { Risk } from "../../types";

export default function DetailSheet({ score, risk, onClose, reset }: { score: number; risk: Risk; onClose: () => void; reset: () => void }) {
  const [transacted, setTransacted] = useState<"no" | "yes">("no");
  const [feedback, setFeedback] = useState<"yes" | "no" | null>(null);
  return (
    <Sheet title="Mengapa bahan ini berisiko?" eyebrow={`Analisis lengkap · ${score}/100`} onClose={onClose} wide>
      {risk === "suspicious" && <div className="warning-banner"><Icon name="alert" /><div><strong>Pemeriksaan URL tidak lengkap</strong><p>Penyedia threat-intel tidak merespons. Hasil ini tidak berarti URL aman.</p></div></div>}
      <div className="detail-grid">
        <div className="detail-column">
          <section className="content-block">
            <span className="section-label">01 · SINYAL YANG DITEMUKAN</span>
            <ol className="evidence-list">
              <li><b>Tekanan waktu</b><p>Frasa <mark>“klik sekarang, akun akan diblokir”</mark> mendorong keputusan tergesa-gesa.</p></li>
              <li><b>Permintaan kredensial</b><p>Pesan meminta kode OTP yang seharusnya tidak dibagikan kepada siapa pun.</p></li>
              <li><b>Domain tidak sesuai</b><p><code>bca-verifikasi-sekarang.info</code> bukan domain resmi layanan yang disebut.</p></li>
            </ol>
          </section>
          <section className="content-block">
            <span className="section-label">02 · PEMERIKSAAN URL</span>
            <div className="url-table">
              <div><span>Domain</span><code>bca-verifikasi-sekarang.info</code><StatusChip tone="bad">Tidak sesuai</StatusChip></div>
              <div><span>Struktur</span><b>Subdomain menyesatkan</b><StatusChip tone="warn">Waspada</StatusChip></div>
              <div><span>Threat intel</span><b>2 sinyal aktif</b><StatusChip tone="bad">Berisiko</StatusChip></div>
              <div><span>Komunitas</span><b>12 laporan pendukung</b><StatusChip tone="neutral">Sinyal tambahan</StatusChip></div>
            </div>
            <p className="fine-print">Laporan komunitas hanya sinyal pendukung, bukan bukti langsung.</p>
          </section>
        </div>
        <div className="detail-column">
          <section className="content-block">
            <span className="section-label">03 · LANGKAH YANG DISARANKAN</span>
            <ol className="action-list">
              <li><span>1</span><div><b>Jangan klik tautan</b><p>Buka aplikasi atau situs resmi secara manual.</p></div></li>
              <li><span>2</span><div><b>Jangan bagikan OTP</b><p>Penyedia resmi tidak meminta kode rahasia.</p></div></li>
              <li><span>3</span><div><b>Verifikasi lewat kanal resmi</b><p>Hubungi nomor di aplikasi atau kartu Anda.</p></div></li>
            </ol>
          </section>
          <section className="content-block decision-block">
            <b>Apakah Anda sudah melakukan transaksi atau membagikan data?</b>
            <div className="segmented">
              <button className={transacted === "no" ? "selected" : ""} onClick={() => setTransacted("no")}>Belum</button>
              <button className={transacted === "yes" ? "selected" : ""} onClick={() => setTransacted("yes")}>Sudah</button>
            </div>
            {transacted === "no" ? <p><Icon name="shield" /> Tetap hentikan komunikasi, blokir pengirim, dan periksa akun melalui kanal resmi.</p> : <p className="urgent"><Icon name="alert" /> Simpan bukti, segera hubungi bank/penyedia, lalu buat laporan melalui kanal resmi.</p>}
          </section>
        </div>
      </div>
      <div className="sheet-footer">
        <div><button className="text-button">Masuk dan simpan</button><span>Membantu? <button className={feedback === "yes" ? "chosen" : ""} onClick={() => setFeedback("yes")}>Ya</button> / <button className={feedback === "no" ? "chosen" : ""} onClick={() => setFeedback("no")}>Tidak</button></span></div>
        <div><Button className="button--secondary">Laporkan secara anonim</Button><Button onClick={reset}>Periksa bahan lain <Icon name="chevron" /></Button></div>
      </div>
    </Sheet>
  );
}
