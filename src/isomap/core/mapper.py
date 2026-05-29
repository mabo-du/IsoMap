"""mapper.py — Orchestrates the 6-stage column matching pipeline.
exports: ColumnMapper class
used_by: main.py -> ColumnMapper
rules:
Pipeline: Exact -> Preferences -> Fuzzy -> Semantic -> Distribution
"""

import pandas as pd
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from isomap.matching.exact import exact_match, normalize_string
from isomap.matching.fuzzy import fuzzy_match
from isomap.matching.semantic import SemanticMatcher
from isomap.matching.valentine_matcher import ValentineMatcher
from isomap.matching.preferences import PreferenceCache
from isomap.matching.distribution import infer_column_types

class ColumnMapper:
    def __init__(self, db_path: str = "data/preferences.db", schema_dir: str = "data/schemas"):
        self.pref_cache = PreferenceCache(db_path)
        self.semantic_matcher = SemanticMatcher()
        self.valentine_matcher = ValentineMatcher()
        self.schema_dir = Path(schema_dir)
        
    def _load_schema_fields(self, schema_name: str) -> List[str]:
        """Loads required and optional fields from a JSON schema."""
        schema_path = self.schema_dir / f"{schema_name}.json"
        if not schema_path.exists():
            return []
            
        with open(schema_path, "r") as f:
            schema = json.load(f)
            
        return list(schema.get("properties", {}).keys())

    def map_columns(self, df: pd.DataFrame, schema_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Maps all columns in the DataFrame to the target schema using a hierarchical pipeline.
        Returns a dictionary mapping source columns to a ranked list of suggestions.
        """
        targets = self._load_schema_fields(schema_name)
        if not targets:
            raise ValueError(f"Schema {schema_name} not found or has no properties.")
            
        inferred_types = infer_column_types(df)
        results = {}
        
        for col in df.columns:
            suggestions = self._match_column(col, df[col], targets, inferred_types[col], schema_name)
            results[col] = suggestions
            
        return results

    def _match_column(self, col: str, series: pd.Series, targets: List[str], inferred: Dict[str, Any], schema_name: str) -> List[Dict[str, Any]]:
        """Runs the 6-stage fallback pipeline for a single column."""
        norm_col = normalize_string(col)
        
        # 1. Exact Match
        exact = exact_match(col, targets)
        if exact:
            return [{"target": exact, "confidence": 1.0, "method": "exact"}]
            
        # 2. User Preferences
        pref = self.pref_cache.get_preference(norm_col, repository=schema_name)
        if pref and pref in targets:
            return [{"target": pref, "confidence": 0.95, "method": "preference"}]
            
        # Initialize candidate pool
        candidates = {}
        
        # 3. Fuzzy Match
        fuz_matches = fuzzy_match(col, targets, threshold=0.7)
        for match in fuz_matches:
            target = match["target"]
            candidates[target] = {"target": target, "confidence": match["confidence"] * 0.8, "method": "fuzzy"}
            
        # 4. Semantic Embedding Match
        sem_matches = self.semantic_matcher.match(col, targets, threshold=0.5)
        for match in sem_matches:
            target = match["target"]
            score = match["confidence"] * 0.8
            if target not in candidates or candidates[target]["confidence"] < score:
                candidates[target] = {"target": target, "confidence": score, "method": "semantic"}
                
        # 5. Valentine Ensemble Match
        val_matches = self.valentine_matcher.match(col, series, targets)
        for match in val_matches:
            target = match["target"]
            score = match["confidence"] * 0.85
            if target not in candidates or candidates[target]["confidence"] < score:
                candidates[target] = {"target": target, "confidence": score, "method": "valentine"}
                
        # 6. Value Distribution Profiling (heuristic-based overrides based on inferred type)
        dist_suggestions = self._map_inferred_to_target(inferred, targets)
        for target, score in dist_suggestions.items():
            if target not in candidates or candidates[target]["confidence"] < score:
                candidates[target] = {"target": target, "confidence": score, "method": "distribution"}
                
        # Sort all candidates by confidence descending
        sorted_candidates = sorted(candidates.values(), key=lambda x: x["confidence"], reverse=True)
        return sorted_candidates

    def _map_inferred_to_target(self, inferred: Dict[str, Any], targets: List[str]) -> Dict[str, float]:
        """Maps an inferred semantic type to likely target schema fields."""
        inf_type = inferred.get("type", "unknown")
        inf_conf = inferred.get("confidence", "low")
        
        if inf_type == "unknown" or inf_conf == "low":
            return {}
            
        # Base confidence scalar
        conf_scalar = 0.9 if inf_conf == "high" else 0.7
        
        suggestions = {}
        # Simple heuristic mappings
        if inf_type == "latitude":
            for t in targets:
                if t.lower() in ["latitude", "lat"]:
                    suggestions[t] = conf_scalar
        elif inf_type == "longitude":
            for t in targets:
                if t.lower() in ["longitude", "lon", "long"]:
                    suggestions[t] = conf_scalar
        elif inf_type == "d13C":
            for t in targets:
                if t.lower() in ["d13c", "delta13c"]:
                    suggestions[t] = conf_scalar
        elif inf_type == "taxon_name":
            for t in targets:
                if t.lower() in ["taxonname", "taxon", "species"]:
                    suggestions[t] = conf_scalar
        elif inf_type == "14C BP":
            for t in targets:
                if t.lower() in ["age", "14cbp", "radiocarbon_age"]:
                    suggestions[t] = conf_scalar
                    
        return suggestions
        
    def save_override(self, source_column: str, target_field: str, schema_name: str):
        """Saves a user manual override (Stage 6) to the preference cache."""
        norm_source = normalize_string(source_column)
        self.pref_cache.store_preference(norm_source, target_field, repository=schema_name)
