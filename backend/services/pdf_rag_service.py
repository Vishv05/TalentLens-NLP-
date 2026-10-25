import os
import uuid
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from backend.nlp.preprocessing import get_spacy_nlp
from backend.nlp.embeddings import get_embedding, get_embeddings
from backend.nlp.similarity import compute_cosine_similarity
from backend.utils.db import get_db

logger = logging.getLogger(__name__)

class DocumentRAGService:
    """
    RAG Service for processing, sentence-chunking, embedding,
    and retrieving custom student lecture notes and syllabus documents.
    """

    def process_and_index_text(self, user_id: str, title: str, raw_text: str) -> Dict[str, Any]:
        if not raw_text or not raw_text.strip():
            raise ValueError("Document text cannot be empty.")

        # Chunk document into sentences using spaCy
        nlp = get_spacy_nlp()
        doc = nlp(raw_text.strip())

        # Sentence chunking with overlap
        sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 8]
        if not sentences:
            sentences = [raw_text.strip()]

        chunks = []
        chunk_size = 3
        for i in range(0, len(sentences), chunk_size):
            chunk_text = " ".join(sentences[i:i + chunk_size])
            if chunk_text:
                chunks.append(chunk_text)

        if not chunks:
            chunks = [raw_text.strip()]

        # Generate dense embeddings for chunks
        chunk_embeddings = get_embeddings(chunks)

        doc_id = str(uuid.uuid4())
        chunk_records = []
        for idx, chunk_str in enumerate(chunks):
            chunk_records.append({
                "chunk_index": idx,
                "text": chunk_str,
                "embedding": chunk_embeddings[idx].tolist()
            })

        doc_record = {
            "doc_id": doc_id,
            "user_id": user_id,
            "title": title or "Custom Lecture Notes",
            "chunk_count": len(chunks),
            "chunks": chunk_records,
            "raw_text_preview": raw_text[:250] + ("..." if len(raw_text) > 250 else "")
        }

        db = get_db()
        db.user_documents.insert_one(doc_record)

        return {
            "doc_id": doc_id,
            "title": title,
            "chunks_indexed": len(chunks)
        }

    def search_user_documents(self, user_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        db = get_db()
        user_docs = list(db.user_documents.find({"user_id": user_id}))
        if not user_docs:
            return []

        query_vec = get_embedding(query)
        matches = []

        for doc_item in user_docs:
            doc_title = doc_item.get("title", "Lecture Note")
            for chunk in doc_item.get("chunks", []):
                chunk_vec = chunk.get("embedding")
                if chunk_vec:
                    sim = compute_cosine_similarity(query_vec, chunk_vec)
                    matches.append({
                        "doc_id": doc_item.get("doc_id"),
                        "doc_title": doc_title,
                        "chunk_index": chunk.get("chunk_index", 0),
                        "chunk_text": chunk.get("text", ""),
                        "similarity_score": round(sim * 100, 2)
                    })

        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:top_k]

    def list_user_documents(self, user_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        user_docs = list(db.user_documents.find({"user_id": user_id}))
        out = []
        for d in user_docs:
            out.append({
                "doc_id": d.get("doc_id"),
                "title": d.get("title"),
                "chunk_count": d.get("chunk_count", 0),
                "raw_text_preview": d.get("raw_text_preview", "")
            })
        return out

    def delete_user_document(self, user_id: str, doc_id: str) -> bool:
        db = get_db()
        res = db.user_documents.delete_one({"user_id": user_id, "doc_id": doc_id})
        return res.deleted_count > 0

_doc_rag_service = DocumentRAGService()

def get_document_rag_service():
    return _doc_rag_service
