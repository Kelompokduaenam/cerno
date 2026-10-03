import { Icon } from "./Icon";
import type { InputMode, SheetName } from "../types";

const modeItems: { mode: InputMode; icon: string; short: string; label: string }[] = [
  { mode: "text", icon: "text", short: "Aa", label: "Teks pesan" },
  { mode: "url", icon: "link", short: "://", label: "URL" },
  { mode: "screenshot", icon: "image", short: "", label: "Screenshot" },
];

export default function Rail({ mode, setMode, openSheet, dark, setDark }: {
  mode: InputMode; setMode: (m: InputMode) => void; openSheet: (s: SheetName) => void; dark: boolean; setDark: (v: boolean) => void;
}) {
  const actions = [
    { icon: "flag", label: "Lapor anonim", sheet: "report" as SheetName },
    { icon: "clock", label: "Riwayat", sheet: "history" as SheetName },
    { icon: "shield", label: "Admin", sheet: "admin" as SheetName },
  ];
  return (
    <nav className="rail" aria-label="Pilih jenis pemeriksaan dan menu">
      {modeItems.map((item) => (
        <button key={item.mode} className={mode === item.mode ? "active" : ""} onClick={() => setMode(item.mode)} aria-label={item.label} aria-pressed={mode === item.mode} data-tip={item.label}>
          {item.short || <Icon name={item.icon} />}
        </button>
      ))}
      <span className="rail-divider" />
      {actions.map((item) => (
        <button key={item.label} onClick={() => openSheet(item.sheet)} aria-label={item.label} data-tip={item.label}><Icon name={item.icon} /></button>
      ))}
      <button onClick={() => setDark(!dark)} aria-label={dark ? "Gunakan mode terang" : "Gunakan mode gelap"} data-tip={dark ? "Mode terang" : "Mode gelap"}><Icon name="moon" /></button>
    </nav>
  );
}
