import type { CSSProperties } from "react";
import Guardian from "./Guardian";
import { EVIDENCE, RISK_COPY } from "../lib/mockAnalysis";
import type { GuardianState, Risk } from "../types";

type Props = {
  guardian: GuardianState;
  isResult: boolean;
  risk: Risk;
  score: number;
  parallax: { x: number; y: number };
};

export default function CenterStage({ guardian, isResult, risk, score, parallax }: Props) {
  const evidence = EVIDENCE[risk];
  return (
    <div className="center-stage">
      {isResult && (
        <div className="risk-heading">
          <span className="risk-icon">{risk === "safe" ? "✓" : "!"}</span>
          <div><span>HASIL ANALISIS</span><h1>{RISK_COPY[risk]}</h1></div>
        </div>
      )}
      <div className="guardian-wrap">
        {isResult && (
          <div className="evidence-cloud" aria-label="Bukti risiko">
            {evidence.map((item, index) => (
              <span key={item} style={{ "--i": index } as CSSProperties}>
                <i>{risk === "safe" ? "✓" : "!"}</i>{item}
              </span>
            ))}
          </div>
        )}
        <Guardian variant={guardian} score={score} parallax={parallax} />
      </div>
      {guardian === "scanning" && (
        <div className="scan-caption"><span /><b>Membandingkan pola pesan</b><small>Mohon tunggu, jangan buka tautan dulu.</small></div>
      )}
    </div>
  );
}
