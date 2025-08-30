export default function ResultsList({ results = [], answer }) {
  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      {answer !== undefined && (
        <>
          <h3>Answer</h3>
          <p>{answer || "No generator configured; showing sources below."}</p>
          <hr />
        </>
      )}
      <h3>Top Matches</h3>
      {results.length === 0 ? <p>No results yet.</p> : null}
      {results.map((r, idx) => (
        <div key={r.id || idx} style={{ marginBottom: 12 }}>
          <strong>{r.metadata?.title || `Result ${idx + 1}`}</strong>
          <div style={{ fontSize: 12, opacity: 0.7 }}>
            distance: {r.distance?.toFixed?.(4)}
          </div>
          <p style={{ whiteSpace: "pre-wrap" }}>{r.text.slice(0, 400)}{r.text.length > 400 ? "…" : ""}</p>
        </div>
      ))}
    </div>
  );
}
