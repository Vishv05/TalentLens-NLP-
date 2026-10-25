from flask import Blueprint, jsonify, session
from backend.services.gamification_service import get_gamification_engine

gamification_bp = Blueprint("gamification", __name__, url_prefix="/api/gamification")

@gamification_bp.route("/profile", methods=["GET"])
@gamification_bp.route("/status", methods=["GET"])
def get_gamification_profile():
    user_id = session.get("user_id", "guest_user")
    engine = get_gamification_engine()
    profile = engine.get_user_gamification_profile(user_id)
    profile["status"] = "success"
    return jsonify(profile)
