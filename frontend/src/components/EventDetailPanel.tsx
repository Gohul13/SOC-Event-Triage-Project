import type { EventStatus, SecurityEvent } from "../types";

const STATUSES: EventStatus[] = ["Reviewed", "False Positive", "Escalated"];

interface Props {
  event: SecurityEvent | null;
  onStatusChange: (status: EventStatus) => Promise<void>;
}

export function EventDetailPanel({ event, onStatusChange }: Props) {
  if (!event) {
    return (
      <div className="card detail-card">
        <h2>Event detail</h2>
        <p className="muted">Select a row to inspect classification and update triage status.</p>
      </div>
    );
  }

  return (
    <div className="card detail-card">
      <h2>Event #{event.id}</h2>
      <dl className="detail-grid">
        <dt>Source</dt>
        <dd>{event.source}</dd>
        <dt>Risk</dt>
        <dd>
          <span className={`badge risk-${event.risk_level.toLowerCase()}`}>{event.risk_level}</span>
        </dd>
        <dt>Confidence</dt>
        <dd>{(event.confidence * 100).toFixed(2)}%</dd>
        <dt>Status</dt>
        <dd>{event.status}</dd>
        <dt>Received</dt>
        <dd>{new Date(event.created_at).toLocaleString()}</dd>
      </dl>

      <h3>Raw log</h3>
      <pre className="raw-log">{event.raw_log}</pre>

      <h3>Analyst action</h3>
      <div className="status-actions">
        {STATUSES.map((s) => (
          <button
            key={s}
            type="button"
            className={`btn ${event.status === s ? "primary" : "secondary"}`}
            onClick={() => void onStatusChange(s)}
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
