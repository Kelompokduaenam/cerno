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
  onAnalyze: () => void;
  onReset: () => void;
  openSheet: (s: SheetName) => void;
};

export default function InputArea({ mode, setMode, value, setValue, guardian, isResult, risk, score, onAnalyze, onReset, openSheet }: Props) {
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
              <span><strong>Pilih screenshot percakapan…</strong><small>PNG, JPG · maks. 10 MB</small></span>
            </label>
            <input id="screenshot" type="file" accept="image/*" onChange={(e) => e.target.files?.[0] && openSheet("ocr")} />
            <Button onClick={() => openSheet("ocr")}>Ekstrak <span>→</span></Button>
          </>
        ) : (
          <>
            <div className="field-prefix">{mode === "url" ? "://" : "Aa"}</div>
            <input
              aria-label={mode === "url" ? "Masukkan URL" : "Masukkan teks pesan"}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={mode === "url" ? "Tempel URL yang ingin diperiksa…" : "Pesan apa yang bikin ragu?"}
            />
            <Button onClick={onAnalyze} disabled={!value.trim()}>Periksa <span>→</span></Button>
          </>
        )}
      </div>
    </div>
  );
}
