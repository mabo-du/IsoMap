"""semantic.py — Semantic string matching using sentence embeddings.
exports: SemanticMatcher class
used_by: mapper.py -> SemanticMatcher
rules:
Must use optimum.onnxruntime and transformers. Load model lazily to avoid startup overhead.
"""

from typing import List, Dict, Any
import numpy as np
import os
from pathlib import Path

class SemanticMatcher:
    def __init__(self, model_name: str = "assets/models/scibert_onnx_quantized"):
        self.model_name = model_name
        self._model = None
        self._tokenizer = None

    def _lazy_load(self):
        """Lazy load the ONNX model and tokenizer."""
        if self._model is None or self._tokenizer is None:
            try:
                from optimum.onnxruntime import ORTModelForFeatureExtraction
                from transformers import AutoTokenizer
                
                # Resolve path relative to project root if it's local
                model_path = self.model_name
                if not os.path.isabs(model_path):
                    # Assume running from project root or find absolute path
                    base_dir = Path(__file__).parent.parent.parent.parent
                    model_path = str(base_dir / self.model_name)
                    
                self._tokenizer = AutoTokenizer.from_pretrained(model_path)
                self._model = ORTModelForFeatureExtraction.from_pretrained(model_path)
            except ImportError:
                raise ImportError("optimum[onnxruntime] and transformers are required for semantic matching.")
            except Exception as e:
                raise RuntimeError(f"Failed to load ONNX model from {model_path}: {e}")

    def _mean_pooling(self, last_hidden_state: np.ndarray, attention_mask: np.ndarray) -> np.ndarray:
        """Mean pooling for token embeddings using numpy."""
        input_mask_expanded = np.expand_dims(attention_mask, -1)
        input_mask_expanded = np.broadcast_to(input_mask_expanded, last_hidden_state.shape)
        
        sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(input_mask_expanded, axis=1), a_min=1e-9, a_max=None)
        return sum_embeddings / sum_mask

    def _encode(self, texts: List[str]) -> np.ndarray:
        self._lazy_load()
        # Tokenize
        encoded_input = self._tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        
        # We can pass the tensors directly to the ORTModel
        outputs = self._model(**encoded_input)
        
        # Get embeddings (numpy array)
        last_hidden_state = outputs.last_hidden_state.detach().numpy()
        attention_mask = encoded_input['attention_mask'].numpy()
        
        # Pool
        sentence_embeddings = self._mean_pooling(last_hidden_state, attention_mask)
        
        # Normalize
        norms = np.linalg.norm(sentence_embeddings, axis=1, keepdims=True)
        norms = np.clip(norms, a_min=1e-12, a_max=None)
        return sentence_embeddings / norms

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
        source_embedding = self._encode([source])[0]
        
        # Encode all target strings
        target_embeddings = self._encode(targets)
        
        matches = []
        for i, target in enumerate(targets):
            # Since vectors are already normalized, cosine similarity is just the dot product
            score = float(np.dot(source_embedding, target_embeddings[i]))
            if score >= threshold:
                matches.append({
                    "target": target,
                    "confidence": score
                })
                
        # Sort descending by confidence
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
