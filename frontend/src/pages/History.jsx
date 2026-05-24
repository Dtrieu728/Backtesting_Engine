import { useState, useEffect } from "react";
import { getBacktestHistory } from "../api/client";
import EquityCurve from "../components/EquityCurve";
import "./History.css";

export default function History() {
  const [runs, setRuns] = useState([]);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    getBacktestHistory().then(r => setRuns(r.data)).catch(() => {});
  }, []);

  const formatDate = (str) => new Date(str).toLocaleDateString("en-US", {
    month: "short", day: "numeric", year: "numeric",
    hour: "2-digit", minute: "2-digit"
  });

  const getReturn = (stats) => {
    if (!stats) return null;
    const entry = Object.entries(stats).find(([k]) => k === "Total Return");
    return entry ? entry[1] : null;
  };

  return (
    <div className="hs-shell">
      <div className="hs-sidebar">
        <div className="hs-sidebar-header">
          <span className="hs-logo-icon"></span>
          <span className="hs-logo-text">History</span>
        </div>
        <div className="hs-list">
          {runs.length === 0 && (
            <p className="hs-empty">No backtest runs yet.</p>
          )}
          {runs.map(run => {
            const ret = getReturn(run.stats);
            const isPos = ret && !ret.startsWith("-");
            return (
              <div
                key={run.run_id}
                className={`hs-item ${selected?.run_id === run.run_id ? "hs-item--active" : ""}`}
                onClick={() => setSelected(run)}
              >
                <div className="hs-item-top">
                  <span className="hs-item-strategy">{run.strategy}</span>
                  {ret && (
                    <span className={`hs-item-return ${isPos ? "pos" : "neg"}`}>
                      {ret}
                    </span>
                  )}
                </div>
                <div className="hs-item-bottom">
                  <span className="hs-item-symbols">{run.symbols?.join(", ")}</span>
                  <span className="hs-item-date">{formatDate(run.created_at)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="hs-main">
        {!selected ? (
          <div className="hs-empty-state">
            <div className="hs-empty-icon"></div>
            <p className="hs-empty-title">Select a run to view details</p>
          </div>
        ) : (
          <>
            <div className="hs-main-header">
              <div>
                <h1 className="hs-title">{selected.strategy}</h1>
                <p className="hs-sub">
                  {selected.symbols?.join(", ")} · EMA {selected.short_period}/{selected.long_period} · {formatDate(selected.created_at)}
                </p>
              </div>
              <div className="hs-tags">
                {selected.symbols?.map(s => (
                  <span key={s} className="hs-tag">{s}</span>
                ))}
              </div>
            </div>

            {selected.stats && (
              <div className="hs-stats-grid">
                {Object.entries(selected.stats).map(([key, value]) => {
                  const num = parseFloat(value);
                  const isNeg = !isNaN(num) && num < 0;
                  const isPos = !isNaN(num) && num > 0 && key !== "Max Drawdown";
                  return (
                    <div key={key} className={`hs-stat-card ${isNeg ? "neg" : isPos ? "pos" : "neu"}`}>
                      <div className="hs-stat-label">{key}</div>
                      <div className={`hs-stat-value ${isNeg ? "neg" : isPos ? "pos" : "neu"}`}>{value}</div>
                    </div>
                  );
                })}
              </div>
            )}

            {selected.equity_curve && (
              <EquityCurve
                data={selected.equity_curve}
                config={{ strategy: selected.strategy, symbols: selected.symbols }}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
}