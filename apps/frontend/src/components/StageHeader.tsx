export default function StageHeader({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="stage-top">
      <button className="login-chip" onClick={onLogin}>Masuk</button>
      <div className="brand"><b>CERNO</b><span>BEDAKAN SEBELUM PERCAYA</span></div>
    </div>
  );
}
