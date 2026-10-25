from flask import Blueprint, request, jsonify, session
from backend.services.viva_service import get_viva_service

viva_bp = Blueprint("viva", __name__, url_prefix="/api/viva")

@viva_bp.route("/topics", methods=["GET"])
def get_topics():
    service = get_viva_service()
    topics = service.get_available_topics()
    return jsonify({"topics": topics})

@viva_bp.route("/question", methods=["POST"])
def get_question():
    data = request.get_json() or {}
    subject = data.get("subject")
    topic = data.get("topic")
    difficulty = data.get("difficulty", "Medium")

    service = get_viva_service()
    question_payload = service.generate_viva_question(subject=subject, topic=topic, difficulty=difficulty)
    return jsonify(question_payload)

@viva_bp.route("/evaluate", methods=["POST"])
def evaluate_defense():
    data = request.get_json() or {}
    topic = data.get("topic", "General")
    question = data.get("question", "")
    student_answer = data.get("student_answer", "")
    expected_keywords = data.get("expected_keywords", [])

    user_id = session.get("user_id")

    service = get_viva_service()
    eval_result = service.evaluate_viva_defense(
        user_id=user_id,
        topic=topic,
        question=question,
        student_answer=student_answer,
        expected_keywords=expected_keywords
    )
    return jsonify(eval_result)
