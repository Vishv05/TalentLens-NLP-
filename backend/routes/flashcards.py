from flask import Blueprint, request, jsonify
from backend.services.flashcard_service import get_flashcard_service

flashcards_bp = Blueprint("flashcards", __name__, url_prefix="/api/flashcards")

@flashcards_bp.route("/list", methods=["GET"])
def get_flashcards():
    subject = request.args.get("subject", "All")
    service = get_flashcard_service()
    cards = service.generate_flashcards(subject)
    return jsonify({"flashcards": cards, "total": len(cards)})
