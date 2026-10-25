import { FormEvent, useState } from "react";

interface Props {
  onSubmit: (raw_log: string, source: string) => Promise<void>;
}

export function IngestForm({ onSubmit }: Props) {
  const [rawLog, setRawLog] = useState("");
  const [source, setSource] = useState("firewall");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      await onSubmit(rawLog.trim(), source.trim());
      setRawLog("");
      setMsg("Event ingested and classified.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Ingest failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="card ingest-form" onSubmit={(e) => void handleSubmit(e)}>
      <h2>Ingest log line</h2>
      <p className="muted">Requires API key in frontend `.env` (write endpoint).</p>
      <label>
        Source
        <input value={source} onChange={(e) => setSource(e.target.value)} placeholder="firewall, ids, auth…" />
      </label>
      <label>
        Raw log
        <textarea
          rows={3}
          value={rawLog}
          onChange={(e) => setRawLog(e.target.value)}
          placeholder="Paste a security log line…"
          required
        />
      </label>
      <button type="submit" className="btn primary" disabled={busy || !rawLog.trim()}>
        {busy ? "Classifying…" : "Submit event"}
      </button>
      {msg && <p className="form-msg">{msg}</p>}
    </form>
  );
}
