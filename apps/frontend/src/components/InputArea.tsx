import { useEffect, useState } from "react";
import { Icon } from "./Icon";
import { Button } from "./Button";
import { RESULT_HEADLINE, RISK_COPY } from "../lib/mockAnalysis";
import type { GuardianState, InputMode, Risk, SheetName } from "../types";

type Props = {
  mode: InputMode;
  setMode: (m: InputMode) => void;
  value: string;
  setValue: (v: string) => void;
  guardian: GuardianState;
  isResult: boolean;
  risk: Risk;
  score: number;
  screenshot: File | null;
  onSelectScreenshot: (file: File | null) => void;
  onAnalyze: () => void;
  onReset: () => void;
  openSheet: (s: SheetName) => void;
};

export default function InputArea({ mode, setMode, value, setValue, guardian, isResult, risk, score, screenshot, onSelectScreenshot, onAnalyze, onReset, openSheet }: Props) {
  const [error, setError] = useState("");
  useEffect(() => setError(""), [mode]);
  const selectScreenshot = (file?: File) => {
    if (!file) return;
    if (!["image/png", "image/jpeg"].includes(file.type)) {
      onSelectScreenshot(null);
      setError("Gunakan gambar PNG atau JPG.");
      return;
    }
    if (file.size > 5_000_000) {
      onSelectScreenshot(null);
      setError("Ukuran gambar maksimal 5 MB.");
      return;
    }
    setError("");
    onSelectScreenshot(file);
    openSheet("ocr");
  };
  const analyzeInput = () => {
    if (mode === "url") {
      try {
        const url = new URL(value.trim());
        if (!["http:", "https:"].includes(url.protocol) || !url.hostname) throw new Error("invalid");
      } catch {
        setError("Masukkan URL lengkap yang diawali http:// atau https://.");
        return;
      }
    }
    setError("");
    onAnalyze();
  };
  return (
    <div className={`input-area ${isResult ? "input-area--result" : ""}`}>
      {guardian === "idle" && (
        <button
          className="example-link"
          onClick={() => { setMode("text"); setValue("Akun Anda akan diblokir. Klik sekarang dan kirim OTP untuk verifikasi."); }}
        >
          COBA CONTOH PESAN <span>↗</span>
        </button>
      )}
      {isResult && <button className="example-link" onClick={onReset}>↺ PERIKSA BAHAN LAIN</button>}

      <div className="input-pill">
        {guardian === "scanning" ? (
          <div className="loading-copy"><i /><span>Mencari sinyal risiko…</span><small>Memeriksa struktur, konteks, dan sumber</small></div>
        ) : isResult ? (
          <>
            <div className="result-copy">
              <span>{RISK_COPY[risk]} · {score}/100</span>
              <strong>{RESULT_HEADLINE[risk]}</strong>
            </div>
            <Button onClick={() => openSheet("detail")}>Lihat alasan <span>↑</span></Button>
          </>
        ) : mode === "screenshot" ? (
          <>
            <label className="upload-copy" htmlFor="screenshot">
              <Icon name="image" />
              <span><strong>{screenshot ? screenshot.name : "Pilih screenshot percakapan…"}</strong><small>PNG, JPG · maks. 5 MB · simulasi OCR</small></span>
            </label>
            <input key="screenshot-input" id="screenshot" type="file" accept="image/png,image/jpeg" onChange={(e) => { selectScreenshot(e.target.files?.[0]); e.target.value = ""; }} />
            <Button onClick={() => openSheet("ocr")} disabled={!screenshot}>Tinjau <span>→</span></Button>
          </>
        ) : (
          <>
            <div className="field-prefix">{mode === "url" ? "://" : "Aa"}</div>
            <input
              key="message-input"
              aria-label={mode === "url" ? "Masukkan URL" : "Masukkan teks pesan"}
              value={value}
              onChange={(e) => { setValue(e.target.value); setError(""); }}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.nativeEvent.isComposing && value.trim()) {
                  e.preventDefault();
                  analyzeInput();
                }
              }}
              placeholder={mode === "url" ? "Tempel URL yang ingin diperiksa…" : "Pesan apa yang bikin ragu?"}
            />
            <Button onClick={analyzeInput} disabled={!value.trim()}>Periksa <span>→</span></Button>
          </>
        )}
      </div>
      {error && <p className="input-error" role="alert">{error}</p>}
    </div>
  );
}
