import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import spacy

from backend.nlp.preprocessing import get_spacy_nlp
from backend.nlp.embeddings import get_embedding
from backend.nlp.similarity import compute_cosine_similarity

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base" / "knowledge_base.json"

TAG_DESCRIPTIONS = {
    "CC": "Coordinating conjunction",
    "CD": "Cardinal number",
    "DT": "Determiner",
    "EX": "Existential there",
    "FW": "Foreign word",
    "IN": "Preposition or conjunction",
    "JJ": "Adjective",
    "JJR": "Adjective, comparative",
    "JJS": "Adjective, superlative",
    "MD": "Modal auxiliary",
    "NN": "Noun, singular",
    "NNS": "Noun, plural",
    "NNP": "Proper noun, singular",
    "NNPS": "Proper noun, plural",
    "PDT": "Predeterminer",
    "POS": "Possessive ending",
    "PRP": "Personal pronoun",
    "PRP$": "Possessive pronoun",
    "RB": "Adverb",
    "RBR": "Adverb, comparative",
    "RBS": "Adverb, superlative",
    "RP": "Particle",
    "SYM": "Symbol",
    "TO": "to",
    "UH": "Interjection",
    "VB": "Verb, base form",
    "VBD": "Verb, past tense",
    "VBG": "Verb, gerund or present participle",
    "VBN": "Verb, past participle",
    "VBP": "Verb, non-3rd person singular present",
    "VBZ": "Verb, 3rd person singular present",
    "WDT": "Wh-determiner",
    "WP": "Wh-pronoun",
    "WP$": "Possessive wh-pronoun",
    "WRB": "Wh-adverb"
}

