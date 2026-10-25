from flask import Blueprint, jsonify, session
from backend.services.recommendation_service import get_recommendation_engine
from backend.utils.db import get_db

progress_bp = Blueprint("progress", __name__, url_prefix="/api/progress")

@progress_bp.route("/summary", methods=["GET"])
def get_progress_summary():
    user_id = session.get("user_id", "guest_user")
    rec_engine = get_recommendation_engine()
    analytics = rec_engine.get_user_learning_analytics(user_id)
    return jsonify(analytics)

@progress_bp.route("/reset", methods=["POST"])
def reset_progress():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Authentication required to reset progress"}), 401
    
    db = get_db()
    try:
        # Delete quiz attempts for this user
        db.quiz_attempts.delete_many({"user_id": user_id})

        # Delete conversation history for fresh chat
        db.conversations.delete_many({"user_id": user_id})

        # Reset user gamification profile
        db.users.update_one(
            {"id": user_id},
            {"$set": {
                "xp": 0,
                "level": 1,
                "streak_days": 1,
                "badges": [],
                "questions_asked": 0
            }}
        )

        return jsonify({
            "success": True,
            "message": "Academic progress, quiz attempts, and study history have been reset successfully for demo presentation."
        })
    except Exception as e:
        return jsonify({"error": f"Failed to reset progress: {str(e)}"}), 500
