import { useState, useEffect } from "react";
import { getSymbols, getStrategies, runBacktest, getBacktestResult } from "../api/client";

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
    getSymbols().then(r => setSymbols(r.data.symbols));
    getStrategies().then(r => setStrategies(r.data));
  }, []);

  const handleSubmit = async () => {
    setStatus("pending");
    const { data } = await runBacktest(config);
    const runId = data.run_id;

    // Poll until complete
    const interval = setInterval(async () => {
      const result = await getBacktestResult(runId);
      if (result.data.status === "complete") {
        clearInterval(interval);
        setStatus("complete");
        onResults(result.data);
      } else if (result.data.status === "error") {
        clearInterval(interval);
        setStatus("error");
      }
    }, 1000);
  };

  return (
    <div className="p-4 space-y-4">
      <select onChange={e => setConfig({...config, strategy: e.target.value})}>
        {strategies.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
      </select>

      <select multiple onChange={e => setConfig({...config, symbols: [...e.target.selectedOptions].map(o => o.value)})}>
        {symbols.map(s => <option key={s} value={s}>{s}</option>)}
      </select>

      <input type="number" placeholder="Short Period" value={config.short_period}
        onChange={e => setConfig({...config, short_period: parseInt(e.target.value)})} />
      <input type="number" placeholder="Long Period" value={config.long_period}
        onChange={e => setConfig({...config, long_period: parseInt(e.target.value)})} />
      <input type="number" placeholder="Initial Capital" value={config.initial_capital}
        onChange={e => setConfig({...config, initial_capital: parseFloat(e.target.value)})} />

      <button onClick={handleSubmit} disabled={status === "pending"}>
        {status === "pending" ? "Running..." : "Run Backtest"}
      </button>
    </div>
  );
}