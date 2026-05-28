"""exact.py — Normalised exact matching for column names.
exports: normalize_string(s: str) -> str, exact_match(source: str, targets: list[str]) -> str | None
used_by: mapper.py -> exact_match
rules:
Must strip whitespace, lowercase, and remove special characters.
"""

import re
from typing import List, Optional

def normalize_string(s: str) -> str:
    """
    Normalizes a string by converting to lowercase, removing non-alphanumeric
    characters, and stripping whitespace.
    """
    if not isinstance(s, str):
        return ""
    # Lowercase
    s = s.lower()
    # Remove special characters, keep alphanumeric
    s = re.sub(r'[^a-z0-9]', '', s)
    return s.strip()

def exact_match(source: str, targets: List[str]) -> Optional[str]:
    """
    Finds an exact normalized match between the source string and a list of target strings.
    Returns the original target string if a match is found, else None.
    """
    norm_source = normalize_string(source)
    if not norm_source:
        return None
        
    for target in targets:
        if norm_source == normalize_string(target):
            return target
            
    return None
