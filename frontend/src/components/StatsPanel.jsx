import "./StatsPanel.css";

function classify(key, value) {
  const num = parseFloat(value);
  if (isNaN(num)) return "neu";
  if (key === "Total Return" || key === "Sharpe Ratio") {
    return num >= 0 ? "pos" : "neg";
  }
  if (key === "Max Drawdown") return num > 20 ? "neg" : "warn";
  return "neu";
}

export default function StatsPanel({ stats }) {
  const entries = Object.entries(stats);

  return (
    <div className="sp-grid">
      {entries.map(([key, value]) => {
        const cls = classify(key, value);
        return (
          <div key={key} className={`sp-card sp-card--${cls}`}>
            <div className="sp-label">{key}</div>
            <div className={`sp-value sp-value--${cls}`}>{value}</div>
          </div>
        );
      })}
    </div>
  );
}