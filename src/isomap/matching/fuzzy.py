"""fuzzy.py — Fuzzy string matching using rapidfuzz.
exports: fuzzy_match(source: str, targets: list[str], threshold: float) -> list[dict]
used_by: mapper.py -> fuzzy_match
rules:
Must use Jaro-Winkler similarity via rapidfuzz.
"""

from typing import List, Dict, Any
from rapidfuzz import process, distance
from isomap.matching.exact import normalize_string

def fuzzy_match(source: str, targets: List[str], threshold: float = 0.8) -> List[Dict[str, Any]]:
    """
    Finds fuzzy matches using normalized strings and Jaro-Winkler similarity.
    Returns a sorted list (highest confidence first) of dictionaries:
    [{"target": str, "confidence": float}]
    """
    norm_source = normalize_string(source)
    if not norm_source:
        return []
        
    # Create a mapping from normalized target back to original target
    target_map = {normalize_string(t): t for t in targets}
    norm_targets = list(target_map.keys())
    
    # Extract matches using Jaro-Winkler (returns (match, score, index))
    # rapidfuzz distance functions return scores from 0 to 1
    # process.extract returns scores from 0 to 100
    results = process.extract(
        norm_source, 
        norm_targets, 
        scorer=distance.JaroWinkler.normalized_similarity,
        limit=None
    )
    
    matches = []
    for match_str, score, _ in results:
        # score is already 0.0 to 1.0 because of normalized_similarity
        if score >= threshold:
            original_target = target_map[match_str]
            matches.append({
                "target": original_target,
                "confidence": score
            })
            
    # Sort descending by confidence
    matches.sort(key=lambda x: x["confidence"], reverse=True)
    return matches
