import { useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";
import { StatusChip } from "../StatusChip";
import type { MockAnalysis } from "../../lib/mockAnalysis";

export default function DetailSheet({ analysis, onClose, reset }: { analysis: MockAnalysis; onClose: () => void; reset: () => void }) {
  const [transacted, setTransacted] = useState<"no" | "yes">("no");
  const [feedback, setFeedback] = useState<"yes" | "no" | null>(null);
  const hasSecretRequest = analysis.findings.some((item) => item.title === "Permintaan data rahasia");
  return (
    <Sheet title="Mengapa hasil ini muncul?" eyebrow={`Simulasi lokal · ${analysis.score}/100`} onClose={onClose} wide>
      <div className="warning-banner"><Icon name="alert" /><div><strong>Ini contoh hasil, bukan pemeriksaan keamanan</strong><p>Aturan sederhana hanya membaca teks yang dimasukkan. Reputasi URL, identitas pengirim, dan laporan komunitas belum diperiksa.</p></div></div>
      <div className="detail-grid">
        <div className="detail-column">
          <section className="content-block">
            <span className="section-label">01 · POLA DALAM MASUKAN</span>
            {analysis.findings.length > 0 ? (
              <ol className="evidence-list">
                {analysis.findings.map((finding) => <li key={finding.title}><b>{finding.title}</b><p>{finding.description}</p></li>)}
              </ol>
            ) : <p className="no-findings">Aturan contoh belum menemukan pola yang dikenali. Ini tidak berarti pesan atau alamat tersebut aman.</p>}
          </section>
          {analysis.hosts.length > 0 && <section className="content-block">
            <span className="section-label">02 · ALAMAT YANG TERDETEKSI</span>
            <div className="url-table">{analysis.hosts.map((host, index) => <div key={`${host}-${index}`}><span>Domain</span><code>{host}</code><StatusChip tone="neutral">Belum diverifikasi</StatusChip></div>)}</div>
            <p className="fine-print">Nama domain ditampilkan untuk ditinjau manual. Status reputasi belum tersedia pada prototipe ini.</p>
          </section>}
        </div>
        <div className="detail-column">
          <section className="content-block">
            <span className="section-label">LANGKAH YANG DISARANKAN</span>
            <ol className="action-list">
              {analysis.hosts.length > 0 && <li><span>1</span><div><b>Jangan buka tautan dulu</b><p>Cari situs atau aplikasi resmi secara mandiri.</p></div></li>}
              {hasSecretRequest && <li><span>{analysis.hosts.length > 0 ? 2 : 1}</span><div><b>Jangan bagikan kode rahasia</b><p>OTP, PIN, dan kata sandi tidak boleh diberikan melalui pesan.</p></div></li>}
              <li><span>{Number(analysis.hosts.length > 0) + Number(hasSecretRequest) + 1}</span><div><b>Verifikasi lewat kanal resmi</b><p>Hubungi layanan dari nomor atau aplikasi yang Anda temukan sendiri.</p></div></li>
            </ol>
          </section>
          <section className="content-block decision-block">
            <b>Apakah Anda sudah melakukan transaksi atau membagikan data?</b>
            <div className="segmented" role="group" aria-label="Status tindakan Anda">
              <button aria-pressed={transacted === "no"} className={transacted === "no" ? "selected" : ""} onClick={() => setTransacted("no")}>Belum</button>
              <button aria-pressed={transacted === "yes"} className={transacted === "yes" ? "selected" : ""} onClick={() => setTransacted("yes")}>Sudah</button>
            </div>
            {transacted === "no" ? <p><Icon name="shield" /> Hentikan komunikasi dan periksa melalui kanal resmi.</p> : <p className="urgent"><Icon name="alert" /> Simpan bukti dan segera hubungi penyedia layanan terkait.</p>}
          </section>
        </div>
      </div>
      <div className="sheet-footer">
        <div><span>Membantu? <button className={feedback === "yes" ? "chosen" : ""} onClick={() => setFeedback("yes")}>Ya</button> / <button className={feedback === "no" ? "chosen" : ""} onClick={() => setFeedback("no")}>Tidak</button></span>{feedback && <small>Tanggapan tersimpan sementara di halaman ini.</small>}</div>
        <div><Button onClick={reset}>Periksa bahan lain <Icon name="chevron" /></Button></div>
      </div>
    </Sheet>
  );
}
