import type { EventStatus, RiskLevel, SecurityEvent, Stats } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";
const API_KEY = import.meta.env.VITE_API_KEY ?? "";

function buildQuery(params: Record<string, string | undefined>): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v) q.set(k, v);
  }
  const s = q.toString();
  return s ? `?${s}` : "";
}

export async function fetchEvents(filters: {
  risk_level?: RiskLevel | "";
  source?: string;
  status?: EventStatus | "";
}): Promise<SecurityEvent[]> {
  const query = buildQuery({
    risk_level: filters.risk_level || undefined,
    source: filters.source || undefined,
    status: filters.status || undefined,
  });
  const res = await fetch(`${API_BASE}/events${query}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchEvent(id: number): Promise<SecurityEvent> {
  const res = await fetch(`${API_BASE}/events/${id}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function updateEventStatus(id: number, status: EventStatus): Promise<SecurityEvent> {
  const res = await fetch(`${API_BASE}/events/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function ingestEvent(raw_log: string, source: string): Promise<SecurityEvent[]> {
  const res = await fetch(`${API_BASE}/events`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ raw_log, source }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
