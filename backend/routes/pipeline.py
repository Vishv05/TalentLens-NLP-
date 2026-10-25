from flask import Blueprint, request, jsonify
from backend.services.pipeline_service import get_pipeline_service

pipeline_bp = Blueprint("pipeline", __name__, url_prefix="/api/pipeline")

@pipeline_bp.route("/process", methods=["POST"])
def process_pipeline():
    data = request.get_json() or {}
    text = data.get("text", "")

    service = get_pipeline_service()
    result = service.process_text_pipeline(text)
    return jsonify(result)
