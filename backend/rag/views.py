# backend/rag/views.py
import json
import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .vectorstore import add_documents, query_similar
from .embeddings import client
from openai import OpenAIError

def ping(request):
    print("[VIEW] ping()")
    return JsonResponse({"ok": True})

@csrf_exempt
def upload_docs(request):
    print("[VIEW] upload_docs()", request.method)
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        docs = payload.get("documents", [])
        ids = add_documents(docs)
        print(f"[VIEW] upload_docs OK, added {len(ids)}")
        return JsonResponse({"added": len(ids), "ids": ids})
    except OpenAIError as e:
        # If embeddings via OpenAI failed and your embeddings.py didn’t catch it,
        # surface a helpful status. (Your embeddings.py should already fall back.)
        print("[VIEW] upload_docs OpenAIError:", e)
        return JsonResponse({"error": f"OpenAI error: {e}"}, status=429)
    except Exception as e:
        print("[VIEW] upload_docs ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def search_docs(request):
    print("[VIEW] search_docs()", request.method)
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        query = (payload.get("query") or "").strip()
        k = int(payload.get("top_k", 5))
        print(f"[VIEW] search payload query='{query}' top_k={k}")
        hits = query_similar(query, n_results=k)
        print(f"[VIEW] search_docs OK, hits={len(hits)}")
        return JsonResponse({"results": hits})
    except OpenAIError as e:
        # Should be rare since embeddings.py falls back locally,
        # but catch and return a clear 429 just in case.
        print("[VIEW] search_docs OpenAIError:", e)
        return JsonResponse({"error": f"OpenAI error: {e}"}, status=429)
    except Exception as e:
        print("[VIEW] search_docs ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def ask(request):
    """
    Simple RAG: retrieve top chunks, then (optionally) ask a chat model.
    If OPENAI_CHAT_MODEL is missing or generation fails, we return sources only.
    """
    print("[VIEW] ask()", request.method)
    if request.method != "POST":
        return HttpResponseBadRequest("POST only")
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
        query = (payload.get("query") or "").strip()
        k = int(payload.get("top_k", 5))
        print(f"[VIEW] ask payload query='{query}' top_k={k}")

        # 1) Retrieve (embeddings fallback handled in embeddings.py)
        hits = query_similar(query, n_results=k)
        print(f"[VIEW] ask retrieval OK, hits={len(hits)}")

        # 2) Generate (optional)
        model = os.getenv("OPENAI_CHAT_MODEL")
        if not model:
            print("[VIEW] ask no OPENAI_CHAT_MODEL → returning sources only")
            return JsonResponse({
                "answer": None,
                "sources": hits,
                "note": "Generator disabled; set OPENAI_CHAT_MODEL in .env to enable."
            })

        # Build prompt from retrieved context
        context = "\n\n---\n\n".join(
            f"[{i+1}] {h['metadata'].get('title','')}\n{h['text']}"
            for i, h in enumerate(hits)
        )
        prompt = (
            "You are a helpful assistant. Answer the USER question using only the CONTEXT.\n"
            "If the answer isn't in the CONTEXT, say you don't know.\n\n"
            f"CONTEXT:\n{context}\n\nUSER: {query}"
        )

        try:
            resp = client().responses.create(model=model, input=prompt)
            answer = resp.output_text if hasattr(resp, "output_text") else str(resp)
            print(f"[VIEW] ask generation OK, answer_len={len(answer)}")
            return JsonResponse({"answer": answer, "sources": hits})
        except OpenAIError as e:
            # Generation quota/other OpenAI error → keep app responsive with sources
            print("[VIEW] ask OpenAIError during generation:", e, "→ returning sources only")
            return JsonResponse({
                "answer": None,
                "sources": hits,
                "error": f"Generation failed: {e}"
            })

    except Exception as e:
        print("[VIEW] ask ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)
