import { useState } from "react";
import StrategyForm from "../components/StrategyForm";
import EquityCurve from "../components/EquityCurve";
import StatsPanel from "../components/StatsPanel";

export default function Backtest() {
  const [results, setResults] = useState(null);

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-2xl font-bold mb-6">Backtesting Engine</h1>
      <StrategyForm onResults={setResults} />
      {results && (
        <>
          <StatsPanel stats={results.stats} />
          <EquityCurve data={results.equity_curve} />
        </>
      )}
    </div>
  );
}