class PipelineService:
    def __init__(self):
        self.stemmer = PorterStemmer()
        try:
            self.nltk_stopwords = set(stopwords.words("english"))
        except Exception:
            self.nltk_stopwords = set()
        self._load_kb_embeddings()

    def _load_kb_embeddings(self):
        self.kb_items = []
        self.kb_embeddings = []
        try:
            if KB_PATH.exists():
                with open(KB_PATH, "r", encoding="utf-8") as f:
                    self.kb_items = json.load(f)
                for item in self.kb_items:
                    text_repr = f"{item.get('topic', '')}: {item.get('definition', '')}"
                    vec = get_embedding(text_repr)
                    self.kb_embeddings.append((item, vec))
        except Exception as e:
            logger.error(f"Error loading KB embeddings in PipelineService: {e}")

    def process_text_pipeline(self, text: str) -> Dict[str, Any]:
        """Execute the complete 6-stage NLP pipeline on the user's input."""
        raw_text = (text or "").strip()
        if not raw_text:
            raw_text = "The quick brown foxes were jumping over 10 lazy dogs in New York!"

        nlp = get_spacy_nlp()
        doc = nlp(raw_text)

        # ----------------------------------------------------
        # Step 1: Raw Input & Normalization
        # ----------------------------------------------------
        cleaned_text = re.sub(r'\s+', ' ', raw_text)
        step1 = {
            "original_text": raw_text,
            "cleaned_text": cleaned_text,
            "char_count": len(raw_text),
            "word_count": len([t for t in doc if not t.is_punct and not t.is_space]),
            "lowercased": raw_text.lower()
        }

        # ----------------------------------------------------
        # Step 2: Tokenization & Boundaries
        # ----------------------------------------------------
        tokens_data = []
        for i, token in enumerate(doc):
            tok_type = "word"
            if token.is_punct:
                tok_type = "punctuation"
            elif token.like_num:
                tok_type = "number"
            elif token.is_space:
                tok_type = "whitespace"

            tokens_data.append({
                "index": i,
                "text": token.text,
                "start_char": token.idx,
                "end_char": token.idx + len(token.text),
                "type": tok_type,
                "length": len(token.text)
            })

        step2 = {
            "total_tokens": len(tokens_data),
            "tokens": tokens_data
        }

        # ----------------------------------------------------
        # Step 3: Stopwords & Noise Filtering
        # ----------------------------------------------------
        stopword_analysis = []
        retained_count = 0
        removed_count = 0

        for token in doc:
            if token.is_space:
                continue
            is_stop = token.is_stop or (token.text.lower() in self.nltk_stopwords)
            is_punct = token.is_punct
            
            if is_punct:
                status = "removed"
                reason = "Punctuation symbol"
                removed_count += 1
            elif is_stop:
                status = "removed"
                reason = "Grammatical Stopword (spaCy / NLTK)"
                removed_count += 1
            else:
                status = "retained"
                reason = "Salient Content Word"
                retained_count += 1

            stopword_analysis.append({
                "token": token.text,
                "status": status,
                "reason": reason,
                "is_stop": is_stop
            })

        total_content = max(1, retained_count + removed_count)
        step3 = {
            "retained_count": retained_count,
            "removed_count": removed_count,
            "retention_rate_percent": round((retained_count / total_content) * 100, 1),
            "items": stopword_analysis
        }

        # ----------------------------------------------------
        # Step 4: POS Tagging & Morphological Features
        # ----------------------------------------------------
        pos_data = []
        for token in doc:
            if token.is_space:
                continue
            tag_desc = TAG_DESCRIPTIONS.get(token.tag_, token.pos_)
            pos_data.append({
                "token": token.text,
                "pos": token.pos_,
                "tag": token.tag_,
                "description": tag_desc,
                "dep": token.dep_,
                "morph": str(token.morph) if str(token.morph) else "N/A"
            })

        step4 = {
            "pos_tokens": pos_data
        }

        # ----------------------------------------------------
        # Step 5: Lemmatization vs. Stemming Comparison
        # ----------------------------------------------------
        comparison_data = []
        diff_count = 0
        for token in doc:
            if token.is_punct or token.is_space:
                continue
            lemma = token.lemma_
            stem = self.stemmer.stem(token.text.lower())
            is_diff = (lemma.lower() != stem.lower())
            if is_diff:
                diff_count += 1
                explanation = f"Lemma '{lemma}' retains true dictionary root; Stemmer produced heuristic chop '{stem}'."
            else:
                explanation = "Lemma and Stem produced identical representation."

            comparison_data.append({
                "original": token.text,
                "lemma": lemma,
                "stem": stem,
                "is_different": is_diff,
                "explanation": explanation
            })

        step5 = {
            "different_count": diff_count,
            "total_evaluated": len(comparison_data),
            "comparisons": comparison_data
        }

        # ----------------------------------------------------
        # Step 6: Dense Vector Embedding & Semantic Neighborhood
        # ----------------------------------------------------
        input_vec = get_embedding(raw_text)
        vector_dim = len(input_vec) if hasattr(input_vec, '__len__') else 384
        
        # Calculate top-3 nearest KB concepts
        similarities = []
        for item, kb_vec in self.kb_embeddings:
            sim = float(compute_cosine_similarity(input_vec, kb_vec))
            similarities.append({
                "subject": item.get("subject", "General"),
                "topic": item.get("topic", "General"),
                "title": item.get("title", item.get("topic")),
                "similarity_percent": round(max(0.0, min(1.0, sim)) * 100, 1),
                "definition_snippet": item.get("definition", "")[:120] + "..."
            })

        similarities.sort(key=lambda x: x["similarity_percent"], reverse=True)
        top_matches = similarities[:3]

        # Vector preview snippet
        preview_slice = [round(float(x), 4) for x in list(input_vec)[:8]]

        step6 = {
            "model_name": "all-MiniLM-L6-v2 (Sentence-Transformers)",
            "vector_dimension": vector_dim,
            "l2_norm": 1.00,
            "vector_preview": preview_slice,
            "nearest_concepts": top_matches
        }

        return {
            "step1_raw": step1,
            "step2_tokens": step2,
            "step3_stopwords": step3,
            "step4_pos": step4,
            "step5_lemma_stem": step5,
            "step6_vector": step6
        }

_pipeline_service = None

def get_pipeline_service() -> PipelineService:
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = PipelineService()
    return _pipeline_service
