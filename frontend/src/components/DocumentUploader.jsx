import { useState } from "react";

export default function DocumentUploader({ onUploaded }) {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");

  async function handleUpload() {
    if (!text.trim()) return;
    const doc = { title, text };
    await onUploaded([doc]);
    setTitle("");
    setText("");
  }

  return (
    <div style={{ border: "1px solid #ddd", padding: 16, borderRadius: 8 }}>
      <h3>Upload a Document</h3>
      <input
        placeholder="Title (optional)"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        style={{ width: "100%", marginBottom: 8, padding: 8 }}
      />
      <textarea
        placeholder="Paste text here…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={6}
        style={{ width: "100%", marginBottom: 8, padding: 8 }}
      />
      <button onClick={handleUpload}>Add to Vector DB</button>
    </div>
  );
}
