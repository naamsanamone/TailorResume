import logging
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

_model = None

def get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            import os
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            _model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            logger.error("sentence_transformers not installed.")
            raise ImportError("sentence_transformers package is required for embeddings.")
    return _model

def generate_embedding(text: str) -> List[float]:
    """Encode text and return list of floats."""
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """Batch encode texts."""
    model = get_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity using numpy."""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def compute_similarity(text1: str, text2: str) -> float:
    """Encode both texts and return cosine similarity."""
    if not text1.strip() or not text2.strip():
        return 0.0
    vec1 = generate_embedding(text1)
    vec2 = generate_embedding(text2)
    return cosine_similarity(vec1, vec2)
