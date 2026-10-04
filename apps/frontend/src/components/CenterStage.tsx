import type { CSSProperties } from "react";
import Guardian from "./Guardian";
import { RISK_COPY } from "../lib/mockAnalysis";
import type { MockAnalysis } from "../lib/mockAnalysis";
import type { GuardianState, Risk } from "../types";

type Props = {
  guardian: GuardianState;
  isResult: boolean;
  risk: Risk;
  score: number;
  parallax: { x: number; y: number };
  analysis: MockAnalysis | null;
};

export default function CenterStage({ guardian, isResult, risk, score, parallax, analysis }: Props) {
  return (
    <div className="center-stage">
      {isResult && (
        <div className="risk-heading">
          <span className="risk-icon">{risk === "safe" ? "✓" : "!"}</span>
          <div><span>SIMULASI ANALISIS</span><h1>{RISK_COPY[risk]}</h1></div>
        </div>
      )}
      <div className="guardian-wrap">
        {isResult && analysis && analysis.findings.length > 0 && (
          <div className="evidence-cloud" aria-label="Pola yang ditemukan pada simulasi">
            {analysis.findings.slice(0, 4).map((item, index) => (
              <span key={item.title} style={{ "--i": index } as CSSProperties}>
                <i>!</i>{item.title}
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
