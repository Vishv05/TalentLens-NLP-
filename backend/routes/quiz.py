from flask import Blueprint, request, jsonify, session
from backend.services.quiz_service import get_quiz_service
from backend.services.evaluation_service import get_answer_evaluator
from backend.utils.db import get_db

quiz_bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")

@quiz_bp.route("/topics", methods=["GET"])
def get_subject_topics():
    subject = request.args.get("subject", "Natural Language Processing")
    quiz_service = get_quiz_service()
    topics = quiz_service.get_topics_for_subject(subject)
    return jsonify({"subject": subject, "topics": topics})

@quiz_bp.route("/generate", methods=["POST"])
def generate_quiz():
    data = request.get_json() or {}
    subject = data.get("subject", "Natural Language Processing")
    topic = data.get("topic", "Tokenization")
    difficulty = data.get("difficulty", "Medium")
    count = int(data.get("count", 3))

    user_id = session.get("user_id", "guest_user")
    quiz_service = get_quiz_service()
    quiz_payload = quiz_service.generate_quiz(user_id, subject, topic, difficulty, count)
    return jsonify(quiz_payload)

@quiz_bp.route("/submit", methods=["POST"])
def submit_quiz():
    data = request.get_json() or {}
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    if not quiz_id:
        return jsonify({"error": "Missing quiz_id parameter."}), 400

    user_id = session.get("user_id", "guest_user")
    evaluator = get_answer_evaluator()
    try:
        results = evaluator.evaluate_quiz_submission(user_id, quiz_id, answers)
        return jsonify(results)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Evaluation error: {str(e)}"}), 500

@quiz_bp.route("/<quiz_id>", methods=["GET"])
def get_quiz_details(quiz_id):
    db = get_db()
    quiz = db.quizzes.find_one({"quiz_id": quiz_id})
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    q_dict = dict(quiz)
    q_dict.pop("_id", None)
    return jsonify(q_dict)
