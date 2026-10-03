export default function WayangBackdrop() {
  return (
    <div className="wayang-backdrop" aria-hidden="true">
      <div className="wayang-aura" />
      <div className="wayang-visual">
        <img className="wayang-artwork" src="/assets/wayang-safe.png" alt="" />
        <div className="wayang-state wayang-state--amber" />
        <div className="wayang-state wayang-state--danger" />
        <div className="wayang-sheen" />
      </div>
    </div>
  );
}
