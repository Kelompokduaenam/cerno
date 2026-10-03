import { useEffect, useRef, useState } from "react";
import WayangBackdrop from "./components/WayangBackdrop";
import StageHeader from "./components/StageHeader";
import CenterStage from "./components/CenterStage";
import Rail from "./components/Rail";
import InputArea from "./components/InputArea";
import DetailSheet from "./components/sheets/DetailSheet";
import OcrSheet from "./components/sheets/OcrSheet";
import ReportSheet from "./components/sheets/ReportSheet";
import HistorySheet from "./components/sheets/HistorySheet";
import LoginSheet from "./components/sheets/LoginSheet";
import AdminSheet from "./components/sheets/AdminSheet";
import { mockScore, riskFromScore } from "./lib/mockAnalysis";
import type { GuardianState, InputMode, Risk, SheetName } from "./types";

export default function App() {
  const [mode, setMode] = useState<InputMode>("text");
  const [value, setValue] = useState("");
  const [guardian, setGuardian] = useState<GuardianState>("idle");
  const [score, setScore] = useState(0);
  const [sheet, setSheet] = useState<SheetName>(null);
  const [dark, setDark] = useState(false);
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const timer = useRef<number | null>(null);

  const risk: Risk = riskFromScore(score);
  const isResult = guardian === "safe" || guardian === "suspicious" || guardian === "danger";
  const stageClass = guardian === "danger" ? "theme-danger" : guardian === "suspicious" ? "theme-amber" : "theme-safe";
  const closeSheet = () => setSheet(null);

  useEffect(() => () => { if (timer.current) window.clearTimeout(timer.current); }, []);

  const runAnalysis = (text = value) => {
    if (mode === "screenshot" && !text) { setSheet("ocr"); return; }
    const nextScore = mockScore(text);
    setSheet(null);
    setGuardian("scanning");
    timer.current = window.setTimeout(() => {
      setScore(nextScore);
      setGuardian(riskFromScore(nextScore));
    }, 1700);
  };
  const reset = () => { setSheet(null); setGuardian("idle"); setScore(0); setValue(""); };
  const changeMode = (next: InputMode) => { setMode(next); setGuardian("idle"); setScore(0); setValue(""); };

  return (
    <main
      className={`app ${stageClass} ${dark ? "dark" : ""}`}
      onPointerMove={(e) => setParallax({ x: (e.clientX / window.innerWidth - 0.5) * 10, y: (e.clientY / window.innerHeight - 0.5) * 10 })}
    >
      <div className="stage">
        <WayangBackdrop />
        <StageHeader onLogin={() => setSheet("login")} />
        <CenterStage guardian={guardian} isResult={isResult} risk={risk} score={score} parallax={parallax} />
        <div className="disclaimer">PENILAIAN RISIKO,<br />BUKAN KEPUTUSAN HUKUM<br />ATAU JAMINAN KEAMANAN</div>
        <Rail mode={mode} setMode={changeMode} openSheet={setSheet} dark={dark} setDark={setDark} />
        <InputArea
          mode={mode} setMode={setMode} value={value} setValue={setValue}
          guardian={guardian} isResult={isResult} risk={risk} score={score}
          onAnalyze={() => runAnalysis()} onReset={reset} openSheet={setSheet}
        />
      </div>

      {sheet === "detail" && <DetailSheet score={score} risk={risk} onClose={closeSheet} reset={reset} />}
      {sheet === "ocr" && <OcrSheet onClose={closeSheet} analyze={(text) => { setValue(text); setMode("text"); runAnalysis(text); }} />}
      {sheet === "report" && <ReportSheet onClose={closeSheet} />}
      {sheet === "history" && <HistorySheet onClose={closeSheet} openLogin={() => window.setTimeout(() => setSheet("login"), 100)} />}
      {sheet === "login" && <LoginSheet onClose={closeSheet} />}
      {sheet === "admin" && <AdminSheet onClose={closeSheet} />}
    </main>
  );
}
