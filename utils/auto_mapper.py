"""Auto-mapper for matching parsed field names to PDF AcroForm field names.
Strategy:
- Prefer sentence-transformers embeddings (if available) to compute semantic similarity.
- If sentence-transformers isn't installed, fall back to simple normalized string similarity (Levenshtein-like via difflib).

Public function: map_fields(parsed: Dict[str, Any], template_field_names: List[str]) -> Dict[str, Any]
Returns a mapping from template field name -> value (best-match) and a score for each mapping.
"""
from typing import Dict, Any, List, Tuple


def _normalize_label(s: str) -> str:
    return ''.join(c.lower() for c in s if c.isalnum())


def _fallback_similarity(a: str, b: str) -> float:
    """Simple fallback similarity based on prefix/common substring and difflib SequenceMatcher."""
    import difflib
    a2 = a.lower()
    b2 = b.lower()
    # score partial match
    base = difflib.SequenceMatcher(None, a2, b2).ratio()
    # boost if a token appears in b
    tokens = [t for t in a2.split() if len(t) > 2]
    bonus = 0.0
    for t in tokens:
        if t in b2:
            bonus += 0.15
    return min(1.0, base + bonus)


def map_fields(parsed: Dict[str, Any], template_field_names: List[str]) -> Dict[str, Tuple[Any, float]]:
    """Map parsed fields to template field names.
    Returns a dict: {template_field_name: (value, score)}
    """
    # try sentence-transformers if available
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer('all-MiniLM-L6-v2')
        parsed_labels = list(parsed.keys())
        # build candidate labels from template fields
        template_labels = template_field_names
        corpus = parsed_labels + template_labels
        embeddings = model.encode(corpus, convert_to_tensor=True)
        p_emb = embeddings[: len(parsed_labels)]
        t_emb = embeddings[len(parsed_labels):]
        mapping: Dict[str, Tuple[Any, float]] = {}
        # for each template label, find best parsed label
        for i, tlabel in enumerate(template_labels):
            sims = util.cos_sim(t_emb[i], p_emb)
            best_idx = int(sims.argmax())
            score = float(sims[best_idx])
            parsed_label = parsed_labels[best_idx]
            mapping[tlabel] = (parsed[parsed_label], score)
        return mapping
    except Exception:
        # fallback
        mapping: Dict[str, Tuple[Any, float]] = {}
        for tlabel in template_field_names:
            best_score = 0.0
            best_val = None
            for k, v in parsed.items():
                score = _fallback_similarity(k, tlabel)
                if score > best_score:
                    best_score = score
                    best_val = v
            mapping[tlabel] = (best_val, best_score)
        return mapping
