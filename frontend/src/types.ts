export type RiskLevel = "Benign" | "Suspicious" | "Malicious";

export type EventStatus = "Pending" | "Reviewed" | "False Positive" | "Escalated";

export interface SecurityEvent {
  id: number;
  raw_log: string;
  source: string;
  risk_level: RiskLevel;
  confidence: number;
  status: EventStatus;
  created_at: string;
}

export interface Stats {
  total_events: number;
  by_risk_level: Record<RiskLevel, number>;
  by_source: Record<string, number>;
}
