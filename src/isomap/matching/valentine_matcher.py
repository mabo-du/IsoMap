"""valentine_matcher.py — Valentine ensemble matcher wrapper.
exports: ValentineMatcher class
used_by: mapper.py -> ValentineMatcher
rules:
Must lazily load valentine to avoid startup overhead.
"""

import pandas as pd
from typing import List, Dict, Any
import warnings

class ValentineMatcher:
    def __init__(self):
        self._valentine_match = None
        self._algorithms = None
        
    def _lazy_load(self):
        if self._valentine_match is None:
            try:
                from valentine import valentine_match
                from valentine.algorithms import Coma, JaccardDistanceMatcher, Cupid
                self._valentine_match = valentine_match
                # We use Schema-only matchers because target is just a list of column names, not instances
                self._algorithms = [
                    Coma(use_instances=False, use_schema=True),
                    Cupid()
                ]
            except ImportError:
                raise ImportError("Valentine is required for ensemble matching.")
                
    def match(self, source_col: str, source_series: pd.Series, targets: List[str]) -> List[Dict[str, Any]]:
        self._lazy_load()
        
        # Build dummy dataframe for target with columns = targets, 0 rows
        df1 = pd.DataFrame({source_col: source_series.astype(str)})
        df2 = pd.DataFrame(columns=targets)
        
        best_scores = {}
        for algo in self._algorithms:
            try:
                # Suppress warnings from Valentine/NLTK
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    matches_algo = self._valentine_match([df1, df2], algo)
                
                for pair, score in matches_algo.items():
                    # pair is a ColumnPair object in valentine 1.0
                    c1, c2 = pair.source_column, pair.target_column
                    if c1 == source_col and c2 in targets:
                        if c2 not in best_scores or score > best_scores[c2]:
                            best_scores[c2] = float(score)
            except Exception as e:
                # Some algorithms might fail on 0 instances or specific data types.
                # print(f"Valentine algo {algo.__class__.__name__} failed: {e}")
                continue
                
        # Format results
        results = [{"target": t, "confidence": s} for t, s in best_scores.items() if s > 0.0]
        results.sort(key=lambda x: x["confidence"], reverse=True)
        return results
