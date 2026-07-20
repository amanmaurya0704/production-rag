"""A small demo module used to show code-aware (document-aware) chunking."""

import math
from typing import List


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Return the cosine similarity between two equal-length vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class VectorStore:
    """A minimal in-memory vector store for demos and tests."""

    def __init__(self):
        self._vectors: List[List[float]] = []
        self._metadata: List[dict] = []

    def add(self, vector: List[float], metadata: dict) -> None:
        self._vectors.append(vector)
        self._metadata.append(metadata)

    def search(self, query_vector: List[float], top_k: int = 3) -> List[dict]:
        scored = [
            (cosine_similarity(query_vector, v), m)
            for v, m in zip(self._vectors, self._metadata)
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [m for _, m in scored[:top_k]]

    def filter(self, **conditions) -> "VectorStore":
        """Return a new VectorStore containing only entries matching all conditions."""
        filtered = VectorStore()
        for v, m in zip(self._vectors, self._metadata):
            if all(m.get(k) == val for k, val in conditions.items()):
                filtered.add(v, m)
        return filtered
