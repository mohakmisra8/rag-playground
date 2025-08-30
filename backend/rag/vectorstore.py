# backend/rag/vectorstore.py
import os
import uuid
from typing import List, Dict, Any

import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from .embeddings import embed_texts

# Persist to local ./chroma directory
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "chroma")

class OpenAIEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: List[str]) -> List[List[float]]:
        return embed_texts(input)

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name="docs",
    metadata={"hnsw:space": "cosine"},
    embedding_function=OpenAIEmbeddingFunction(),
)

def add_documents(docs: List[Dict[str, Any]]):
    """
    docs: [{"id": str (optional), "title": str, "text": str, "meta": dict}]
    """
    ids, documents, metadatas = [], [], []
    for d in docs:
        ids.append(d.get("id") or str(uuid.uuid4()))
        documents.append(d["text"])
        metadatas.append({"title": d.get("title", ""), **(d.get("meta") or {})})
    _collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return ids

def query_similar(query: str, n_results: int = 5):
    res = _collection.query(query_texts=[query], n_results=n_results)
    # Normalize result rows
    hits = []
    # res keys: ids, distances, documents, metadatas (each is list length=1 for one query)
    if res and res.get("ids"):
        for i in range(len(res["ids"][0])):
            hits.append({
                "id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i],
                "distance": res["distances"][0][i],  # cosine distance
            })
    return hits
