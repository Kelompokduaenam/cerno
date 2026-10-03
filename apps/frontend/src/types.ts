export type Risk = "safe" | "suspicious" | "danger";
export type GuardianState = "idle" | "scanning" | Risk;
export type InputMode = "text" | "url" | "screenshot";
export type SheetName = "detail" | "ocr" | "report" | "history" | "login" | "admin" | null;
