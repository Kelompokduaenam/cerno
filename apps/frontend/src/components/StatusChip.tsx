import type { ReactNode } from "react";

export const StatusChip = ({ tone, children }: { tone: "ok" | "warn" | "bad" | "neutral"; children: ReactNode }) => <span className={`status status--${tone}`}>{children}</span>;
