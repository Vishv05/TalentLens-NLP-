import json
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.nlp.embeddings import get_embedding, get_embeddings
from backend.nlp.similarity import compute_cosine_similarity

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base" / "knowledge_base.json"

class KnowledgeService:
    _instance = None

    def __init__(self):
        self.knowledge_items: List[Dict[str, Any]] = []
        self.embeddings_matrix = None
        self.load_knowledge_base()

    def load_knowledge_base(self):
        if not KB_PATH.exists():
            logger.error(f"Knowledge base file not found at {KB_PATH}")
            self.knowledge_items = []
            return

        with open(KB_PATH, "r", encoding="utf-8") as f:
            self.knowledge_items = json.load(f)

        # Index knowledge base text into embeddings
        texts_to_embed = [
            f"{item.get('title', '')}. {item.get('definition', '')} {item.get('explanation', '')}"
            for item in self.knowledge_items
        ]
        if texts_to_embed:
            self.embeddings_matrix = get_embeddings(texts_to_embed)
            logger.info(f"Knowledge base indexed successfully with {len(self.knowledge_items)} concepts.")

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        if not self.knowledge_items or self.embeddings_matrix is None:
            return []

        query_vec = get_embedding(query)
        scores = []
        for idx, item_vec in enumerate(self.embeddings_matrix):
            sim = compute_cosine_similarity(query_vec, item_vec)
            scores.append((sim, self.knowledge_items[idx]))

        # Sort descending by similarity score
        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for sim, item in scores[:top_k]:
            res = dict(item)
            res["similarity_score"] = round(sim * 100, 2)
            results.append(res)
        return results

_knowledge_service = None

def get_knowledge_service():
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service
