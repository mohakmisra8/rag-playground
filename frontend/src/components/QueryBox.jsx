import { useState } from "react";

export default function QueryBox({ onSearch, onAsk }) {
  const [q, setQ] = useState("");

  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <h3>Query</h3>
      <input
        placeholder="Ask or search…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        style={{ width: "100%", marginBottom: 8, padding: 8 }}
      />
      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => onSearch(q)}>Semantic Search</button>
        <button onClick={() => onAsk(q)}>Ask (RAG)</button>
      </div>
    </div>
  );
}
