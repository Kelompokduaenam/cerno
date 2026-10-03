import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { Icon } from "./Icon";

export default function Sheet({ title, eyebrow, onClose, children, wide = false }: { title: string; eyebrow: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  const closeRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    closeRef.current?.focus();
    const close = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", close);
    return () => window.removeEventListener("keydown", close);
  }, [onClose]);
  return (
    <div className="sheet-backdrop" role="presentation" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <section className={`sheet ${wide ? "sheet--wide" : ""}`} role="dialog" aria-modal="true" aria-labelledby="sheet-title">
        <div className="sheet-handle" />
        <header className="sheet-header">
          <div><span className="eyebrow">{eyebrow}</span><h2 id="sheet-title">{title}</h2></div>
          <button ref={closeRef} className="icon-button" onClick={onClose} aria-label="Tutup panel"><Icon name="close" /></button>
        </header>
        <div className="sheet-body">{children}</div>
      </section>
    </div>
  );
}
