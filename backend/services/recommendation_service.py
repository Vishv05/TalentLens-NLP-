from typing import Dict, Any, List
from backend.utils.db import get_db

class RecommendationEngine:
    def get_user_learning_analytics(self, user_id: str) -> Dict[str, Any]:
        db = get_db()

        # Fetch progress records
        progress_docs = list(db.learning_progress.find({"user_id": user_id}))
        conv_count = len(list(db.conversations.find({"user_id": user_id})))
        quiz_docs = list(db.quizzes.find({"user_id": user_id}))

        total_questions_attempted = sum(p.get("questions_attempted", 0) for p in progress_docs)
        total_correct = sum(p.get("correct_answers", 0) for p in progress_docs)
        overall_accuracy = round((total_correct / total_questions_attempted * 100), 2) if total_questions_attempted > 0 else 0.0

        quiz_scores = [q.get("score", 0.0) for q in quiz_docs if "score" in q]
        avg_quiz_score = round(sum(quiz_scores) / len(quiz_scores), 2) if quiz_scores else 0.0

        # Recent Quizzes (sorted most recent first)
        recent_quizzes = []
        for q in reversed(quiz_docs[-6:]):
            recent_quizzes.append({
                "quiz_id": q.get("quiz_id"),
                "subject": q.get("subject", "General"),
                "topic": q.get("topic", "General"),
                "difficulty": q.get("difficulty", "Medium"),
                "score": q.get("score", 0.0),
                "timestamp": str(q.get("timestamp", ""))[:19]
            })

        weak_topics = []
        strong_topics = []
        topic_stats = []
        subject_buckets: Dict[str, List[float]] = {}

        for p in progress_docs:
            acc = p.get("accuracy", 0.0)
            topic = p.get("topic", "General")
            subject = p.get("subject", "General")

            topic_stats.append({
                "subject": subject,
                "topic": topic,
                "accuracy": acc,
                "attempted": p.get("questions_attempted", 0)
            })

            if subject not in subject_buckets:
                subject_buckets[subject] = []
            subject_buckets[subject].append(acc)

            if acc < 65.0:
                weak_topics.append(topic)
            elif acc >= 80.0:
                strong_topics.append(topic)

        # Compute Subject Averages
        subject_stats = []
        for subj, acc_list in subject_buckets.items():
            subject_stats.append({
                "subject": subj,
                "accuracy": round(sum(acc_list) / len(acc_list), 2)
            })

        recommendations = []
        if weak_topics:
            for w in weak_topics:
                recommendations.append({
                    "topic": w,
                    "reason": f"Your accuracy in {w} is below 65%. We recommend reviewing concepts and taking a practice quiz.",
                    "action": f"Revise {w}"
                })
        else:
            recommendations.append({
                "topic": "Transformers & Attention Mechanism",
                "reason": "You've demonstrated solid accuracy across foundational topics! Challenge yourself with advanced Transformer architectures.",
                "action": "Start Advanced Topics"
            })

        # Adaptive Difficulty Logic
        if overall_accuracy >= 85.0:
            suggested_difficulty = "Hard"
        elif overall_accuracy >= 65.0:
            suggested_difficulty = "Medium"
        else:
            suggested_difficulty = "Easy"

        return {
            "total_questions_asked": conv_count,
            "total_quizzes_attempted": len(quiz_docs),
            "average_quiz_score": avg_quiz_score,
            "overall_accuracy": overall_accuracy,
            "strong_topics": strong_topics if strong_topics else ["Tokenization"],
            "weak_topics": weak_topics if weak_topics else [],
            "recommendations": recommendations,
            "suggested_difficulty": suggested_difficulty,
            "topic_stats": topic_stats,
            "subject_stats": subject_stats,
            "recent_quizzes": recent_quizzes
        }

_recommendation_engine = RecommendationEngine()

def get_recommendation_engine():
    return _recommendation_engine
