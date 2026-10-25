import re
from typing import Dict, Any, Optional
from backend.nlp.preprocessing import get_spacy_nlp

SUBJECT_DOMAINS = {
    "Natural Language Processing": ["token", "lemma", "nlp", "tfidf", "spacy", "nltk", "bert", "embedding", "transformer", "attention", "word2vec", "glove", "pos tag", "ner"],
    "Machine Learning": ["machine learning", "deep learning", "neural network", "overfit", "underfit", "regression", "classification", "clustering", "epoch", "loss", "gradient", "backprop", "ai", "supervised", "unsupervised"],
    "Database Management Systems": ["database", "dbms", "sql", "table", "norm", "1nf", "2nf", "3nf", "bcnf", "primary key", "foreign key", "join", "query", "indexing", "transaction", "acid", "er diagram"],
    "Software & Programming": ["python", "java", "c++", "javascript", "code", "function", "variable", "algorithm", "data structure", "array", "list", "dict", "tuple", "class", "object", "oop", "recursion", "decorator", "generator"],
    "Computer Networks & Security": ["network", "tcp", "udp", "ip", "protocol", "http", "https", "socket", "firewall", "cybersecurity", "encryption", "dns", "router", "port"],
    "Operating Systems": ["operating system", "os", "process", "thread", "deadlock", "memory", "paging", "kernel", "cpu", "semaphore", "virtual memory"],
    "Mathematics & Statistics": ["math", "calculus", "algebra", "matrix", "vector", "probability", "statistics", "derivative", "integral", "equation", "eigenvalue", "geometry"],
    "Physics & Natural Sciences": ["physics", "chemistry", "biology", "quantum", "thermodynamics", "photosynthesis", "atom", "molecule", "energy", "gravity", "force", "dna", "cell", "genetics"],
    "General Knowledge & Humanities": ["history", "geography", "literature", "economics", "philosophy", "language", "art", "music", "world", "society"]
}

class TopicClassifier:
    def predict(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip().lower()
        if not cleaned:
            return {"subject": "General Knowledge", "topic": "General", "confidence": 1.0}

        # Check domain keyword matches
        for subject, keywords in SUBJECT_DOMAINS.items():
            for kw in keywords:
                if kw in cleaned:
                    # Extract specific topic title using spaCy noun chunks if possible
                    topic_title = self._extract_topic_title(text, kw)
                    return {
                        "subject": subject,
                        "topic": topic_title,
                        "confidence": 0.92
                    }

        # Dynamic fallback using spaCy linguistic parsing for ANY arbitrary question
        topic_title = self._extract_topic_title(text, "")
        return {
            "subject": "General Knowledge & Science",
            "topic": topic_title,
            "confidence": 0.75
        }

    def _extract_topic_title(self, text: str, matched_kw: str) -> str:
        cleaned = text.lower()
        canonical_map = {
            "overfit": "Overfitting",
            "underfit": "Underfitting",
            "token": "Tokenization",
            "lemma": "Lemmatization",
            "tfidf": "TF-IDF",
            "norm": "Normalization",
            "1nf": "1NF",
            "2nf": "2NF",
            "3nf": "3NF",
            "bcnf": "BCNF",
            "sql": "SQL Querying",
            "transformer": "Transformers",
            "embedding": "Word Embeddings",
            "data structure": "Data Structures"
        }
        for key, val in canonical_map.items():
            if key in cleaned:
                return val

        nlp = get_spacy_nlp()
        doc = nlp(text)

        # Extract main noun chunks excluding stop word questions
        chunks = [chunk.text for chunk in doc.noun_chunks if not any(w in chunk.text.lower() for w in ["what", "how", "why", "who", "where", "can you", "explain", "tell me"])]
        if chunks:
            best_chunk = max(chunks, key=len).strip().title()
            if len(best_chunk) > 2:
                return best_chunk

        if matched_kw:
            return matched_kw.title()

        tokens = [t.text.title() for t in doc if t.is_alpha and not t.is_stop]
        return " ".join(tokens[:2]) if tokens else "General Inquiry"

_topic_classifier = TopicClassifier()

def detect_topic(text: str) -> Dict[str, Any]:
    return _topic_classifier.predict(text)

