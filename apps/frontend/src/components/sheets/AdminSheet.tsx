import { useState } from "react";
import Sheet from "../Sheet";
import { StatusChip } from "../StatusChip";

export default function AdminSheet({ onClose }: { onClose: () => void }) {
  const [queue, setQueue] = useState(["CRN-R821", "CRN-R819", "CRN-R808"]);
  return <Sheet title="Pusat operasi" eyebrow="Admin · data tersamarkan" onClose={onClose} wide>
    <div className="admin-kpis">
      {[["12.480", "Analisis minggu ini", "+18%"], ["2.108", "Risiko tinggi", "16,8%"], ["1,8 dtk", "Respons rata-rata", "Normal"], ["38", "Laporan menunggu", "Perlu tinjau"]].map(([value, label, delta]) => <article key={label}><span>{label}</span><strong>{value}</strong><small>{delta}</small></article>)}
    </div>
    <div className="admin-grid">
      <section className="content-block"><span className="section-label">STATUS LAYANAN</span>
        <div className="service-list"><div><b>API analisis</b><StatusChip tone="ok">Operasional</StatusChip></div><div><b>OCR</b><StatusChip tone="ok">Operasional</StatusChip></div><div><b>Threat-intel provider</b><StatusChip tone="warn">Terganggu</StatusChip></div><div><b>Model</b><code>cerno-risk-v2.4.1</code></div></div>
      </section>
      <section className="content-block"><span className="section-label">ANTREAN MODERASI</span>
        <div className="queue-list">{queue.length ? queue.map((id) => <div key={id}><code>{id}</code><span>URL · 4 sinyal</span><div><button onClick={() => setQueue(queue.filter((q) => q !== id))}>Terima</button><button onClick={() => setQueue(queue.filter((q) => q !== id))}>Tolak</button><button onClick={() => setQueue(queue.filter((q) => q !== id))}>Duplikat</button></div></div>) : <p className="inline-empty">Antrean sudah bersih.</p>}</div>
      </section>
    </div>
    <section className="content-block feedback-review"><span className="section-label">TINJAUAN UMPAN BALIK</span><div><b>84% membantu</b><p>126 respons tersamarkan · Tidak ada pesan mentah atau screenshot yang ditampilkan.</p></div></section>
  </Sheet>;
}
