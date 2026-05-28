"""semantic.py — Semantic string matching using sentence embeddings.
exports: SemanticMatcher class
used_by: mapper.py -> SemanticMatcher
rules:
Must use sentence-transformers. Load model lazily to avoid startup overhead.
"""

from typing import List, Dict, Any
import numpy as np

class SemanticMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        """Lazy load the sentence transformer model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError("sentence-transformers is required for semantic matching.")
        return self._model

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Computes cosine similarity between two 1D numpy arrays."""
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot / (norm1 * norm2))

    def match(self, source: str, targets: List[str], threshold: float = 0.6) -> List[Dict[str, Any]]:
        """
        Finds semantic matches using cosine similarity of sentence embeddings.
        Returns a sorted list (highest confidence first) of dictionaries:
        [{"target": str, "confidence": float}]
        """
        if not source or not targets:
            return []

        # Encode source string
        source_embedding = self.model.encode([source])[0]
        
        # Encode all target strings
        target_embeddings = self.model.encode(targets)
        
        matches = []
        for i, target in enumerate(targets):
            score = self._cosine_similarity(source_embedding, target_embeddings[i])
            if score >= threshold:
                matches.append({
                    "target": target,
                    "confidence": score
                })
                
        # Sort descending by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
