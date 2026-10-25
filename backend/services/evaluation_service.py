from datetime import datetime, timezone
from typing import Dict, Any, List
from backend.nlp.embeddings import get_embedding
from backend.nlp.similarity import compute_cosine_similarity, compute_keyword_coverage
from backend.services.spaced_repetition_service import get_spaced_repetition_engine
from backend.utils.db import get_db

class AnswerEvaluator:
    def evaluate_short_answer(self, expected_answer: str, student_answer: str) -> Dict[str, Any]:
        if not student_answer or not student_answer.strip():
            return {
                "score_percent": 0.0,
                "status": "Incorrect",
                "semantic_similarity": 0.0,
                "keyword_coverage": 0.0,
                "feedback": "No answer provided.",
                "is_correct": False
            }

        # 1. Dense Semantic Similarity
        exp_vec = get_embedding(expected_answer)
        stu_vec = get_embedding(student_answer)
        semantic_sim = compute_cosine_similarity(exp_vec, stu_vec)

        # 2. Lemmatized Keyword Coverage
        kw_cov = compute_keyword_coverage(expected_answer, student_answer)

        # 3. Combined Score (Dynamic weights and thresholds from Admin Rubric Studio)
        try:
            from backend.services.admin_service import get_grading_config
            cfg = get_grading_config()
            sem_w = float(cfg.get("semantic_weight", 0.60))
            kw_w = float(cfg.get("keyword_weight", 0.40))
            dist_thresh = float(cfg.get("distinction_threshold", 80.0))
            pass_thresh = float(cfg.get("pass_threshold", 55.0))
        except Exception:
            sem_w, kw_w = 0.60, 0.40
            dist_thresh, pass_thresh = 80.0, 55.0

        combined_score = (semantic_sim * sem_w) + (kw_cov * kw_w)
        final_score_percent = round(combined_score * 100, 2)

        if final_score_percent >= dist_thresh:
            status = "Correct"
            is_correct = True
            feedback = "Excellent! Your answer demonstrates a strong semantic understanding of the concept."
        elif final_score_percent >= pass_thresh:
            status = "Partially Correct"
            is_correct = True
            feedback = f"Partially correct ({final_score_percent}%). You captured core elements, but ensure you include key terminology."
        else:
            status = "Incorrect"
            is_correct = False
            feedback = f"Incorrect ({final_score_percent}%). Consider reviewing the definition and key points."

        return {
            "score_percent": final_score_percent,
            "status": status,
            "semantic_similarity": round(semantic_sim * 100, 2),
            "keyword_coverage": round(kw_cov * 100, 2),
            "feedback": feedback,
            "is_correct": is_correct
        }

    def evaluate_quiz_submission(self, user_id: str, quiz_id: str, submitted_answers: Dict[str, str]) -> Dict[str, Any]:
        db = get_db()
        quiz = db.quizzes.find_one({"quiz_id": quiz_id})
        if not quiz:
            raise ValueError(f"Quiz ID '{quiz_id}' not found.")

        questions = quiz.get("questions", [])
        total_questions = len(questions)
        if total_questions == 0:
            return {"score": 0, "total": 0, "evaluations": []}

        question_evaluations = []
        earned_scores = []

        for q in questions:
            q_id = q["id"]
            q_type = q.get("type", "mcq")
            expected = q["correct_answer"]
            user_ans = submitted_answers.get(q_id, "").strip()

            if q_type in ["mcq", "true_false"]:
                is_correct = (user_ans.lower() == expected.lower())
                score = 100.0 if is_correct else 0.0
                eval_item = {
                    "question_id": q_id,
                    "question": q["question"],
                    "type": q_type,
                    "student_answer": user_ans,
                    "correct_answer": expected,
                    "is_correct": is_correct,
                    "score_percent": score,
                    "feedback": "Correct!" if is_correct else f"Incorrect. Correct answer: {expected}"
                }
            else: # short answer
                eval_res = self.evaluate_short_answer(expected, user_ans)
                score = eval_res["score_percent"]
                is_correct = eval_res["is_correct"]
                eval_item = {
                    "question_id": q_id,
                    "question": q["question"],
                    "type": q_type,
                    "student_answer": user_ans,
                    "correct_answer": expected,
                    "is_correct": is_correct,
                    "score_percent": score,
                    "semantic_similarity": eval_res["semantic_similarity"],
                    "keyword_coverage": eval_res["keyword_coverage"],
                    "feedback": eval_res["feedback"]
                }

            earned_scores.append(score)
            question_evaluations.append(eval_item)

        avg_score = round(sum(earned_scores) / total_questions, 2)

        # Update Quiz Record in Database
        db.quizzes.update_one(
            {"quiz_id": quiz_id},
            {"$set": {"user_answers": question_evaluations, "score": avg_score, "evaluated_at": datetime.now(timezone.utc)}}
        )

        # Update Student Learning Progress Record
        topic = quiz.get("topic", "General")
        subject = quiz.get("subject", "General")
        self._update_learning_progress(user_id, subject, topic, avg_score, question_evaluations)

        # Automatically update SuperMemo-2 (SM-2) Spaced Repetition engine
        try:
            sr_engine = get_spaced_repetition_engine()
            sr_engine.record_topic_review(user_id, topic, avg_score)
        except Exception:
            pass

        return {
            "quiz_id": quiz_id,
            "subject": subject,
            "topic": topic,
            "overall_score_percent": avg_score,
            "total_questions": total_questions,
            "evaluations": question_evaluations
        }

    def _update_learning_progress(self, user_id: str, subject: str, topic: str, avg_score: float, evals: List[Dict[str, Any]]):
        db = get_db()
        existing = db.learning_progress.find_one({"user_id": user_id, "topic": topic})

        correct_cnt = sum(1 for e in evals if e.get("is_correct"))
        incorrect_cnt = len(evals) - correct_cnt

        if existing:
            new_attempted = existing.get("questions_attempted", 0) + len(evals)
            new_correct = existing.get("correct_answers", 0) + correct_cnt
            new_incorrect = existing.get("incorrect_answers", 0) + incorrect_cnt
            new_accuracy = round((new_correct / new_attempted) * 100, 2)

            db.learning_progress.update_one(
                {"_id": existing["_id"]},
                {"$set": {
                    "questions_attempted": new_attempted,
                    "correct_answers": new_correct,
                    "incorrect_answers": new_incorrect,
                    "accuracy": new_accuracy,
                    "last_updated": datetime.now(timezone.utc)
                }}
            )
        else:
            db.learning_progress.insert_one({
                "user_id": user_id,
                "subject": subject or "General",
                "topic": topic or "General",
                "questions_attempted": len(evals),
                "correct_answers": correct_cnt,
                "incorrect_answers": incorrect_cnt,
                "accuracy": round((correct_cnt / max(len(evals), 1)) * 100, 2),
                "difficulty_level": "Medium",
                "last_updated": datetime.now(timezone.utc)
            })

_evaluator = AnswerEvaluator()

def get_answer_evaluator():
    return _evaluator
