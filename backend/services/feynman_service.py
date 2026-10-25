import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from backend.nlp.embeddings import get_embedding
from backend.nlp.similarity import compute_cosine_similarity
from backend.nlp.preprocessing import analyze_text
from backend.services.gamification_service import get_gamification_engine

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base" / "knowledge_base.json"

ANALOGY_MARKERS = {
    "like", "as if", "imagine", "picture", "think of", "compare to", "similar to",
    "metaphor", "for example", "analogy", "just as", "recipe", "bucket", "lego",
    "box", "dictionary", "library", "toy", "kitchen", "chef", "traffic", "puzzle"
}

TECHNICAL_JARGON_LIST = {
    "hyperplane", "eigenvalue", "eigenvector", "backpropagation", "orthogonality",
    "stochastic", "multinomial", "convolutional", "recurrent", "loss function",
    "gradient descent", "vector space", "matrix multiplication", "tokenization",
    "lemmatization", "stemming", "regularization", "overfitting", "underfitting",
    "cosine similarity", "dimensionality", "asymptotic"
}

class FeynmanService:
    def __init__(self):
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        self.kb_items = []
        try:
            if KB_PATH.exists():
                with open(KB_PATH, "r", encoding="utf-8") as f:
                    self.kb_items = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base for Feynman Service: {e}")

    def get_available_topics(self) -> List[Dict[str, str]]:
        """Return topics suitable for the Feynman Teach-Back challenge."""
        topics = []
        for item in self.kb_items:
            topics.append({
                "id": item.get("id"),
                "subject": item.get("subject"),
                "topic": item.get("topic"),
                "title": item.get("title", item.get("topic")),
                "definition": item.get("definition", "")
            })
        return topics

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count in a single English word."""
        w = word.lower().strip()
        if not w:
            return 0
        w = re.sub(r'[^a-z]', '', w)
        if len(w) <= 3:
            return 1
        w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
        w = re.sub(r'^y', '', w)
        syllables = len(re.findall(r'[aeiouy]{1,2}', w))
        return max(1, syllables)

    def _compute_readability(self, text: str) -> Dict[str, Any]:
        """Compute Flesch Reading Ease and simplicity metrics."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        total_sentences = max(1, len(sentences))
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        total_words = max(1, len(words))

        total_syllables = sum(self._count_syllables(w) for w in words)
        words_per_sentence = total_words / total_sentences
        syllables_per_word = total_syllables / total_words

        # Flesch Reading Ease: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        flesch_score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
        flesch_score = max(0.0, min(100.0, flesch_score))

        # Convert to simplicity rating (higher flesch score = simpler to understand)
        simplicity_percent = round(flesch_score, 1)

        return {
            "total_sentences": total_sentences,
            "total_words": total_words,
            "words_per_sentence": round(words_per_sentence, 1),
            "simplicity_score": simplicity_percent,
            "reading_level": "Child-Friendly (Simple & Clear)" if flesch_score >= 70 else ("High School (Moderately Clear)" if flesch_score >= 50 else "College Academic (Complex)")
        }

    def evaluate_explanation(self, user_id: str, topic: str, student_explanation: str, audience_level: str = "child") -> Dict[str, Any]:
        """
        Evaluate student explanation using the Feynman Technique:
        1. Simplicity & Clarity (Readability)
        2. Detection of Analogies & Metaphors
        3. Jargon & Circular Definition Detection
        4. Conceptual Grounding & Semantic Accuracy
        """
        text = (student_explanation or "").strip()
        if not text or len(text.split()) < 5:
            return {
                "feynman_score": 0.0,
                "mastery_title": "Explanation Incomplete",
                "simplicity_score": 0.0,
                "analogy_score": 0.0,
                "accuracy_score": 0.0,
                "specs_dialogue": "Tweet! That was too short for Specs to understand! 🐣 Can you explain it with a story or an analogy?",
                "specs_mood": "puzzled",
                "feedback": "Please write at least 2-3 sentences explaining the concept in plain English.",
                "circularity_detected": False,
                "jargon_detected": [],
                "analogies_found": [],
                "xp_awarded": 0
            }

        # 1. Find ground-truth concept from KB
        matched_item = None
        for item in self.kb_items:
            if item.get("topic", "").lower() == topic.lower():
                matched_item = item
                break

        benchmark_text = ""
        if matched_item:
            benchmark_text = f"{matched_item.get('definition', '')} {matched_item.get('explanation', '')}"
        else:
            benchmark_text = topic

        # 2. Readability & Simplicity
        readability = self._compute_readability(text)
        simplicity_score = readability["simplicity_score"]

        # 3. Analogy & Metaphor Recognition
        text_lower = text.lower()
        found_analogies = []
        for marker in ANALOGY_MARKERS:
            if marker in text_lower:
                found_analogies.append(marker)
        
        # Analogy score: presence of at least 1-2 vivid markers
        analogy_score = min(100.0, len(found_analogies) * 45.0)

        # 4. Circular Definition & Unexplained Jargon Detection
        # Circularity: student uses the exact topic word repeatedly without explaining the root
        topic_lower = topic.lower()
        topic_tokens = topic_lower.split()
        circularity_detected = False
        
        # Count frequency of topic tokens
        topic_word_count = sum(text_lower.count(tok) for tok in topic_tokens if len(tok) > 3)
        if topic_word_count >= 3 and readability["total_words"] < 35:
            # High density of topic name in very short text -> circular definition
            circularity_detected = True

        # Check for ungrounded technical jargon
        found_jargon = []
        for j in TECHNICAL_JARGON_LIST:
            if j in text_lower and j not in topic_lower:
                found_jargon.append(j)

        # 5. Conceptual Accuracy (Dense Embedding Cosine Similarity)
        stu_vec = get_embedding(text)
        kb_vec = get_embedding(benchmark_text)
        sim = float(compute_cosine_similarity(stu_vec, kb_vec))
        sim = max(0.0, min(1.0, sim))
        accuracy_score = round(sim * 100.0, 1)

        # 6. Composite Feynman Score Calculation
        # Simplicity (35%) + Accuracy (35%) + Analogy (30%) - Circularity Penalty
        composite = (simplicity_score * 0.35) + (accuracy_score * 0.35) + (analogy_score * 0.30)
        
        if circularity_detected:
            composite = max(0.0, composite - 25.0)
        if len(found_jargon) >= 3:
            composite = max(0.0, composite - 15.0)

        feynman_score = round(composite, 1)

        # 7. Mastery Level & Specs Avatar Reaction
        if feynman_score >= 80.0:
            mastery_title = "Feynman Master Mentor"
            specs_mood = "celebrating"
            specs_dialogue = f"🎉 WOW! Specs understands completely! Your explanation of {topic} made it super simple! But wait... Specs has one curious question: What happens if we do this backwards or with giant amounts of data?"
            xp_awarded = 40
        elif feynman_score >= 65.0:
            mastery_title = "Intuitive Explainer"
            specs_mood = "curious"
            specs_dialogue = f"💡 Ah! Specs is starting to see the picture! But can you add an everyday comparison (like pizza, toys, or school lockers) to make it even more fun?"
            xp_awarded = 25
        elif feynman_score >= 45.0:
            mastery_title = "Technical Translator"
            specs_mood = "thinking"
            specs_dialogue = f"🤔 Specs is following along, but some of those words felt a bit like a college textbook! Try swapping the complex words for simpler ones!"
            xp_awarded = 15
        else:
            mastery_title = "Novice Apprentice"
            specs_mood = "puzzled"
            specs_dialogue = f"🐣 Chirp! Specs got tangled up! Remember the golden rule of Feynman: If a 10-year-old wouldn't get it on the playground, make it simpler!"
            xp_awarded = 5

        # 8. Award Gamification XP
        if user_id and xp_awarded > 0:
            try:
                engine = get_gamification_engine()
                engine.award_xp(user_id, xp_awarded, f"Feynman Teach-Back: {topic}")
            except Exception as e:
                logger.warning(f"Failed to award gamification XP in Feynman: {e}")

        return {
            "feynman_score": feynman_score,
            "mastery_title": mastery_title,
            "simplicity_score": simplicity_score,
            "analogy_score": analogy_score,
            "accuracy_score": accuracy_score,
            "specs_dialogue": specs_dialogue,
            "specs_mood": specs_mood,
            "circularity_detected": circularity_detected,
            "jargon_detected": found_jargon,
            "analogies_found": found_analogies,
            "readability_details": readability,
            "xp_awarded": xp_awarded
        }

_feynman_service = None

def get_feynman_service() -> FeynmanService:
    global _feynman_service
    if _feynman_service is None:
        _feynman_service = FeynmanService()
    return _feynman_service
