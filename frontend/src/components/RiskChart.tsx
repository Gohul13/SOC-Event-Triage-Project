import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { Stats } from "../types";

const COLORS: Record<string, string> = {
  Benign: "#22c55e",
  Suspicious: "#f59e0b",
  Malicious: "#ef4444",
};

interface Props {
  stats: Stats | null;
}

export function RiskChart({ stats }: Props) {
  const data = stats
    ? (["Benign", "Suspicious", "Malicious"] as const).map((name) => ({
        name,
        value: stats.by_risk_level[name] ?? 0,
      }))
    : [];

  return (
    <div className="card chart-card">
      <h2>Risk breakdown</h2>
      {data.every((d) => d.value === 0) ? (
        <p className="muted">No events yet — ingest logs or run the seed script.</p>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
              {data.map((entry) => (
                <Cell key={entry.name} fill={COLORS[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
