import numpy as np
from typing import Dict, Any, List
from sklearn.metrics.pairwise import cosine_similarity
from backend.nlp.preprocessing import analyze_text

def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two 1D or 2D embedding vectors."""
    if vec1 is None or vec2 is None:
        return 0.0
    v1 = np.asarray(vec1).reshape(1, -1)
    v2 = np.asarray(vec2).reshape(1, -1)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    sim = cosine_similarity(v1, v2)[0][0]
    return float(np.clip(sim, 0.0, 1.0))

def compute_keyword_coverage(text1: str, text2: str) -> float:
    """Compute lemmatized keyword overlap between reference text and candidate text."""
    analysis1 = analyze_text(text1)
    analysis2 = analyze_text(text2)

    lemmas1 = set([l.lower() for l in analysis1.get("lemmas", []) if len(l) > 2 and l.lower() not in analysis1.get("stopwords", [])])
    lemmas2 = set([l.lower() for l in analysis2.get("lemmas", []) if len(l) > 2 and l.lower() not in analysis2.get("stopwords", [])])

    if not lemmas1:
        return 0.0

    overlap = lemmas1.intersection(lemmas2)
    coverage = len(overlap) / float(len(lemmas1))
    return round(coverage, 4)
