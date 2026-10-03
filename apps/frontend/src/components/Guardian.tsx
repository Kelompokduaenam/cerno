import type { CSSProperties } from "react";
import type { GuardianState } from "../types";

export default function Guardian({ variant, score, parallax }: { variant: GuardianState; score?: number; parallax: { x: number; y: number } }) {
  const showScore = variant === "safe" || variant === "suspicious" || variant === "danger";
  return (
    <div className={`guardian guardian--${variant}`} style={{ "--px": `${parallax.x}px`, "--py": `${parallax.y}px` } as CSSProperties}>
      <svg className="guardian-ring" viewBox="0 0 400 400" aria-hidden="true">
        <path d="M200 29c37 0 54 17 84 30 30 12 58 13 77 39 19 25 13 53 18 84 5 31 19 55 7 84-12 30-40 39-64 60-24 21-37 47-69 53-31 6-54-13-85-17-31-4-58 6-83-13-25-19-25-48-37-77-12-29-34-49-29-81 5-31 31-45 50-70 19-25 25-53 55-66 29-13 49-26 76-26Z" />
        <circle className="ring-inner" cx="200" cy="200" r="169" />
      </svg>
      <div className="guardian-art">
        <svg viewBox="0 0 360 360" role="img" aria-label={`Guardian dalam keadaan ${variant}`}>
          <defs>
            <radialGradient id="orbBody" cx=".34" cy=".24" r=".82">
              <stop offset="0" stopColor="white" stopOpacity=".96" />
              <stop offset=".13" stopColor="var(--guardian-hi)" stopOpacity=".76" />
              <stop offset=".5" stopColor="var(--primary)" stopOpacity=".94" />
              <stop offset="1" stopColor="var(--guardian-low)" />
            </radialGradient>
            <radialGradient id="orbGlow">
              <stop stopColor="white" stopOpacity=".9" />
              <stop offset=".35" stopColor="var(--guardian-hi)" stopOpacity=".44" />
              <stop offset="1" stopColor="var(--primary)" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="orbRibbon" x1="0" y1="0" x2="1" y2="1">
              <stop stopColor="white" stopOpacity=".08" />
              <stop offset=".45" stopColor="white" stopOpacity=".72" />
              <stop offset="1" stopColor="var(--guardian-hi)" stopOpacity=".08" />
            </linearGradient>
            <clipPath id="orbClip"><circle cx="180" cy="180" r="142" /></clipPath>
            <filter id="orbShadow"><feDropShadow dx="0" dy="20" stdDeviation="18" floodColor="var(--guardian-low)" floodOpacity=".3" /></filter>
            <filter id="orbBlur"><feGaussianBlur stdDeviation="7" /></filter>
          </defs>
          <g filter="url(#orbShadow)">
            <circle className="orb-shell" cx="180" cy="180" r="144" fill="url(#orbBody)" />
            <g className="orb-energy" clipPath="url(#orbClip)">
              <ellipse cx="118" cy="102" rx="120" ry="46" fill="white" opacity=".14" transform="rotate(-22 118 102)" />
              <path d="M1 219C80 83 164 312 351 94 261 294 114 70 1 219Z" fill="url(#orbRibbon)" filter="url(#orbBlur)" />
              <path d="M36 105c87 5 89 184 266 154-156 77-218-29-266-154Z" fill="url(#orbRibbon)" opacity=".8" />
              <path d="M72 298c18-91 204-106 217-232 48 162-111 181-217 232Z" fill="url(#orbRibbon)" opacity=".68" />
              <path d="M66 139c72-104 199-54 233 55-80-83-180-22-233-55Z" fill="white" opacity=".13" />
              <circle cx="180" cy="180" r="95" fill="url(#orbGlow)" opacity=".6" />
            </g>
            <circle cx="180" cy="180" r="142" fill="none" stroke="white" strokeOpacity=".5" strokeWidth="2" />
            <path d="M78 100c32-49 86-71 139-60" fill="none" stroke="white" strokeOpacity=".72" strokeWidth="7" strokeLinecap="round" />
          </g>
        </svg>
        <div className="guardian-readout" aria-live="polite">
          {variant === "idle" && <span className="question-mark">?</span>}
          {variant === "scanning" && <span className="scan-mark"><i /><i /><i /></span>}
          {showScore && <><strong>{score}</strong><span>/100 · RISK SCORE</span></>}
        </div>
      </div>
    </div>
  );
}
