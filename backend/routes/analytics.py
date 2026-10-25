from flask import Blueprint, jsonify, session
from backend.services.recommendation_service import get_recommendation_engine

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/dashboard", methods=["GET"])
def dashboard_analytics():
    user_id = session.get("user_id", "guest_user")
    engine = get_recommendation_engine()
    data = engine.get_user_learning_analytics(user_id)

    # Chart.js friendly formatting
    topics = [t["topic"] for t in data["topic_stats"]] or ["Tokenization", "Lemmatization", "TF-IDF", "Overfitting"]
    accuracies = [t["accuracy"] for t in data["topic_stats"]] or [92.0, 85.0, 78.0, 58.0]

    subject_labels = [s["subject"] for s in data.get("subject_stats", [])] or [
        "Natural Language Processing", "Machine Learning", "Database Management Systems", "Python Programming"
    ]
    subject_accuracies = [s["accuracy"] for s in data.get("subject_stats", [])] or [88.0, 72.0, 80.0, 90.0]

    return jsonify({
        "metrics": {
            "questions_asked": data["total_questions_asked"],
            "quizzes_attempted": data["total_quizzes_attempted"],
            "average_quiz_score": data["average_quiz_score"],
            "overall_accuracy": data["overall_accuracy"],
            "suggested_difficulty": data["suggested_difficulty"]
        },
        "charts": {
            "topic_labels": topics,
            "topic_accuracies": accuracies,
            "subject_labels": subject_labels,
            "subject_accuracies": subject_accuracies,
            "strong_count": len(data["strong_topics"]),
            "weak_count": len(data["weak_topics"])
        },
        "recommendations": data["recommendations"],
        "recent_quizzes": data.get("recent_quizzes", [])
    })
