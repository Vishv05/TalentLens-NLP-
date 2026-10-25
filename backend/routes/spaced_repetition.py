from flask import Blueprint, request, jsonify, session
from backend.services.spaced_repetition_service import get_spaced_repetition_engine

spaced_repetition_bp = Blueprint("spaced_repetition", __name__, url_prefix="/api/spaced-repetition")

@spaced_repetition_bp.route("/due", methods=["GET"])
def get_due_topics():
    user_id = session.get("user_id", "guest_user")
    engine = get_spaced_repetition_engine()
    due_topics = engine.get_due_reviews(user_id)
    return jsonify({"due_topics": due_topics, "total_due": len(due_topics)})

@spaced_repetition_bp.route("/record", methods=["POST"])
def record_review():
    data = request.get_json() or {}
    topic = data.get("topic")
    score_percent = float(data.get("score_percent", 70.0))

    if not topic:
        return jsonify({"error": "Missing topic parameter."}), 400

    user_id = session.get("user_id", "guest_user")
    engine = get_spaced_repetition_engine()
    res = engine.record_topic_review(user_id, topic, score_percent)
    return jsonify(res)

@spaced_repetition_bp.route("/flashcard-rate", methods=["POST"])
def rate_flashcard():
    data = request.get_json() or {}
    topic = data.get("topic")
    rating = data.get("rating", "good").lower()  # easy | good | hard | forgot

    rating_to_score = {
        "easy": 100.0,
        "good": 85.0,
        "hard": 60.0,
        "forgot": 20.0
    }
    score = rating_to_score.get(rating, 80.0)

    if not topic:
        return jsonify({"error": "Missing topic parameter."}), 400

    user_id = session.get("user_id", "guest_user")
    engine = get_spaced_repetition_engine()
    res = engine.record_topic_review(user_id, topic, score)
    return jsonify({"message": f"Recorded {rating} review for {topic}", "sm2": res})
