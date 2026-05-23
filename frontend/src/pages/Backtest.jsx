import { useState } from "react";
import StrategyForm from "../components/StrategyForm";
import EquityCurve from "../components/EquityCurve";
import StatsPanel from "../components/StatsPanel";
import "./Backtest.css";

export default function Backtest() {
  const [results, setResults] = useState(null);
  const [runConfig, setRunConfig] = useState(null);

  const handleResults = (data, config) => {
    setResults(data);
    setRunConfig(config);
  };

  return (
    <div className="bt-shell">
      <div className="bt-sidebar">
        <div className="bt-sidebar-header">
          <span className="bt-logo-icon"></span>
          <span className="bt-logo-text">Backtest</span>
        </div>
        <StrategyForm onResults={handleResults} />
      </div>

      <div className="bt-main">
        {!results ? (
          <div className="bt-empty">
            <div className="bt-empty-icon"></div>
            <p className="bt-empty-title">No results yet</p>
            <p className="bt-empty-sub">
              Configure a strategy and run a backtest to see results here.
            </p>
          </div>
        ) : (
          <>
            <div className="bt-main-header">
              <div>
                <h1 className="bt-page-title">Backtesting engine</h1>
                <p className="bt-page-sub">
                  {runConfig?.strategy} · {runConfig?.symbols?.join(", ")}
                </p>
              </div>
              <div className="bt-symbol-tags">
                {runConfig?.symbols?.map(s => (
                  <span key={s} className="bt-tag">{s}</span>
                ))}
              </div>
            </div>
            <StatsPanel stats={results.stats} />
            <EquityCurve data={results.equity_curve} config={runConfig} />
          </>
        )}
      </div>
    </div>
  );
}