import logging
import numpy as np
from typing import List, Union
from sklearn.feature_extraction.text import HashingVectorizer

logger = logging.getLogger(__name__)

_model_instance = None
_hashing_vectorizer = HashingVectorizer(n_features=384, alternate_sign=False)

def get_sentence_transformer_model():
    global _model_instance
    if _model_instance is None:
        try:
            from sentence_transformers import SentenceTransformer
            try:
                _model_instance = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
            except Exception:
                _model_instance = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer loaded successfully.")
        except Exception as e:
            logger.warning(f"SentenceTransformer not loaded ({e}). Using HashingVectorizer fallback.")
            _model_instance = "FALLBACK"
    return _model_instance

def get_embedding(text: str) -> np.ndarray:
    """Generate dense 384-dimensional vector embedding for input text."""
    if not text:
        return np.zeros(384, dtype=np.float32)

    model = get_sentence_transformer_model()
    if model != "FALLBACK":
        try:
            return model.encode(text, convert_to_numpy=True)
        except Exception as e:
            logger.warning(f"Encoding via SentenceTransformer failed: {e}. Using HashingVectorizer.")

    # Instant offline fallback vector generator
    vec = _hashing_vectorizer.transform([text]).toarray()[0]
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec.astype(np.float32)

def get_embeddings(texts: List[str]) -> np.ndarray:
    """Batch generate dense embeddings."""
    if not texts:
        return np.empty((0, 384), dtype=np.float32)
    return np.array([get_embedding(t) for t in texts], dtype=np.float32)
