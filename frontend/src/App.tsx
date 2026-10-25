import { useCallback, useEffect, useMemo, useState } from "react";
import { fetchEvents, fetchStats, ingestEvent, updateEventStatus } from "./api";
import { EventDetailPanel } from "./components/EventDetailPanel";
import { EventsTable } from "./components/EventsTable";
import { IngestForm } from "./components/IngestForm";
import { RiskChart } from "./components/RiskChart";
import { StatsCards } from "./components/StatsCards";
import type { EventStatus, RiskLevel, SecurityEvent, Stats } from "./types";

type SortKey = "created_at" | "risk_level" | "source" | "confidence" | "status";

const RISK_ORDER: Record<RiskLevel, number> = {
  Malicious: 0,
  Suspicious: 1,
  Benign: 2,
};

export default function App() {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [riskFilter, setRiskFilter] = useState<RiskLevel | "">("");
  const [sourceFilter, setSourceFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState<EventStatus | "">("");
  const [sortKey, setSortKey] = useState<SortKey>("created_at");
  const [sortAsc, setSortAsc] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [ev, st] = await Promise.all([
        fetchEvents({
          risk_level: riskFilter,
          source: sourceFilter,
          status: statusFilter,
        }),
        fetchStats(),
      ]);
      setEvents(ev);
      setStats(st);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [riskFilter, sourceFilter, statusFilter]);

  useEffect(() => {
    void load();
  }, [load]);

  const sortedEvents = useMemo(() => {
    const copy = [...events];
    copy.sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "created_at":
          cmp = new Date(a.created_at).getTime() - new Date(b.created_at).getTime();
          break;
        case "risk_level":
          cmp = RISK_ORDER[a.risk_level] - RISK_ORDER[b.risk_level];
          break;
        case "source":
          cmp = a.source.localeCompare(b.source);
          break;
        case "confidence":
          cmp = a.confidence - b.confidence;
          break;
        case "status":
          cmp = a.status.localeCompare(b.status);
          break;
      }
      return sortAsc ? cmp : -cmp;
    });
    return copy;
  }, [events, sortKey, sortAsc]);

  const selected = events.find((e) => e.id === selectedId) ?? null;

  const onSort = (key: SortKey) => {
    if (sortKey === key) setSortAsc((v) => !v);
    else {
      setSortKey(key);
      setSortAsc(key === "source" || key === "status");
    }
  };

  const onStatusChange = async (status: EventStatus) => {
    if (!selected) return;
    try {
      const updated = await updateEventStatus(selected.id, status);
      setEvents((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
      const st = await fetchStats();
      setStats(st);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Update failed");
    }
  };

  const onIngest = async (raw_log: string, source: string) => {
    const created = await ingestEvent(raw_log, source);
    await load();
    if (created[0]) setSelectedId(created[0].id);
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Raksha SOC — Event Triage</h1>
          <p className="subtitle">ML-assisted classification for shift analysts</p>
        </div>
        <button type="button" className="btn secondary" onClick={() => void load()} disabled={loading}>
          Refresh
        </button>
      </header>

      {error && (
        <div className="banner error" role="alert">
          {error}
        </div>
      )}

      <section className="grid-top">
        <StatsCards stats={stats} loading={loading} />
        <RiskChart stats={stats} />
      </section>

      <section className="ingest-section">
        <IngestForm onSubmit={onIngest} />
      </section>

      <section className="main-grid">
        <EventsTable
          events={sortedEvents}
          loading={loading}
          selectedId={selectedId}
          onSelect={setSelectedId}
          riskFilter={riskFilter}
          sourceFilter={sourceFilter}
          statusFilter={statusFilter}
          onRiskFilter={setRiskFilter}
          onSourceFilter={setSourceFilter}
          onStatusFilter={setStatusFilter}
          sortKey={sortKey}
          sortAsc={sortAsc}
          onSort={onSort}
        />
        <EventDetailPanel event={selected} onStatusChange={onStatusChange} />
      </section>
    </div>
  );
}
