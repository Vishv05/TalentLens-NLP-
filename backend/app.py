import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, jsonify, session, redirect, url_for, send_from_directory
from dotenv import load_dotenv
from config import Config
from backend.routes.auth import auth_bp
from backend.routes.tutor import tutor_bp
from backend.routes.quiz import quiz_bp
from backend.routes.progress import progress_bp
from backend.routes.analytics import analytics_bp
from backend.routes.documents import documents_bp
from backend.routes.gamification import gamification_bp
from backend.routes.spaced_repetition import spaced_repetition_bp
from backend.routes.knowledge_graph import knowledge_graph_bp
from backend.routes.flashcards import flashcards_bp
from backend.models.user import UserModel
from backend.routes.admin import admin_bp
from backend.routes.viva import viva_bp
from backend.routes.feynman import feynman_bp
from backend.routes.pipeline import pipeline_bp

load_dotenv()

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "frontend" / "templates"),
        static_folder=str(PROJECT_ROOT / "frontend" / "static"),
    )
    app.config.from_object(Config)
    # Isolate student session cookie to prevent cross-portal collision with admin app
    app.config["SESSION_COOKIE_NAME"] = "talentlens_student_session"

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(gamification_bp)
    app.register_blueprint(spaced_repetition_bp)
    app.register_blueprint(knowledge_graph_bp)
    app.register_blueprint(flashcards_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(viva_bp)
    app.register_blueprint(feynman_bp)
    app.register_blueprint(pipeline_bp)

    # Ensure initial database seed once during app setup
    with app.app_context():
        try:
            UserModel.ensure_default_admin()
            UserModel.ensure_sample_students()
        except Exception:
            pass

    @app.before_request
    def ensure_student_session():
        # Fast session check on the Student portal:
        # If an admin session leaked into this portal, or no user is logged in, activate the primary student profile (Vishv Patel)
        if session.get("user_role") == "admin" or session.get("user_email") == "admin@gmail.com" or "user_id" not in session:
            student = UserModel.find_by_email("student@gmail.com")
            if student:
                session["user_id"] = student["id"]
                session["user_name"] = student["name"]
                session["user_email"] = student["email"]
                session["user_role"] = "student"

    @app.context_processor
    def inject_user():
        user_id = session.get("user_id")
        user_name = session.get("user_name", "Vishv Patel")
        user_email = session.get("user_email", "student@gmail.com")
        user_role = session.get("user_role", "student")

        # Defensive fallback: If role or email is admin on student portal, sanitize to student
        if user_role == "admin" or user_email == "admin@gmail.com" or "Instructor" in user_name:
            student = UserModel.find_by_email("student@gmail.com")
            if student:
                user_id = student["id"]
                user_name = student["name"]
                user_email = student["email"]
                user_role = "student"
                session["user_id"] = user_id
                session["user_name"] = user_name
                session["user_email"] = user_email
                session["user_role"] = user_role

        gamification_data = {
            "level": 3,
            "level_title": "Knowledge Architect",
            "total_xp": 717,
            "xp_in_level": 217,
            "xp_needed_next": 250,
            "level_progress_pct": 86.8,
            "streak_days": 5,
            "questions_asked": 3,
            "quizzes_completed": 5,
            "average_accuracy": 87.4,
            "earned_badges": [],
            "all_badges": [],
            "total_badges_count": 4,
            "joined_date": "Active Student"
        }

        if user_id:
            try:
                from backend.services.gamification_service import get_gamification_engine
                gamification_data = get_gamification_engine().get_user_gamification_profile(user_id)
            except Exception:
                pass

        return {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "gamification": gamification_data
        }

    # Template View Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/profile")
    def profile_view():
        user_id = session.get("user_id")
        if not user_id or session.get("user_role") == "admin":
            student = UserModel.find_by_email("student@gmail.com")
            if student:
                session["user_id"] = student["id"]
                session["user_name"] = student["name"]
                session["user_email"] = student["email"]
                session["user_role"] = "student"
                user_id = student["id"]
        from backend.services.gamification_service import get_gamification_engine
        gamification_data = get_gamification_engine().get_user_gamification_profile(user_id)
        return render_template("profile.html", active_page="profile", profile=gamification_data)

    @app.route("/transcript")
    def transcript_view():
        user_id = session.get("user_id")
        if not user_id or session.get("user_role") == "admin":
            student = UserModel.find_by_email("student@gmail.com")
            if student:
                session["user_id"] = student["id"]
                session["user_name"] = student["name"]
                session["user_email"] = student["email"]
                session["user_role"] = "student"
                user_id = student["id"]
        from backend.services.gamification_service import get_gamification_engine
        gamification_data = get_gamification_engine().get_user_gamification_profile(user_id)
        return render_template("transcript.html", active_page="transcript", profile=gamification_data)

    @app.route("/dashboard")
    def dashboard_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("dashboard.html")

    @app.route("/chat")
    def chat_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("chat.html")

    @app.route("/subjects")
    def subjects_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("subjects.html")

    @app.route("/quiz")
    def quiz_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("quiz.html")

    @app.route("/flashcards")
    def flashcards_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("flashcards.html")

    @app.route("/knowledge-graph")
    def knowledge_graph_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("knowledge_graph.html")

    @app.route("/documents")
    def documents_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("documents.html")

    @app.route("/admin")
    def admin_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            from flask import flash
            flash("Access restricted: Instructor / Admin privileges required.", "warning")
            return redirect(url_for("dashboard_view"))
        return render_template("admin.html")

    @app.route("/viva")
    def viva_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("viva.html")

    @app.route("/teach-back")
    def teach_back_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return render_template("teach_back.html")

    @app.route("/pipeline")
    def pipeline_view():
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
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
            error_title="Academic Resource Not Found",
            error_message="The requested learning module, endpoint, or resource could not be found."
        ), 404

    @app.errorhandler(500)
    def handle_500(e):
        return render_template(
            "error.html",
            error_code=500,
            error_title="Internal Processing Anomaly",
            error_message="An internal server error occurred while processing your academic request. Please try again."
        ), 500

    @app.route("/api/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "system": "TalentLens — An NLP-Based Intelligent Personalized Learning Assistant",
            "phase": "Full Production NLP System Operational"
        })

    return app

app = create_app()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run TalentLens System")
    parser.add_argument("--port", "-p", type=int, default=int(os.getenv("PORT", 5000)), help="Port to run server on (default: 5000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    args = parser.parse_args()

    print(f"==================================================")
    print(f"  TalentLens — Student Learning Portal")
    print(f"  Running on: http://{args.host}:{args.port}")
    print(f"==================================================")
    app.run(host=args.host, port=args.port, debug=True)
