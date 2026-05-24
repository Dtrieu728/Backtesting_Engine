import { useState, useEffect } from "react";
import { getSymbols, getStrategies, runBacktest, getBacktestResult } from "../api/client";
import "./StrategyForm.css";

export default function StrategyForm({ onResults }) {
  const [symbols, setSymbols] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [config, setConfig] = useState({
    symbols: [],
    strategy: "long_only",
    short_period: 20,
    long_period: 50,
    initial_capital: 100000,
  });
  const [status, setStatus] = useState(null);

  useEffect(() => {
    getSymbols().then(r => {
      const data = r.data.symbols ?? r.data ?? [];
      setSymbols(Array.isArray(data) ? data : []);
    }).catch(() => {});
  
    getStrategies().then(r => {
      const data = r.data ?? [];
      setStrategies(Array.isArray(data) ? data : []);
    }).catch(() => {});
    }, []);

  const handleSymbolChange = (e) => {
    const selected = [...e.target.selectedOptions].map(o => o.value);
    setConfig(c => ({ ...c, symbols: selected }));
  };

  const handleSubmit = async () => {
    if (!config.symbols.length) return;
    setStatus("pending");
    try {
      const { data } = await runBacktest(config);
      const runId = data.run_id;
      const interval = setInterval(async () => {
        try {
          const result = await getBacktestResult(runId);
          if (result.data.status === "complete") {
            clearInterval(interval);
            setStatus("complete");
            onResults(result.data, config); // ← passes config as second arg
          } else if (result.data.status === "error") {
            clearInterval(interval);
            setStatus("error");
          }
        } catch {
          clearInterval(interval);
          setStatus("error");
        }
      }, 1000);
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="sf-form">
      <div className="sf-section-label">Strategy</div>

      <div className="sf-field">
        <label className="sf-label">Type</label>
        <select
          className="sf-select"
          value={config.strategy}
          onChange={e => setConfig(c => ({ ...c, strategy: e.target.value }))}
        >
          {strategies.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      <div className="sf-field">
        <label className="sf-label">Symbols</label>
        <select
          className="sf-select sf-multiselect"
          multiple
          value={config.symbols}
          onChange={handleSymbolChange}
        >
          {symbols.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <span className="sf-hint">Hold Ctrl to select multiple</span>
      </div>

      <div className="sf-divider" />
      <div className="sf-section-label">Parameters</div>

      <div className="sf-field">
        <label className="sf-label">Short period</label>
        <input
          className="sf-input"
          type="number"
          value={config.short_period}
          onChange={e => setConfig(c => ({ ...c, short_period: parseInt(e.target.value) }))}
        />
      </div>

      <div className="sf-field">
        <label className="sf-label">Long period</label>
        <input
          className="sf-input"
          type="number"
          value={config.long_period}
          onChange={e => setConfig(c => ({ ...c, long_period: parseInt(e.target.value) }))}
        />
      </div>

      <div className="sf-field">
        <label className="sf-label">Initial capital ($)</label>
        <input
          className="sf-input"
          type="number"
          value={config.initial_capital}
          onChange={e => setConfig(c => ({ ...c, initial_capital: parseFloat(e.target.value) }))}
        />
      </div>

      <button
        className={`sf-run-btn ${status === "pending" ? "sf-run-btn--loading" : ""}`}
        onClick={handleSubmit}
        disabled={status === "pending" || !config.symbols.length}
      >
        {status === "pending" ? (
          <><span className="sf-spinner" /> Running...</>
        ) : (
          "Run backtest"
        )}
      </button>

      {status === "error" && (
        <p className="sf-error">Something went wrong. Check the console.</p>
      )}
    </div>
  );
}