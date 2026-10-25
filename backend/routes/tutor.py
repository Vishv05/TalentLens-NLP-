from flask import Blueprint, request, jsonify, session
from backend.services.tutor_service import get_tutor_service
from backend.nlp.preprocessing import analyze_text
from backend.nlp.intent_classifier import detect_intent
from backend.nlp.topic_classifier import detect_topic
from backend.services.knowledge_service import get_knowledge_service
from backend.utils.db import get_db

tutor_bp = Blueprint("tutor", __name__, url_prefix="/api/tutor")

@tutor_bp.route("/ask", methods=["POST"])
def ask_tutor():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "Question parameter cannot be empty."}), 400

    user_id = session.get("user_id", "guest_user")
    conversation_id = data.get("conversation_id", "default_session")

    tutor_service = get_tutor_service()
    response_payload = tutor_service.process_student_question(user_id, question, conversation_id)
    return jsonify(response_payload)

@tutor_bp.route("/nlp-analysis", methods=["POST"])
def nlp_analysis_demo():
    """Standalone endpoint for live Academic NLP Panel presentation."""
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Text parameter cannot be empty."}), 400

    analysis = analyze_text(text)
    intent = detect_intent(text)
    topic = detect_topic(text)
    kb_service = get_knowledge_service()
    search_res = kb_service.search(text, top_k=1)
    retrieved = search_res[0] if search_res else None

    return jsonify({
        "raw_text": text,
        "tokens": analysis.get("tokens", []),
        "lemmas": analysis.get("lemmas", []),
        "pos_tags": analysis.get("pos_tags", []),
        "entities": analysis.get("entities", []),
        "stopwords": analysis.get("stopwords", []),
        "intent": intent.get("intent"),
        "intent_confidence": intent.get("confidence"),
        "subject": topic.get("subject"),
        "topic": topic.get("topic"),
        "similarity_score": retrieved.get("similarity_score", 0.0) if retrieved else 0.0,
        "retrieved_concept": retrieved.get("title") if retrieved else None
    })

@tutor_bp.route("/history", methods=["GET"])
def conversation_history():
    user_id = session.get("user_id", "guest_user")
    db = get_db()
    convs = db.conversations.find({"user_id": user_id})
    history = []
    for c in convs:
        c_dict = dict(c)
        c_dict["id"] = str(c_dict.get("_id", ""))
        c_dict.pop("_id", None)
        history.append(c_dict)
    return jsonify({"history": history})
