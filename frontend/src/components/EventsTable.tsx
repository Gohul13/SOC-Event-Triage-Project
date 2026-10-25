import type { EventStatus, RiskLevel, SecurityEvent } from "../types";

type SortKey = "created_at" | "risk_level" | "source" | "confidence" | "status";

interface Props {
  events: SecurityEvent[];
  loading: boolean;
  selectedId: number | null;
  onSelect: (id: number) => void;
  riskFilter: RiskLevel | "";
  sourceFilter: string;
  statusFilter: EventStatus | "";
  onRiskFilter: (v: RiskLevel | "") => void;
  onSourceFilter: (v: string) => void;
  onStatusFilter: (v: EventStatus | "") => void;
  sortKey: SortKey;
  sortAsc: boolean;
  onSort: (key: SortKey) => void;
}

function riskClass(level: RiskLevel): string {
  return `badge risk-${level.toLowerCase()}`;
}

function sortIndicator(active: boolean, asc: boolean): string {
  if (!active) return "";
  return asc ? " ▲" : " ▼";
}

export function EventsTable({
  events,
  loading,
  selectedId,
  onSelect,
  riskFilter,
  sourceFilter,
  statusFilter,
  onRiskFilter,
  onSourceFilter,
  onStatusFilter,
  sortKey,
  sortAsc,
  onSort,
}: Props) {
  return (
    <div className="card table-card">
      <div className="table-toolbar">
        <h2>Events</h2>
        <div className="filters">
          <select value={riskFilter} onChange={(e) => onRiskFilter(e.target.value as RiskLevel | "")}>
            <option value="">All risks</option>
            <option value="Benign">Benign</option>
            <option value="Suspicious">Suspicious</option>
            <option value="Malicious">Malicious</option>
          </select>
          <input
            value={sourceFilter}
            onChange={(e) => onSourceFilter(e.target.value)}
            placeholder="Filter source…"
          />
          <select value={statusFilter} onChange={(e) => onStatusFilter(e.target.value as EventStatus | "")}>
            <option value="">All statuses</option>
            <option value="Pending">Pending</option>
            <option value="Reviewed">Reviewed</option>
            <option value="False Positive">False Positive</option>
            <option value="Escalated">Escalated</option>
          </select>
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>
                <button type="button" className="th-btn" onClick={() => onSort("created_at")}>
                  Time{sortIndicator(sortKey === "created_at", sortAsc)}
                </button>
              </th>
              <th>
                <button type="button" className="th-btn" onClick={() => onSort("source")}>
                  Source{sortIndicator(sortKey === "source", sortAsc)}
                </button>
              </th>
              <th>
                <button type="button" className="th-btn" onClick={() => onSort("risk_level")}>
                  Risk{sortIndicator(sortKey === "risk_level", sortAsc)}
                </button>
              </th>
              <th>
                <button type="button" className="th-btn" onClick={() => onSort("confidence")}>
                  Conf.{sortIndicator(sortKey === "confidence", sortAsc)}
                </button>
              </th>
              <th>
                <button type="button" className="th-btn" onClick={() => onSort("status")}>
                  Status{sortIndicator(sortKey === "status", sortAsc)}
                </button>
              </th>
              <th>Log preview</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={6} className="muted center">
                  Loading…
                </td>
              </tr>
            )}
            {!loading && events.length === 0 && (
              <tr>
                <td colSpan={6} className="muted center">
                  No events match filters.
                </td>
              </tr>
            )}
            {!loading &&
              events.map((ev) => (
                <tr
                  key={ev.id}
                  className={ev.id === selectedId ? "selected" : ""}
                  onClick={() => onSelect(ev.id)}
                >
                  <td>{new Date(ev.created_at).toLocaleString()}</td>
                  <td>{ev.source}</td>
                  <td>
                    <span className={riskClass(ev.risk_level)}>{ev.risk_level}</span>
                  </td>
                  <td>{(ev.confidence * 100).toFixed(1)}%</td>
                  <td>{ev.status}</td>
                  <td className="log-preview">{ev.raw_log.slice(0, 72)}{ev.raw_log.length > 72 ? "…" : ""}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
