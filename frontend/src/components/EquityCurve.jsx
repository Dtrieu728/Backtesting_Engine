import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer
} from "recharts";
import "./EquityCurve.css";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const val = payload[0].value;
    const pct = ((val - 1) * 100).toFixed(2);
    const isPos = pct >= 0;
    return (
      <div className="ec-tooltip">
        <div className="ec-tooltip-bar">Bar {label}</div>
        <div className={`ec-tooltip-val ${isPos ? "pos" : "neg"}`}>
          {isPos ? "+" : ""}{pct}%
        </div>
      </div>
    );
  }
  return null;
};

export default function EquityCurve({ data, config }) {
  if (!data || !data.length) return null;

  const chartData = data
    .filter(v => v !== null && v !== undefined)
    .map((v, i) => ({ bar: i, value: parseFloat(v.toFixed(6)) }));

  const finalVal = chartData[chartData.length - 1]?.value ?? 1;
  const isPositive = finalVal >= 1;
  const strokeColor = isPositive ? "#c8f04a" : "#e24b4a";

  const tickCount = 8;
  const step = Math.floor(chartData.length / tickCount);
  const xTicks = chartData
    .filter((_, i) => i % step === 0)
    .map(d => d.bar);

  return (
    <div className="ec-card">
      <div className="ec-header">
        <div>
          <div className="ec-title">Equity curve</div>
          {config && (
            <div className="ec-sub">
              {config.strategy} · {config.symbols?.join(", ")}
            </div>
          )}
        </div>
        <div className={`ec-return ${isPositive ? "pos" : "neg"}`}>
          {isPositive ? "+" : ""}{((finalVal - 1) * 100).toFixed(2)}%
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="ecGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity={0.15} />
              <stop offset="100%" stopColor={strokeColor} stopOpacity={0.01} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#1e1e1e" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="bar"
            ticks={xTicks}
            tick={{ fill: "#555", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tickFormatter={v => `${((v - 1) * 100).toFixed(0)}%`}
            tick={{ fill: "#555", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={52}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="value"
            stroke={strokeColor}
            strokeWidth={1.5}
            fill="url(#ecGradient)"
            dot={false}
            activeDot={{ r: 4, fill: strokeColor, strokeWidth: 0 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}