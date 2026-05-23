import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from "recharts";

export default function EquityCurve({ data }) {
  const chartData = data.map((v, i) => ({ bar: i, value: parseFloat(v.toFixed(4)) }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="bar" label={{ value: "Bar", position: "insideBottom" }} />
        <YAxis tickFormatter={v => `${((v - 1) * 100).toFixed(1)}%`} />
        <Tooltip formatter={v => `${((v - 1) * 100).toFixed(2)}%`} />
        <Line type="monotone" dataKey="value" stroke="#2563eb" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}