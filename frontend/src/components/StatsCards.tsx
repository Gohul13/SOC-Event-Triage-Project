import type { Stats } from "../types";

interface Props {
  stats: Stats | null;
  loading: boolean;
}

export function StatsCards({ stats, loading }: Props) {
  const total = stats?.total_events ?? 0;
  const malicious = stats?.by_risk_level.Malicious ?? 0;
  const suspicious = stats?.by_risk_level.Suspicious ?? 0;
  const benign = stats?.by_risk_level.Benign ?? 0;

  return (
    <div className="stats-cards">
      <div className="card stat">
        <span className="label">Total events</span>
        <strong>{loading ? "—" : total}</strong>
      </div>
      <div className="card stat malicious">
        <span className="label">Malicious</span>
        <strong>{loading ? "—" : malicious}</strong>
      </div>
      <div className="card stat suspicious">
        <span className="label">Suspicious</span>
        <strong>{loading ? "—" : suspicious}</strong>
      </div>
      <div className="card stat benign">
        <span className="label">Benign</span>
        <strong>{loading ? "—" : benign}</strong>
      </div>
    </div>
  );
}
