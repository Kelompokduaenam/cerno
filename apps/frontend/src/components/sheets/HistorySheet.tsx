import { useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";
import { StatusChip } from "../StatusChip";

export default function HistorySheet({ onClose, openLogin }: { onClose: () => void; openLogin: () => void }) {
  const [loggedIn, setLoggedIn] = useState(false);
  const [items, setItems] = useState([
    { id: "CRN-92F1", type: "URL", text: "bca-ver••••.info", score: 91, risk: "bad" as const },
    { id: "CRN-8A4C", type: "TEKS", text: "Paket Anda s••••••", score: 58, risk: "warn" as const },
  ]);
  return <Sheet title="Riwayat pemeriksaan" eyebrow="Tersimpan 30 hari" onClose={onClose}>
    {!loggedIn ? <div className="empty-state"><span><Icon name="clock" size={28} /></span><h3>Riwayat Anda belum tersambung</h3><p>Masuk untuk melihat pemeriksaan yang disimpan di perangkat ini. Isi sensitif tetap disamarkan.</p><Button onClick={() => { setLoggedIn(true); openLogin(); }}>Masuk untuk melihat riwayat</Button></div> :
      items.length === 0 ? <div className="empty-state"><span><Icon name="clock" size={28} /></span><h3>Belum ada riwayat</h3><p>Hasil yang Anda simpan akan muncul di sini.</p></div> :
      <div className="history-list">{items.map((item) => <article key={item.id}>
        <div><span className="section-label">{item.id} · {item.type}</span><b>{item.text}</b></div>
        <StatusChip tone={item.risk}>{item.score}/100</StatusChip>
        <button className="icon-button" aria-label={`Hapus ${item.id}`} onClick={() => setItems(items.filter((i) => i.id !== item.id))}><Icon name="trash" /></button>
      </article>)}</div>}
    <p className="retention"><Icon name="shield" /> Riwayat dihapus otomatis setelah 30 hari. Anda dapat menghapusnya lebih awal kapan saja.</p>
  </Sheet>;
}
