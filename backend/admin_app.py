import os
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, jsonify, session, redirect, url_for, request, send_from_directory
from dotenv import load_dotenv
from config import Config
from backend.models.user import UserModel
from backend.routes.auth import auth_bp
from backend.routes.admin import admin_bp
from backend.routes.tutor import tutor_bp
from backend.routes.quiz import quiz_bp
from backend.routes.progress import progress_bp
from backend.routes.analytics import analytics_bp
from backend.routes.documents import documents_bp
from backend.routes.gamification import gamification_bp
from backend.routes.spaced_repetition import spaced_repetition_bp
from backend.routes.knowledge_graph import knowledge_graph_bp
from backend.routes.flashcards import flashcards_bp
from backend.routes.viva import viva_bp
from backend.routes.feynman import feynman_bp
from backend.routes.pipeline import pipeline_bp

load_dotenv()

def create_admin_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "frontend" / "templates"),
        static_folder=str(PROJECT_ROOT / "frontend" / "static"),
    )
    app.config.from_object(Config)
    # Isolate admin session cookie to prevent cross-portal collision with student app
    app.config["SESSION_COOKIE_NAME"] = "talentlens_admin_session"

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(gamification_bp)
    app.register_blueprint(spaced_repetition_bp)
    app.register_blueprint(knowledge_graph_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(viva_bp)
    app.register_blueprint(feynman_bp)
    app.register_blueprint(pipeline_bp)

    # Seed database once during startup
    with app.app_context():
        try:
            UserModel.ensure_default_admin()
            UserModel.ensure_sample_students()
        except Exception:
            pass

    @app.before_request
    def ensure_admin_session():
        # Automatically establish instructor admin session if not logged in
        if "user_id" not in session or session.get("user_role") != "admin":
            admin_user = UserModel.find_by_email("admin@gmail.com")
            if admin_user:
                session["user_id"] = admin_user["id"]
                session["user_name"] = admin_user["name"]
                session["user_email"] = admin_user["email"]
                session["user_role"] = "admin"
            else:
                session["user_id"] = "admin_root"
                session["user_name"] = "Course Instructor & Admin"
                session["user_email"] = "admin@gmail.com"
                session["user_role"] = "admin"

    @app.context_processor
    def inject_user():
        user_id = session.get("user_id", "admin_root")
        user_name = session.get("user_name", "Course Instructor")
        user_email = session.get("user_email", "admin@gmail.com")
        user_role = session.get("user_role", "admin")

        gamification_data = {
            "level": 10,
            "level_title": "Lead Instructor",
            "total_xp": 9999,
            "xp_in_level": 9999,
            "xp_needed_next": 10000,
            "level_progress_pct": 100.0,
            "streak_days": 30,
            "questions_asked": 0,
            "quizzes_completed": 0,
            "average_accuracy": 100.0,
            "earned_badges": [],
            "all_badges": [],
            "total_badges_count": 5,
            "joined_date": "Active Instructor"
        }

        return {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "gamification": gamification_data
        }

    @app.route("/", endpoint="index")
    @app.route("/admin", endpoint="admin_view")
    def admin_view():
        return render_template("admin.html")

    @app.route("/dashboard")
    def dashboard_view():
        return render_template("dashboard.html")

    @app.route("/chat")
    def chat_view():
        return render_template("chat.html")

    @app.route("/subjects")
    def subjects_view():
        return render_template("subjects.html")

    @app.route("/quiz")
    def quiz_view():
        return render_template("quiz.html")

    @app.route("/flashcards")
    def flashcards_view():
        return render_template("flashcards.html")

    @app.route("/knowledge-graph")
    def knowledge_graph_view():
        return render_template("knowledge_graph.html")

    @app.route("/documents")
    def documents_view():
        return render_template("documents.html")

    @app.route("/viva")
    def viva_view():
        return render_template("viva.html")

    @app.route("/teach-back")
    def teach_back_view():
        return render_template("teach_back.html")

    @app.route("/pipeline")
    def pipeline_view():
        return render_template("pipeline.html")

    @app.route("/favicon.ico")
    def favicon():
        return send_from_directory(
            os.path.join(app.static_folder, "images"),
            "favicon.svg",
            mimetype="image/svg+xml"
        )

    @app.errorhandler(404)
    def handle_404(e):
        return render_template(
            "error.html",
            error_code=404,
            error_title="Admin Resource Not Found",
            error_message="The requested administrative endpoint or cohort analytics resource was not found."
        ), 404

    @app.errorhandler(500)
    def handle_500(e):
        return render_template(
            "error.html",
            error_code=500,
            error_title="Instructor Portal Anomaly",
            error_message="An internal administrative processing anomaly occurred. Please try again."
        ), 500

    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "service": "TalentLens — Admin & Instructor Dashboard",
            "port": request.host.split(":")[-1] if ":" in request.host else "5001",
            "role": "Administrator / Instructor"
        })

    return app

app = create_admin_app()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TalentLens Admin Dashboard")
    parser.add_argument("--port", "-p", type=int, default=int(os.getenv("ADMIN_PORT", 5001)), help="Port to run Admin Dashboard on (default: 5001)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    args = parser.parse_args()

    print(f"==================================================")
    print(f"  TalentLens — Admin & Instructor Portal")
    print(f"  Running on: http://{args.host}:{args.port}")
    print(f"==================================================")
    app.run(host=args.host, port=args.port, debug=True)
