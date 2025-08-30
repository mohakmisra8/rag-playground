# backend/rag/embeddings.py
import os
from typing import List
from openai import OpenAI, OpenAIError

EMBED_MODEL = "text-embedding-3-small"

_client = None
_local_model = None

def client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("[OPENAI] client created. key present?", bool(os.getenv("OPENAI_API_KEY")))
    return _client

def _embed_openai(texts: List[str]) -> List[List[float]]:
    print(f"[EMBED] calling OpenAI for {len(texts)} text(s) with {EMBED_MODEL}")
    resp = client().embeddings.create(model=EMBED_MODEL, input=texts)
    vecs = [d.embedding for d in resp.data]
    print("[EMBED] success via OpenAI")
    return vecs

def _embed_local(texts: List[str]) -> List[List[float]]:
    global _local_model
    if _local_model is None:
        print("[EMBED] loading local model: all-MiniLM-L6-v2")
        from sentence_transformers import SentenceTransformer
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    vecs = _local_model.encode(texts, normalize_embeddings=True).tolist()
    print(f"[EMBED] success via local model (all-MiniLM-L6-v2), {len(texts)} text(s)")
    return vecs

def embed_texts(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    # Try OpenAI first if a key exists; fall back on any OpenAIError (e.g., insufficient_quota)
    try:
        if os.getenv("OPENAI_API_KEY"):
            return _embed_openai(texts)
        else:
            print("[EMBED] no OPENAI_API_KEY in env → using local model")
            return _embed_local(texts)
    except OpenAIError as e:
        print("[EMBED] OpenAIError:", e, "→ falling back to local model")
        return _embed_local(texts)
