const BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";

async function jsonFetch(url, opts={}) {
  console.log("[API] →", url, opts);
  const res = await fetch(url, { ...opts, mode: "cors" });
  console.log("[API] ← status", res.status, res.statusText);
  const body = await res.json().catch(() => ({}));
  console.log("[API] ← body", body);
  return body;
}

export function ping() {
  return jsonFetch(`${BASE}/ping`);
}

export function uploadDocuments(documents) {
  return jsonFetch(`${BASE}/upload`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ documents }),
  });
}

export function search(query, top_k = 5) {
  return jsonFetch(`${BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });
}

export function ask(query, top_k = 5) {
  return jsonFetch(`${BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k }),
  });
}
