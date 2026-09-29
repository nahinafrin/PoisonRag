"""Stage 3 - dense retrieval: BGE-M3 embeddings (L2-normalised) + FAISS inner
product = cosine similarity. Any retriever can be plugged in instead: the pipeline
only needs a function question -> list[str] (the TrustRAG benchmark passes the
protocol's Contriever top-k this way)."""
from __future__ import annotations

import numpy as np

from .poison_consensus_filter import embed


class FaissRetriever:
    def __init__(self, texts: list[str]):
        import faiss
        self.texts = list(texts)
        vecs = embed(self.texts).astype("float32")
        self.index = faiss.IndexFlatIP(vecs.shape[1])
        self.index.add(vecs)

    def __call__(self, question: str, k: int = 5) -> list[str]:
        q = embed([question]).astype("float32")
        _s, idx = self.index.search(q, min(k, len(self.texts)))
        return [self.texts[i] for i in idx[0] if i >= 0]
