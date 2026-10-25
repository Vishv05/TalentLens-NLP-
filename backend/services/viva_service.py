import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np

from backend.nlp.embeddings import get_embedding
from backend.nlp.similarity import compute_cosine_similarity
from backend.nlp.preprocessing import analyze_text
from backend.services.gamification_service import get_gamification_engine
from backend.services.llm_service import LLMService

logger = logging.getLogger(__name__)

KB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base" / "knowledge_base.json"

class VivaService:
    def __init__(self):
        self.llm = LLMService()
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        self.kb_items = []
        try:
            if KB_PATH.exists():
                with open(KB_PATH, "r", encoding="utf-8") as f:
                    self.kb_items = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge base for Viva Service: {e}")

    def get_available_topics(self) -> List[Dict[str, str]]:
        """Return distinct subjects and topics available for viva defense."""
        topics = []
        seen = set()
        for item in self.kb_items:
            key = (item.get("subject"), item.get("topic"))
            if key not in seen:
                seen.add(key)
                topics.append({
                    "subject": item.get("subject", "General"),
                    "topic": item.get("topic", "General"),
                    "title": item.get("title", item.get("topic", ""))
                })
        return topics

    def generate_viva_question(self, subject: Optional[str] = None, topic: Optional[str] = None, difficulty: str = "Medium") -> Dict[str, Any]:
        """Generate a realistic, challenging university viva / oral defense question."""
        matched_item = None
        for item in self.kb_items:
            if topic and item.get("topic", "").lower() == topic.lower():
                matched_item = item
                break
            elif subject and item.get("subject", "").lower() == subject.lower():
                matched_item = item
                break

        if not matched_item and self.kb_items:
            matched_item = self.kb_items[0]

        target_topic = matched_item.get("topic", "Natural Language Processing")
        target_subject = matched_item.get("subject", "Computer Science")
        definition = matched_item.get("definition", "")
        explanation = matched_item.get("explanation", "")
        keywords = matched_item.get("keywords", [])

        # Curated oral defense question patterns tailored to academic vivas
        if difficulty == "Hard":
            questions = [
                f"Defend the architectural intuition behind {target_topic}. Under what specific edge cases or data distributions does this technique fail, and what mathematical/algorithmic trade-offs must you accept?",
                f"In an oral defense, explain how {target_topic} interacts with downstream machine learning pipelines. What are the computational complexity bottlenecks and how do you mitigate them?",
                f"Critique {target_topic} from first principles. How does it resolve the fundamental limitations of prior naive approaches, and what are its key hyperparameter sensitivities?"
            ]
        elif difficulty == "Easy":
            questions = [
                f"Define {target_topic} clearly from first principles. What core problem does it solve in {target_subject}, and what is a concrete real-world example of its use?",
                f"Explain the primary objective of {target_topic}. What are the primary input requirements and what output does it produce?",
                f"Can you provide a clear conceptual overview of {target_topic} and identify its two most critical advantages?"
            ]
        else: # Medium
            questions = [
                f"Explain how {target_topic} operates step-by-step. What are the key algorithmic components, and how does it maintain semantic and computational integrity?",
                f"Compare {target_topic} with traditional alternative techniques. Why is it preferred in modern systems, and what key assumptions does it rely upon?",
                f"Walk me through the theoretical mechanics of {target_topic}. Which specific parameters dictate its performance in practice?"
            ]

        import random
        selected_q = random.choice(questions)

        return {
            "question_id": f"viva_{matched_item.get('id', 'gen')}_{difficulty.lower()}",
            "subject": target_subject,
            "topic": target_topic,
            "difficulty": difficulty,
            "question": selected_q,
            "expected_keywords": keywords,
            "benchmark_definition": definition,
            "benchmark_explanation": explanation,
            "rubric_hint": f"Your response will be evaluated on semantic vector similarity, precision in technical terminology, and architectural depth."
        }

    def evaluate_viva_defense(self, user_id: str, topic: str, question: str, student_answer: str, expected_keywords: List[str]) -> Dict[str, Any]:
        """Comprehensive NLP evaluation of student's spoken/written viva defense."""
        ans = (student_answer or "").strip()
        if not ans:
            return {
                "score_percent": 0.0,
                "verdict": "Defense Not Attempted",
                "verdict_badge": "danger",
                "semantic_similarity": 0.0,
                "keyword_coverage_percent": 0.0,
                "mentioned_keywords": [],
                "missed_keywords": expected_keywords,
                "feedback": "You did not submit an oral or written response. Please state your answer clearly.",
                "followup_probe": "Could you at least define the primary function of this topic?",
                "xp_awarded": 0
            }

        # 1. Linguistic Parsing via NLP Pipeline
        nlp_res = analyze_text(ans)
        student_tokens_lower = [t.lower() for t in nlp_res.get("tokens", [])]
        student_lemmas_lower = [l.lower() for l in nlp_res.get("lemmas", [])]
        student_text_lower = ans.lower()

        # 2. Benchmark Retrieval
        matched_item = None
        for item in self.kb_items:
            if item.get("topic", "").lower() == topic.lower():
                matched_item = item
                break

        benchmark_text = ""
        if matched_item:
            benchmark_text = f"{matched_item.get('definition', '')} {matched_item.get('explanation', '')}"
            if not expected_keywords:
                expected_keywords = matched_item.get("keywords", [])
        else:
            benchmark_text = question

        # 3. Dense Vector Semantic Similarity
        student_vec = get_embedding(ans)
        benchmark_vec = get_embedding(benchmark_text)
        semantic_sim = float(compute_cosine_similarity(student_vec, benchmark_vec))
        semantic_sim = max(0.0, min(1.0, semantic_sim))

        # 4. Technical Keyword Coverage
        mentioned_kw = []
        missed_kw = []
        for kw in expected_keywords:
            kw_clean = kw.lower().strip()
            # Check direct substring or lemma match
            if kw_clean in student_text_lower or any(kw_clean in tok for tok in student_tokens_lower) or any(kw_clean in lem for lem in student_lemmas_lower):
                mentioned_kw.append(kw)
            else:
                missed_kw.append(kw)

        kw_cov = (len(mentioned_kw) / len(expected_keywords)) if expected_keywords else 1.0
        kw_cov = max(0.0, min(1.0, kw_cov))

        # 5. Technical Depth & Elaboration (Sentence length, argumentation markers)
        word_count = nlp_res.get("word_count", 0)
        depth_score = min(1.0, word_count / 40.0) # ideal answer has at least 35-40 words of technical defense
        
        # Connective reasoning words
        reasoning_markers = ["because", "therefore", "due to", "whereas", "in contrast", "specifically", "computationally", "trade-off", "optimizes", "complexity"]
        has_reasoning = any(m in student_text_lower for m in reasoning_markers)
        if has_reasoning:
            depth_score = min(1.0, depth_score + 0.15)

        # 6. Composite Viva Score
        composite = (semantic_sim * 0.45) + (kw_cov * 0.35) + (depth_score * 0.20)
        final_score = round(composite * 100, 1)

        # 7. Examiner Verdict
        if final_score >= 82.0:
            verdict = "Distinction Defense (Outstanding Technical Mastery)"
            verdict_badge = "success"
            feedback = "Superb oral defense! You articulated the theoretical principles with strong technical vocabulary and sound conceptual clarity."
            xp_awarded = 45
        elif final_score >= 68.0:
            verdict = "Passed Defense (Sound Conceptual Foundation)"
            verdict_badge = "primary"
            feedback = "Solid defense. You understand the foundational mechanisms, but make sure to emphasize the missing technical nuances identified below."
            xp_awarded = 30
        elif final_score >= 50.0:
            verdict = "Conditional Pass (Surface Level — Lacks Technical Rigor)"
            verdict_badge = "warning"
            feedback = "Borderline defense. Your response captures high-level intuition, but lacks rigorous technical keywords and architectural depth."
            xp_awarded = 15
        else:
            verdict = "Defense Rejected (Major Conceptual Gaps)"
            verdict_badge = "danger"
            feedback = "The examiner identified substantial conceptual gaps. Review the formal definition and fundamental mechanics before re-attempting."
            xp_awarded = 5

        # 8. Socratic Follow-Up Challenge Probe
        followup_probe = self._generate_socratic_probe(topic, ans, missed_kw, final_score)

        # 9. Award Gamification XP if user_id is provided
        if user_id and xp_awarded > 0:
            try:
                engine = get_gamification_engine()
                engine.award_xp(user_id, xp_awarded, f"Completed Viva Defense on {topic}")
            except Exception as e:
                logger.warning(f"Failed to award gamification XP in viva: {e}")

        return {
            "score_percent": final_score,
            "verdict": verdict,
            "verdict_badge": verdict_badge,
            "semantic_similarity": round(semantic_sim * 100, 1),
            "keyword_coverage_percent": round(kw_cov * 100, 1),
            "depth_score_percent": round(depth_score * 100, 1),
            "word_count": word_count,
            "mentioned_keywords": mentioned_kw,
            "missed_keywords": missed_kw,
            "feedback": feedback,
            "followup_probe": followup_probe,
            "xp_awarded": xp_awarded
        }

    def _generate_socratic_probe(self, topic: str, student_answer: str, missed_keywords: List[str], score: float) -> str:
        """Dynamically formulate a follow-up challenge question probing the student's exact defense."""
        if missed_keywords:
            sample_missed = ", ".join(f"'{k}'" for k in missed_keywords[:2])
            return f"Interesting point. However, in your defense you did not account for {sample_missed}. How would the behavior of {topic} change if those constraints are violated?"
        
        if score >= 80:
            return f"Excellent. Now take it one level deeper: If you were optimizing {topic} in an ultra-low-latency production environment, what engineering bottleneck would you tackle first?"
        else:
            return f"Could you provide a concrete mathematical or practical edge-case scenario where {topic} fails or yields suboptimal performance?"

_viva_service = None

def get_viva_service() -> VivaService:
    global _viva_service
    if _viva_service is None:
        _viva_service = VivaService()
    return _viva_service
