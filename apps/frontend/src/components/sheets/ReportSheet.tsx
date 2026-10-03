import { useState } from "react";
import Sheet from "../Sheet";
import { Icon } from "../Icon";
import { Button } from "../Button";

export default function ReportSheet({ onClose }: { onClose: () => void }) {
  const [type, setType] = useState<"url" | "text">("url");
  const [sent, setSent] = useState(false);
  return <Sheet title="Laporkan secara anonim" eyebrow="Bantu komunitas" onClose={onClose}>
    {sent ? <div className="success-state"><span><Icon name="check" size={28} /></span><h3>Laporan diterima</h3><p>ID laporan <code>CRN-7F2A</code>. Tim moderasi akan meninjaunya tanpa melihat identitas Anda.</p><Button onClick={onClose}>Selesai</Button></div> : <>
      <div className="segmented"><button className={type === "url" ? "selected" : ""} onClick={() => setType("url")}>URL</button><button className={type === "text" ? "selected" : ""} onClick={() => setType("text")}>Teks pesan</button></div>
      <label className="field-label" htmlFor="report-value">{type === "url" ? "Alamat URL" : "Salin teks pesan"}</label>
      {type === "url" ? <input id="report-value" className="field" placeholder="https://contoh.info" /> : <textarea id="report-value" className="textarea" rows={5} placeholder="Tempel teks tanpa data pribadi…" />}
      <label className="check-row"><input type="checkbox" /> <span>Saya setuju bahan ini ditinjau untuk melindungi komunitas.</span></label>
      <div className="neutral-note"><Icon name="shield" /><p>Laporan dimoderasi dan bukan bukti langsung bahwa suatu pihak melakukan penipuan.</p></div>
      <Button className="button--full" onClick={() => setSent(true)}>Kirim laporan anonim →</Button>
    </>}
  </Sheet>;
}
