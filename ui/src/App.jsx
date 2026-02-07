import { useEffect, useMemo, useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_BASE || "";


function chipStyle(kind) {
  const base = {
    display: "inline-block",
    padding: "6px 10px",
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 700,
    letterSpacing: 0.2,
    border: "1px solid transparent",
    lineHeight: 1,
  };

  if (kind === "GREEN")
    return { ...base, background: "#e8f7ee", color: "#137a3a", borderColor: "#bfe8cf" };
  if (kind === "AMBER")
    return { ...base, background: "#fff6e6", color: "#8a5a00", borderColor: "#ffe1a8" };
  return { ...base, background: "#ffe9e9", color: "#a31616", borderColor: "#ffc0c0" };
}

function severityFromState(state) {
  const s = (state || "").toUpperCase();
  if (s.includes("ESCALATED")) return "RED";
  if (s.includes("REMINDER")) return "AMBER";
  return "GREEN";
}

function severityLabel(sev) {
  if (sev === "GREEN") return "ON TRACK";
  return sev;
}

export default function App() {
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [taskData, setTaskData] = useState([]);

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState("");

  async function loadTasks() {
    try {
      setError("");
      setLoadingTasks(true);
      const res = await axios.get(`${API}/chaser/tasks`);
      setTaskData(res.data || []);
    } catch (e) {
      setError("Failed to load tasks. Is backend running on port 8000?");
    } finally {
      setLoadingTasks(false);
    }
  }

  async function runAsk() {
    if (!question.trim()) return;
    try {
      setError("");
      setAsking(true);
      const res = await axios.get(`${API}/intelligence/ask`, {
        params: { q: question.trim() },
      });
      setAnswer(res.data);
    } catch (e) {
      setError("Failed to run query. Check /intelligence/ask is working.");
    } finally {
      setAsking(false);
    }
  }

  useEffect(() => {
    loadTasks();
  }, []);

  const grouped = useMemo(() => {
    const m = new Map();
    for (const row of taskData) {
      if (!m.has(row.client)) m.set(row.client, []);
      m.get(row.client).push(...(row.tasks || []));
    }

    const pr = { high: 3, medium: 2, low: 1 };
    for (const [k, arr] of m.entries()) {
      arr.sort((a, b) => (pr[b.priority] || 0) - (pr[a.priority] || 0));
      m.set(k, arr);
    }

    return Array.from(m.entries()).map(([client, tasks]) => ({ client, tasks }));
  }, [taskData]);

  const clientSeverity = useMemo(() => {
    const pr = { RED: 3, AMBER: 2, GREEN: 1 };
    const out = {};
    for (const g of grouped) {
      let worst = "GREEN";
      for (const t of g.tasks) {
        const sev = severityFromState(t.state);
        if ((pr[sev] || 0) > (pr[worst] || 0)) worst = sev;
      }
      out[g.client] = worst;
    }
    return out;
  }, [grouped]);

  return (
    <div style={{ maxWidth: 980, margin: "0 auto", padding: 20, fontFamily: "system-ui, Arial" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12 }}>
        <h1 style={{ margin: 0 }}>Agentic Chaser</h1>
        <button
          onClick={loadTasks}
          disabled={loadingTasks}
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "1px solid #ddd",
            background: "#fff",
            cursor: "pointer",
            fontWeight: 700,
          }}
        >
          {loadingTasks ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div style={{ marginTop: 16, padding: 14, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontWeight: 800, marginBottom: 10 }}>Ask Intelligence</div>
        <div style={{ display: "flex", gap: 10 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Who discussed inheritance tax?"
            style={{
              flex: 1,
              padding: "10px 12px",
              borderRadius: 10,
              border: "1px solid #ddd",
              outline: "none",
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") runAsk();
            }}
          />
          <button
            onClick={runAsk}
            disabled={asking || !question.trim()}
            style={{
              padding: "10px 14px",
              borderRadius: 10,
              border: "1px solid #ddd",
              background: asking ? "#f7f7f7" : "#111",
              color: asking ? "#111" : "#fff",
              cursor: "pointer",
              fontWeight: 800,
            }}
          >
            {asking ? "Asking..." : "Search"}
          </button>
        </div>

        {answer?.results?.length ? (
          <div style={{ marginTop: 14 }}>
            <div style={{ fontWeight: 800, marginBottom: 8 }}>Results</div>
            <div style={{ display: "grid", gap: 10 }}>
              {answer.results.map((r, idx) => (
                <div key={idx} style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
                  <div style={{ fontWeight: 900 }}>{r.client}</div>
                  <div style={{ marginTop: 6, color: "#666", fontSize: 13 }}>Source: {r.source}</div>
                </div>
              ))}
            </div>
          </div>
        ) : answer ? (
          <div style={{ marginTop: 12, color: "#666" }}>No matches found.</div>
        ) : null}
      </div>

      {error ? (
        <div style={{ marginTop: 16, padding: 12, borderRadius: 10, background: "#fff2f2", color: "#a31616" }}>
          {error}
        </div>
      ) : null}

      <div style={{ marginTop: 18, display: "grid", gap: 14 }}>
        {grouped.map(({ client, tasks }) => {
          const cSev = clientSeverity[client] || "GREEN";
          return (
            <div key={client} style={{ border: "1px solid #eee", borderRadius: 14, padding: 14 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
                <div style={{ fontSize: 20, fontWeight: 950 }}>{client}</div>
                <span style={chipStyle(cSev)}>{severityLabel(cSev)}</span>
              </div>

              <div style={{ marginTop: 10, display: "grid", gap: 10 }}>
                {tasks.map((t, i) => {
                  const sev = severityFromState(t.state);
                  return (
                    <div
                      key={`${t.item}-${i}`}
                      style={{
                        border: "1px solid #eee",
                        borderRadius: 12,
                        padding: 12,
                        display: "grid",
                        gap: 6,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 10 }}>
                        <div style={{ fontWeight: 900 }}>
                          {t.item} <span style={{ fontWeight: 700, color: "#444" }}>({t.priority})</span>
                        </div>
                        <span style={chipStyle(sev)}>{severityLabel(sev)}</span>
                      </div>

                      <div style={{ color: "#333" }}>
                        <b>State:</b> {t.state}
                      </div>
                      <div style={{ color: "#333" }}>
                        <b>Due:</b> {t.due_date}
                      </div>
                      <div style={{ color: "#333" }}>
                        <b>Action:</b> {t.action}
                      </div>

                      {sev === "GREEN" ? (
                        <div style={{ fontSize: 12, color: "#137a3a" }}>No action required yet</div>
                      ) : null}

                      <div style={{ color: "#666", fontSize: 13 }}>
                        <b>Target:</b> {t.target} · <b>Required:</b> {t.required_for} · <b>Source:</b> {t.source}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: 18, color: "#666", fontSize: 13 }}>
        Tip: Update docs → run <b>python -m ingestion.build_tasks_from_docs</b> → hit <b>Refresh</b>.
      </div>
    </div>
  );
}
