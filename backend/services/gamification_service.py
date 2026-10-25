from typing import Dict, Any, List
from backend.utils.db import get_db

LEVEL_TITLES = {
    1: "NLP Explorer",
    2: "Curious Scholar",
    3: "Knowledge Architect",
    4: "Prompt Engineer",
    5: "AI Synthesizer",
    6: "Master of Language Models"
}

class GamificationEngine:
    """
    Manages XP points, level calculation, study streaks, and badge achievements.
    """

    BADGES_DEFINITIONS = [
        {"id": "first_question", "name": "Curious Mind", "icon": "fa-comment-dots", "desc": "Asked your first question to the AI Tutor.", "color": "#3b82f6"},
        {"id": "quiz_beginner", "name": "Quiz Cadet", "icon": "fa-vial", "desc": "Completed your first practice quiz.", "color": "#10b981"},
        {"id": "nlp_master", "name": "NLP Specialist", "icon": "fa-brain", "desc": "Achieved >85% accuracy in Natural Language Processing.", "color": "#8b5cf6"},
        {"id": "dbms_architect", "name": "Database Architect", "icon": "fa-database", "desc": "Mastered Normalization & DBMS concepts.", "color": "#f59e0b"},
        {"id": "streak_3d", "name": "Consistent Learner", "icon": "fa-fire", "desc": "Maintained a multi-session study streak.", "color": "#ef4444"},
    ]

    def get_user_gamification_profile(self, user_id: str) -> Dict[str, Any]:
        from backend.models.user import UserModel
        db = get_db()
        conv_count = len(list(db.conversations.find({"user_id": user_id})))
        quizzes = list(db.quizzes.find({"user_id": user_id}))
        progress_docs = list(db.learning_progress.find({"user_id": user_id}))

        quiz_count = len(quizzes)
        avg_score = round(sum(q.get("score", 0) for q in quizzes) / max(quiz_count, 1), 2) if quiz_count > 0 else 0.0

        # Calculate XP Points: base + 10 XP per question + 50 XP per quiz + bonus for scores
        total_xp = (conv_count * 10) + (quiz_count * 50) + int(sum(q.get("score", 0) for q in quizzes))

        # Level calculation: Level N at every 250 XP
        level = max(1, (total_xp // 250) + 1)
        level_title = LEVEL_TITLES.get(level, f"Level {level} Master")
        xp_in_level = total_xp % 250
        level_progress_pct = round((xp_in_level / 250.0) * 100, 1)

        # Award Badges
        earned_ids = set()
        if conv_count > 0:
            earned_ids.add("first_question")
        if quiz_count > 0:
            earned_ids.add("quiz_beginner")

        # Check domain mastery
        for p in progress_docs:
            if p.get("subject") == "Natural Language Processing" and p.get("accuracy", 0) >= 85.0:
                earned_ids.add("nlp_master")
            if p.get("subject") == "Database Management Systems" and p.get("accuracy", 0) >= 85.0:
                earned_ids.add("dbms_architect")

        if conv_count >= 3 or quiz_count >= 2:
            earned_ids.add("streak_3d")

        earned_badges = [b for b in self.BADGES_DEFINITIONS if b["id"] in earned_ids]
        all_badges_status = []
        for b in self.BADGES_DEFINITIONS:
            b_copy = dict(b)
            b_copy["unlocked"] = b["id"] in earned_ids
            all_badges_status.append(b_copy)

        # User registered details
        user_doc = UserModel.find_by_id(user_id) if user_id and user_id != "guest_user" else None
        user_name = user_doc.get("name", "Student") if user_doc else "Student"
        user_email = user_doc.get("email", "") if user_doc else ""
        user_role = user_doc.get("role", "student") if user_doc else "student"
        joined_date = str(user_doc.get("created_at", ""))[:10] if user_doc and user_doc.get("created_at") else "Recently"
        pref_subject = user_doc.get("learning_preferences", {}).get("preferred_subject", "Natural Language Processing") if user_doc else "Natural Language Processing"

        return {
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_role": user_role,
            "joined_date": joined_date,
            "preferred_subject": pref_subject,
            "total_xp": total_xp,
            "level": level,
            "level_title": level_title,
            "xp_in_level": xp_in_level,
            "xp_needed_next": 250,
            "level_progress_pct": level_progress_pct,
            "earned_badges": earned_badges,
            "all_badges": all_badges_status,
            "total_badges_count": len(earned_badges),
            "streak_days": max(1, min(7, (conv_count + quiz_count) // 2 + 1)),
            "questions_asked": conv_count,
            "quizzes_completed": quiz_count,
            "average_accuracy": avg_score
        }

_gamification_engine = GamificationEngine()

def get_gamification_engine():
    return _gamification_engine
