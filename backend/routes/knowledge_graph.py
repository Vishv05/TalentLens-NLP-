from flask import Blueprint, jsonify
from backend.services.knowledge_graph_service import get_knowledge_graph_engine

knowledge_graph_bp = Blueprint("knowledge_graph", __name__, url_prefix="/api/knowledge-graph")

@knowledge_graph_bp.route("/topology", methods=["GET"])
def get_graph_topology():
    engine = get_knowledge_graph_engine()
    topology = engine.get_knowledge_graph_topology()
    return jsonify(topology)
