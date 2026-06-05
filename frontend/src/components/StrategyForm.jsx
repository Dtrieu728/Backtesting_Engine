import { useState, useEffect } from "react";
import {
  getSymbols,
  getStrategies,
  runBacktest,
  getBacktestResult,
  validateTicker,
  runWalkForward,
} from "../api/client";
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
    use_live_data: false,
    start_date: "2010-01-01",
  });
  const [status, setStatus] = useState(null);
  const [useLiveData, setUseLiveData] = useState(false);
  const [tickerInput, setTickerInput] = useState("");
  const [tickerError, setTickerError] = useState(null);
  const [mode, setMode] = useState("backtest");

  useEffect(() => {
    getSymbols()
      .then((r) => {
        const data = r.data.symbols ?? r.data ?? [];
        setSymbols(Array.isArray(data) ? data : []);
      })
      .catch(() => {});

    getStrategies()
      .then((r) => {
        const data = r.data ?? [];
        setStrategies(Array.isArray(data) ? data : []);
      })
      .catch(() => {});
  }, []);

  const handleSymbolChange = (e) => {
    const selected = [...e.target.selectedOptions].map((o) => o.value);
    setConfig((c) => ({ ...c, symbols: selected }));
  };

  const handleAddTicker = async () => {
    const symbol = tickerInput.trim().toUpperCase();
    if (!symbol) return;
    try {
      await validateTicker(symbol);
      setConfig((c) => ({
        ...c,
        symbols: [...new Set([...c.symbols, symbol])],
      }));
      setTickerInput("");
      setTickerError(null);
    } catch {
      setTickerError(`${symbol} not found`);
    }
  };

  const handleDataSourceChange = (e) => {
    const live = e.target.value === "live";
    setUseLiveData(live);
    setConfig((c) => ({ ...c, use_live_data: live, symbols: [] }));
  };

  const handleSubmit = async () => {
    if (!config.symbols.length) return;
    setStatus("pending");
    try {
      const payload =
        mode === "walkforward"
          ? {
              symbols: config.symbols,
              strategy: config.strategy,
              initial_capital: config.initial_capital,
              use_live_data: config.use_live_data,
              start_date: config.start_date,
              train_years: 3,
              test_years: 1,
              short_periods: [10, 20, 30, 50],
              long_periods: [50, 100, 150, 200],
            }
          : config;

      const fn = mode === "walkforward" ? runWalkForward : runBacktest;
      const { data } = await fn(payload);
      const runId = data.run_id;

      const interval = setInterval(async () => {
        try {
          const result = await getBacktestResult(runId);
          if (result.data.status === "complete") {
            clearInterval(interval);
            setStatus("complete");
            onResults(result.data, { ...config, mode });
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
        <label className="sf-label">Mode</label>
        <select
          className="sf-select"
          value={mode}
          onChange={(e) => setMode(e.target.value)}
        >
          <option value="backtest">Backtest</option>
          <option value="walkforward">Walk Forward</option>
        </select>
      </div>

      <div className="sf-field">
        <label className="sf-label">Type</label>
        <select
          className="sf-select"
          value={config.strategy}
          onChange={(e) =>
            setConfig((c) => ({ ...c, strategy: e.target.value }))
          }
        >
          {strategies.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>

      <div className="sf-field">
        <label className="sf-label">Data source</label>
        <select
          className="sf-select"
          value={useLiveData ? "live" : "csv"}
          onChange={handleDataSourceChange}
        >
          <option value="csv">CSV files</option>
          <option value="live">Live data (yfinance)</option>
        </select>
      </div>

      {useLiveData ? (
        <div className="sf-field">
          <label className="sf-label">Add ticker</label>
          <div style={{ display: "flex", gap: 6 }}>
            <input
              className="sf-input"
              placeholder="e.g. AAPL"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddTicker()}
            />
            <button className="sf-add-btn" onClick={handleAddTicker}>
              +
            </button>
          </div>
          {tickerError && <span className="sf-error">{tickerError}</span>}
          <div className="sf-tags">
            {config.symbols.map((s) => (
              <span key={s} className="sf-symbol-tag">
                {s}
                <button
                  onClick={() =>
                    setConfig((c) => ({
                      ...c,
                      symbols: c.symbols.filter((x) => x !== s),
                    }))
                  }
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      ) : (
        <div className="sf-field">
          <label className="sf-label">Symbols</label>
          <select
            className="sf-select sf-multiselect"
            multiple
            value={config.symbols}
            onChange={handleSymbolChange}
          >
            {symbols.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <span className="sf-hint">Hold Ctrl to select multiple</span>
        </div>
      )}

      <div className="sf-divider" />
      <div className="sf-section-label">Parameters</div>

      <div className="sf-field">
        <label className="sf-label">Short period</label>
        <input
          className="sf-input"
          type="number"
          value={config.short_period}
          onChange={(e) =>
            setConfig((c) => ({ ...c, short_period: parseInt(e.target.value) }))
          }
        />
      </div>

      <div className="sf-field">
        <label className="sf-label">Long period</label>
        <input
          className="sf-input"
          type="number"
          value={config.long_period}
          onChange={(e) =>
            setConfig((c) => ({ ...c, long_period: parseInt(e.target.value) }))
          }
        />
      </div>

      <div className="sf-field">
        <label className="sf-label">Initial capital ($)</label>
        <input
          className="sf-input"
          type="number"
          value={config.initial_capital}
          onChange={(e) =>
            setConfig((c) => ({
              ...c,
              initial_capital: parseFloat(e.target.value),
            }))
          }
        />
      </div>

      <button
        className={`sf-run-btn ${status === "pending" ? "sf-run-btn--loading" : ""}`}
        onClick={handleSubmit}
        disabled={status === "pending" || !config.symbols.length}
      >
        {status === "pending" ? (
          <>
            <span className="sf-spinner" /> Running...
          </>
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
