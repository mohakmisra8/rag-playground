import { useState, useEffect } from "react";
import { uploadDocuments, search, ask, ping } from "./api";
import DocumentUploader from "./components/DocumentUploader";
import QueryBox from "./components/QueryBox";
import ResultsList from "./components/ResultsList";

export default function App() {
  const [results, setResults] = useState([]);
  const [answer, setAnswer] = useState(undefined); // undefined = not asked yet

  useEffect(() => {
    ping()
      .then((r) => console.log("[PING OK]", r))
      .catch((e) => console.error("[PING ERROR]", e));
  }, []);

  async function handleUploaded(docs) {
    try {
      const res = await uploadDocuments(docs);
      console.log("[UPLOAD OK]", res);
      alert(`Added ${res.added} document(s).`);
    } catch (e) {
      console.error("[UPLOAD ERROR]", e);
      alert("Upload failed. See console.");
    }
  }

  async function handleSearch(q) {
    setAnswer(undefined);
    try {
      const res = await search(q, 5);
      console.log("[SEARCH OK]", res);
      setResults(res.results || []);
    } catch (e) {
      console.error("[SEARCH ERROR]", e);
    }
  }

  async function handleAsk(q) {
    try {
      const res = await ask(q, 5);
      console.log("[ASK OK]", res);
      setResults(res.sources || res.results || []);
      setAnswer(res.answer ?? null);
    } catch (e) {
      console.error("[ASK ERROR]", e);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "24px auto", display: "grid", gap: 16 }}>
      <h1>RAG Playground</h1>
      <DocumentUploader onUploaded={handleUploaded} />
      <QueryBox onSearch={handleSearch} onAsk={handleAsk} />
      <ResultsList results={results} answer={answer} />
    </div>
  );
}
