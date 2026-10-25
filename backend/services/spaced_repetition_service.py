import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from backend.utils.db import get_db

class SpacedRepetitionEngine:
    """
    SuperMemo-2 (SM-2) Spaced Repetition Algorithm Implementation.
    Calculates review interval, repetition count, and ease factor based on performance grade (0 to 5).
    """

    @staticmethod
    def calculate_sm2(grade: int, repetitions: int, interval: int, ease_factor: float) -> Dict[str, Any]:
        """
        grade: 0-5 (0=complete black out, 5=perfect response)
        repetitions: number of successful consecutive reviews
        interval: current review interval in days
        ease_factor: current EF multiplier (default 2.5)
        """
        grade = max(0, min(5, grade))
        
        if grade >= 3:
            if repetitions == 0:
                new_interval = 1
            elif repetitions == 1:
                new_interval = 6
            else:
                new_interval = min(365, math.ceil(interval * ease_factor))
            new_repetitions = repetitions + 1
        else:
            new_repetitions = 0
            new_interval = 1

        # Calculate new ease factor
        new_ef = ease_factor + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))
        new_ef = max(1.3, round(new_ef, 2))

        next_review_date = datetime.now(timezone.utc) + timedelta(days=new_interval)

        return {
            "repetitions": new_repetitions,
            "interval": new_interval,
            "ease_factor": new_ef,
            "next_review_date": next_review_date,
            "due_today": True if new_interval <= 1 else False
        }

    def record_topic_review(self, user_id: str, topic: str, score_percent: float) -> Dict[str, Any]:
        db = get_db()
        existing = db.spaced_repetition.find_one({"user_id": user_id, "topic": topic})

        # Map score percentage (0-100) to SM-2 grade (0-5)
        if score_percent >= 90:
            grade = 5
        elif score_percent >= 80:
            grade = 4
        elif score_percent >= 65:
            grade = 3
        elif score_percent >= 50:
            grade = 2
        elif score_percent >= 30:
            grade = 1
        else:
            grade = 0

        repetitions = existing.get("repetitions", 0) if existing else 0
        interval = existing.get("interval", 1) if existing else 1
        ease_factor = existing.get("ease_factor", 2.5) if existing else 2.5

        sm2_res = self.calculate_sm2(grade, repetitions, interval, ease_factor)

        record_doc = {
            "user_id": user_id,
            "topic": topic,
            "last_score": score_percent,
            "last_reviewed": datetime.now(timezone.utc),
            "next_review_date": sm2_res["next_review_date"],
            "repetitions": sm2_res["repetitions"],
            "interval": sm2_res["interval"],
            "ease_factor": sm2_res["ease_factor"]
        }

        if existing:
            db.spaced_repetition.update_one({"_id": existing["_id"]}, {"$set": record_doc})
        else:
            db.spaced_repetition.insert_one(record_doc)

        return sm2_res

    def get_due_reviews(self, user_id: str) -> List[Dict[str, Any]]:
        db = get_db()
        now = datetime.now(timezone.utc)
        records = list(db.spaced_repetition.find({"user_id": user_id}))

        due_topics = []
        for r in records:
            next_date = r.get("next_review_date")
            if next_date and (isinstance(next_date, str) or next_date <= now):
                due_topics.append({
                    "topic": r.get("topic"),
                    "last_score": r.get("last_score", 0),
                    "interval_days": r.get("interval", 1),
                    "next_review_date": str(next_date)
                })

        return due_topics

_spaced_repetition_engine = SpacedRepetitionEngine()

def get_spaced_repetition_engine():
    return _spaced_repetition_engine
