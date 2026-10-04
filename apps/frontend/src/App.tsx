import { useEffect, useRef, useState } from "react";
import { flushSync } from "react-dom";
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
import { mockAnalyze, riskFromScore } from "./lib/mockAnalysis";
import type { MockAnalysis } from "./lib/mockAnalysis";
import type { GuardianState, InputMode, Risk, SheetName } from "./types";

export default function App() {
  const [mode, setMode] = useState<InputMode>("text");
  const [value, setValue] = useState("");
  const [guardian, setGuardian] = useState<GuardianState>("idle");
  const [score, setScore] = useState(0);
  const [analysis, setAnalysis] = useState<MockAnalysis | null>(null);
  const [screenshot, setScreenshot] = useState<File | null>(null);
  const [sheet, setSheet] = useState<SheetName>(null);
  const [dark, setDark] = useState(false);
  const [parallax, setParallax] = useState({ x: 0, y: 0 });
  const timer = useRef<number | null>(null);
  const themeTransition = useRef(false);

  const risk: Risk = riskFromScore(score);
  const isResult = guardian === "safe" || guardian === "suspicious" || guardian === "danger";
  const stageClass = guardian === "danger" ? "theme-danger" : guardian === "suspicious" ? "theme-amber" : "theme-safe";
  const closeSheet = () => setSheet(null);

  const cancelAnalysis = () => {
    if (timer.current !== null) window.clearTimeout(timer.current);
    timer.current = null;
  };
  useEffect(() => () => { if (timer.current !== null) window.clearTimeout(timer.current); }, []);

  const runAnalysis = (text = value, source = mode) => {
    cancelAnalysis();
    if (source === "screenshot" && !text) { if (screenshot) setSheet("ocr"); return; }
    const nextAnalysis = mockAnalyze(text, source);
    setSheet(null);
    setAnalysis(null);
    setGuardian("scanning");
    timer.current = window.setTimeout(() => {
      setAnalysis(nextAnalysis);
      setScore(nextAnalysis.score);
      setGuardian(riskFromScore(nextAnalysis.score));
      timer.current = null;
    }, 1700);
  };
  const reset = () => { cancelAnalysis(); setSheet(null); setGuardian("idle"); setScore(0); setAnalysis(null); setValue(""); setScreenshot(null); };
  const changeMode = (next: InputMode) => { cancelAnalysis(); setMode(next); setGuardian("idle"); setScore(0); setAnalysis(null); setValue(""); setScreenshot(null); };

  const toggleTheme = (button: HTMLButtonElement) => {
    if (themeTransition.current) return;
    const next = !dark;
    if (!document.startViewTransition || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      setDark(next);
      return;
    }

    const rect = button.getBoundingClientRect();
    const x = rect.left + rect.width / 2;
    const y = rect.top + rect.height / 2;
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    const root = document.documentElement;
    root.style.setProperty("--theme-reveal-x", `${x}px`);
    root.style.setProperty("--theme-reveal-y", `${y}px`);
    root.style.setProperty("--theme-reveal-radius", `${radius}px`);
    root.classList.add("theme-switching");
    themeTransition.current = true;

    const transition = document.startViewTransition(() => flushSync(() => setDark(next)));
    const cleanup = () => {
      root.classList.remove("theme-switching");
      root.style.removeProperty("--theme-reveal-x");
      root.style.removeProperty("--theme-reveal-y");
      root.style.removeProperty("--theme-reveal-radius");
      themeTransition.current = false;
    };
    void transition.finished.then(cleanup, cleanup);
  };

  return (
    <main
      className={`app ${stageClass} ${dark ? "dark" : ""}`}
      onPointerMove={(e) => setParallax({ x: (e.clientX / window.innerWidth - 0.5) * 10, y: (e.clientY / window.innerHeight - 0.5) * 10 })}
    >
      <div className="stage">
        <WayangBackdrop />
        <StageHeader onLogin={() => setSheet("login")} />
        <CenterStage guardian={guardian} isResult={isResult} risk={risk} score={score} parallax={parallax} analysis={analysis} />
        <div className="disclaimer">PENILAIAN RISIKO,<br />BUKAN KEPUTUSAN HUKUM<br />ATAU JAMINAN KEAMANAN</div>
        <Rail mode={mode} setMode={changeMode} openSheet={setSheet} dark={dark} onToggleTheme={toggleTheme} />
        <InputArea
          mode={mode} setMode={setMode} value={value} setValue={setValue}
          guardian={guardian} isResult={isResult} risk={risk} score={score}
          screenshot={screenshot} onSelectScreenshot={setScreenshot}
          onAnalyze={() => runAnalysis()} onReset={reset} openSheet={setSheet}
        />
      </div>

      {sheet === "detail" && analysis && <DetailSheet analysis={analysis} onClose={closeSheet} reset={reset} />}
      {sheet === "ocr" && screenshot && <OcrSheet file={screenshot} onClose={closeSheet} analyze={(text) => { setValue(text); runAnalysis(text, "screenshot"); }} />}
      {sheet === "report" && <ReportSheet onClose={closeSheet} />}
      {sheet === "history" && <HistorySheet onClose={closeSheet} openLogin={() => window.setTimeout(() => setSheet("login"), 100)} />}
      {sheet === "login" && <LoginSheet onClose={closeSheet} />}
      {sheet === "admin" && <AdminSheet onClose={closeSheet} />}
    </main>
  );
}
