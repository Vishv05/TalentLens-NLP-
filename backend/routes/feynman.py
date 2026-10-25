from flask import Blueprint, request, jsonify, session
from backend.services.feynman_service import get_feynman_service

feynman_bp = Blueprint("feynman", __name__, url_prefix="/api/feynman")

@feynman_bp.route("/topics", methods=["GET"])
def get_topics():
    service = get_feynman_service()
    topics = service.get_available_topics()
    return jsonify({"topics": topics})

@feynman_bp.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json() or {}
    topic = data.get("topic", "")
    explanation = data.get("explanation", "")
    audience_level = data.get("audience_level", "child")

    user_id = session.get("user_id")

    service = get_feynman_service()
    eval_result = service.evaluate_explanation(
        user_id=user_id,
        topic=topic,
        student_explanation=explanation,
        audience_level=audience_level
    )
    return jsonify(eval_result)
