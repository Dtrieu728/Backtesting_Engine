export default function StatsPanel({ stats }) {
  return (
    <div className="grid grid-cols-2 gap-4 p-4">
      {Object.entries(stats).map(([key, value]) => (
        <div key={key} className="bg-gray-100 rounded p-3">
          <div className="text-sm text-gray-500">{key}</div>
          <div className="text-xl font-bold">{value}</div>
        </div>
      ))}
    </div>
  );
}