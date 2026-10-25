import csv
import io
from flask import Blueprint, request, jsonify, session, Response
from backend.services.admin_service import get_admin_service
from backend.services.knowledge_service import get_knowledge_service

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/dashboard", methods=["GET"])
def get_admin_dashboard_metrics():
    service = get_admin_service()
    analytics = service.get_cohort_analytics()
    return jsonify(analytics)

@admin_bp.route("/students", methods=["GET"])
def get_students_list():
    service = get_admin_service()
    roster = service.get_students_roster()
    return jsonify({"students": roster, "total": len(roster)})

@admin_bp.route("/students/export-csv", methods=["GET"])
def export_students_csv():
    service = get_admin_service()
    roster = service.get_students_roster()

    output = io.StringIO()
    writer = csv.writer(output)

    # Official Gradebook CSV Header
    writer.writerow([
        "Student ID",
        "Student Name",
        "Email Address",
        "Enrolled Track / Subject",
        "Quizzes Attempted",
        "Average Accuracy (%)",
        "Active Study Streak",
        "Total XP",
        "Current Mastery Level",
        "Mastered Topics",
        "Weak Topics (Need Intervention)",
        "Academic Status"
    ])

    for s in roster:
        accuracy = s.get("average_accuracy", s.get("average_score", 0.0))
        status = "Exemplary (A+)" if accuracy >= 88.0 else ("Competent (A)" if accuracy >= 75.0 else "Needs Academic Support")
        mastered_str = "; ".join(s.get("mastered_topics", [])) or "In Progress"
        weak_str = "; ".join(s.get("weak_topics", [])) or "None Identified"

        writer.writerow([
            s.get("id", "TL-STU"),
            s.get("name", "Student"),
            s.get("email", ""),
            s.get("preferred_subject", "Natural Language Processing"),
            s.get("quizzes_taken", 0),
            f"{accuracy}%",
            f"{s.get('streak_days', 1)} days",
            s.get("total_xp", 150),
            f"Level {s.get('level', 1)}",
            mastered_str,
            weak_str,
            status
        ])

    csv_data = output.getvalue()
    output.close()

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=TalentLens_Student_Cohort_Gradebook_2026.csv"}
    )

@admin_bp.route("/knowledge/list", methods=["GET"])
def list_knowledge_concepts():
    kb = get_knowledge_service()
    return jsonify({"concepts": kb.knowledge_items, "total": len(kb.knowledge_items)})

@admin_bp.route("/knowledge/add", methods=["POST"])
def add_knowledge_concept():
    data = request.get_json() or {}
    service = get_admin_service()
    try:
        result = service.add_knowledge_concept(data)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to publish concept: {str(e)}"}), 500

@admin_bp.route("/knowledge/delete/<concept_id>", methods=["DELETE", "POST"])
def delete_knowledge_concept(concept_id):
    service = get_admin_service()
    success = service.delete_knowledge_concept(concept_id)
    if success:
        return jsonify({"message": f"Concept '{concept_id}' deleted and vector index rebuilt."})
    return jsonify({"error": f"Concept '{concept_id}' not found."}), 404

@admin_bp.route("/quiz/add-question", methods=["POST"])
def add_quiz_question():
    data = request.get_json() or {}
    subject = data.get("subject", "Natural Language Processing")
    topic = data.get("topic", "Tokenization")
    question_data = data.get("question", {})

    service = get_admin_service()
    try:
        res = service.add_quiz_question(subject, topic, question_data)
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to add question: {str(e)}"}), 500

@admin_bp.route("/blind-spots", methods=["GET"])
def get_blind_spots():
    service = get_admin_service()
    result = service.get_curriculum_blind_spots()
    return jsonify(result)

@admin_bp.route("/rubric/config", methods=["GET", "POST"])
def rubric_config():
    service = get_admin_service()
    if request.method == "POST":
        data = request.get_json() or {}
        res = service.update_grading_config(data)
        return jsonify(res)
    else:
        cfg = service.get_grading_config()
        return jsonify({"config": cfg})

@admin_bp.route("/rubric/simulate", methods=["POST"])
def simulate_rubric():
    data = request.get_json() or {}
    expected = data.get("expected_answer", "")
    student = data.get("student_answer", "")
    custom_cfg = data.get("custom_config")

    service = get_admin_service()
    res = service.simulate_grading(expected, student, custom_cfg)
    return jsonify(res)

@admin_bp.route("/student/<student_id>/cognitive-dna", methods=["GET"])
def get_student_cognitive_dna(student_id):
    service = get_admin_service()
    dna = service.get_student_cognitive_dna(student_id)
    return jsonify(dna)

