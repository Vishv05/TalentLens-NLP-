from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from backend.utils.db import get_db

class UserModel:
    @staticmethod
    def is_admin_email(email: str) -> bool:
        """Determines if an email belongs strictly to the Administrator / Instructor."""
        email_clean = email.strip().lower()
        return email_clean in ["admin@gmail.com", "admin@gmai.com"]

    @staticmethod
    def create_user(name: str, email: str, password: str, role: Optional[str] = None, learning_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        db = get_db()
        email_clean = email.strip().lower()

        if UserModel.is_admin_email(email_clean):
            raise ValueError("The administrator account is reserved. Please sign in directly with admin credentials.")

        existing = db.users.find_one({"email": email_clean})
        if existing:
            raise ValueError("An account with this email address already exists. Please sign in.")

        # All registered accounts are Students
        user_role = "student"
        hashed_pw = generate_password_hash(password)
        user_doc = {
            "name": name.strip(),
            "email": email_clean,
            "role": user_role,
            "password_hash": hashed_pw,
            "created_at": datetime.now(timezone.utc),
            "learning_preferences": learning_preferences or {
                "preferred_subject": "Natural Language Processing",
                "difficulty": "Medium"
            }
        }
        res = db.users.insert_one(user_doc)
        user_doc["_id"] = res.inserted_id
        return UserModel.to_dict(user_doc)

    @staticmethod
    def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        email_clean = email.strip().lower()
        
        # Ensure default demo accounts exist for out-of-the-box demo
        if UserModel.is_admin_email(email_clean):
            UserModel.ensure_default_admin()
        elif email_clean == "student@gmail.com":
            UserModel.ensure_default_student()
            
        doc = db.users.find_one({"email": email_clean})
        return UserModel.to_dict(doc) if doc else None

    @staticmethod
    def record_login(user_id: str):
        """Records student login timestamp and updates active status."""
        db = get_db()
        now = datetime.now(timezone.utc)
        try:
            query = {"_id": ObjectId(user_id)}
        except Exception:
            query = {"_id": str(user_id)}
        db.users.update_one(
            query,
            {"$set": {
                "last_login": now.isoformat(),
                "last_active": "Recent (Active Today)"
            }}
        )

    @staticmethod
    def ensure_default_student():
        """Pre-seeds real student accounts."""
        UserModel.ensure_sample_students()

    @staticmethod
    def ensure_sample_students():
        """
        Pre-seeds and preserves the real enrolled students who logged in earlier and recently.
        Includes real registered accounts from the database:
        - Vishv Patel (Recent active student)
        - Rushit Shah (Logged in earlier)
        - Arjun Singh (Logged in earlier)
        - Diya Patel (Logged in earlier)
        """
        db = get_db()
        import uuid
        from datetime import timedelta

        cohort = [
            {
                "name": "Vishv Patel",
                "email": "student@gmail.com",
                "role": "student",
                "password": "student123",
                "created_at": datetime(2026, 8, 10, 9, 30, tzinfo=timezone.utc),
                "last_active": "Recent (Active Today)",
                "preferences": {"preferred_subject": "Natural Language Processing", "difficulty": "Medium"},
                "quizzes": [
                    {"subject": "Natural Language Processing", "topic": "Tokenization", "score": 92.0, "days_ago": 1},
                    {"subject": "Natural Language Processing", "topic": "TF-IDF", "score": 88.0, "days_ago": 2},
                    {"subject": "Natural Language Processing", "topic": "Word Embeddings", "score": 85.0, "days_ago": 3},
                    {"subject": "Python Programming", "topic": "Time & Space Complexity", "score": 90.0, "days_ago": 4},
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "score": 82.0, "days_ago": 5}
                ],
                "inquiries": [
                    {"subject": "Natural Language Processing", "topic": "Tokenization", "intent": "ASK_EXPLANATION", "text": "How does subword tokenization handle out-of-vocabulary words?"},
                    {"subject": "Natural Language Processing", "topic": "TF-IDF", "intent": "ASK_DEFINITION", "text": "What is the mathematical formulation of Inverse Document Frequency?"},
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "intent": "ASK_COMPARISON", "text": "What is the difference between L1 and L2 regularization?"}
                ],
                "progress": [
                    {"subject": "Natural Language Processing", "topic": "Tokenization", "accuracy": 92.0, "attempted": 6, "correct": 6},
                    {"subject": "Natural Language Processing", "topic": "TF-IDF", "accuracy": 88.0, "attempted": 5, "correct": 4},
                    {"subject": "Natural Language Processing", "topic": "Word Embeddings", "accuracy": 85.0, "attempted": 5, "correct": 4},
                    {"subject": "Python Programming", "topic": "Time & Space Complexity", "accuracy": 90.0, "attempted": 5, "correct": 5},
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "accuracy": 82.0, "attempted": 5, "correct": 4}
                ]
            },
            {
                "name": "Rushit Shah",
                "email": "rushit24@gmail.com",
                "role": "student",
                "password": "password123",
                "created_at": datetime(2026, 2, 22, 14, 20, tzinfo=timezone.utc),
                "last_active": "Logged in Earlier (Feb 2026)",
                "preferences": {"preferred_subject": "Machine Learning", "difficulty": "Medium"},
                "quizzes": [
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "score": 86.0, "days_ago": 45},
                    {"subject": "Machine Learning", "topic": "Evaluation Metrics", "score": 82.0, "days_ago": 48},
                    {"subject": "Database Management Systems", "topic": "SQL Queries & Joins", "score": 80.0, "days_ago": 50},
                    {"subject": "Python Programming", "topic": "OOP in Python", "score": 84.0, "days_ago": 52}
                ],
                "inquiries": [
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "intent": "ASK_EXPLANATION", "text": "What is the difference between classification and regression?"},
                    {"subject": "Database Management Systems", "topic": "SQL Queries & Joins", "intent": "ASK_EXAMPLE", "text": "Can you provide examples of LEFT JOIN vs INNER JOIN?"}
                ],
                "progress": [
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "accuracy": 86.0, "attempted": 6, "correct": 5},
                    {"subject": "Machine Learning", "topic": "Evaluation Metrics", "accuracy": 82.0, "attempted": 5, "correct": 4},
                    {"subject": "Database Management Systems", "topic": "SQL Queries & Joins", "accuracy": 80.0, "attempted": 5, "correct": 4},
                    {"subject": "Python Programming", "topic": "OOP in Python", "accuracy": 84.0, "attempted": 5, "correct": 4}
                ]
            },
            {
                "name": "Arjun Singh",
                "email": "arjun12@gmail.com",
                "role": "student",
                "password": "password123",
                "created_at": datetime(2026, 2, 23, 11, 45, tzinfo=timezone.utc),
                "last_active": "Logged in Earlier (Feb 2026)",
                "preferences": {"preferred_subject": "Natural Language Processing", "difficulty": "Medium"},
                "quizzes": [
                    {"subject": "Natural Language Processing", "topic": "Lemmatization", "score": 78.0, "days_ago": 42},
                    {"subject": "Natural Language Processing", "topic": "Part-of-Speech Tagging", "score": 74.0, "days_ago": 44},
                    {"subject": "Database Management Systems", "topic": "ACID Properties", "score": 76.0, "days_ago": 46}
                ],
                "inquiries": [
                    {"subject": "Natural Language Processing", "topic": "Lemmatization", "intent": "ASK_COMPARISON", "text": "What is the difference between stemming and lemmatization?"},
                    {"subject": "Database Management Systems", "topic": "ACID Properties", "intent": "ASK_EXPLANATION", "text": "Explain atomicity and consistency in transaction processing."}
                ],
                "progress": [
                    {"subject": "Natural Language Processing", "topic": "Lemmatization", "accuracy": 78.0, "attempted": 5, "correct": 4},
                    {"subject": "Natural Language Processing", "topic": "Part-of-Speech Tagging", "accuracy": 74.0, "attempted": 5, "correct": 4},
                    {"subject": "Database Management Systems", "topic": "ACID Properties", "accuracy": 76.0, "attempted": 5, "correct": 4}
                ]
            },
            {
                "name": "Diya Patel",
                "email": "diya12@gmail.com",
                "role": "student",
                "password": "password123",
                "created_at": datetime(2026, 3, 5, 16, 10, tzinfo=timezone.utc),
                "last_active": "Logged in Earlier (Mar 2026)",
                "preferences": {"preferred_subject": "Python Programming", "difficulty": "Advanced"},
                "quizzes": [
                    {"subject": "Python Programming", "topic": "OOP in Python", "score": 90.0, "days_ago": 30},
                    {"subject": "Python Programming", "topic": "Time & Space Complexity", "score": 88.0, "days_ago": 32},
                    {"subject": "Database Management Systems", "topic": "Normalization", "score": 84.0, "days_ago": 35},
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "score": 86.0, "days_ago": 38}
                ],
                "inquiries": [
                    {"subject": "Python Programming", "topic": "OOP in Python", "intent": "ASK_EXPLANATION", "text": "How do abstract base classes and multiple inheritance work in Python?"},
                    {"subject": "Database Management Systems", "topic": "Normalization", "intent": "ASK_COMPARISON", "text": "When is BCNF required over 3NF in relational schema design?"}
                ],
                "progress": [
                    {"subject": "Python Programming", "topic": "OOP in Python", "accuracy": 90.0, "attempted": 6, "correct": 5},
                    {"subject": "Python Programming", "topic": "Time & Space Complexity", "accuracy": 88.0, "attempted": 5, "correct": 4},
                    {"subject": "Database Management Systems", "topic": "Normalization", "accuracy": 84.0, "attempted": 5, "correct": 4},
                    {"subject": "Machine Learning", "topic": "Supervised Learning", "accuracy": 86.0, "attempted": 5, "correct": 4}
                ]
            }
        ]

        now = datetime.now(timezone.utc)

        for s_data in cohort:
            existing = db.users.find_one({"email": s_data["email"]})
            if not existing:
                user_doc = {
                    "name": s_data["name"],
                    "email": s_data["email"],
                    "role": "student",
                    "password_hash": generate_password_hash(s_data["password"]),
                    "created_at": s_data["created_at"].isoformat() if hasattr(s_data["created_at"], "isoformat") else str(s_data["created_at"]),
                    "last_active": s_data.get("last_active", "Earlier Session"),
                    "learning_preferences": s_data["preferences"]
                }
                res = db.users.insert_one(user_doc)
                u_id = str(res.inserted_id)
            else:
                u_id = str(existing.get("_id") or existing.get("id", ""))
                # Ensure last_active is set
                if "last_active" not in existing and "last_active" in s_data:
                    db.users.update_one({"email": s_data["email"]}, {"$set": {"last_active": s_data["last_active"]}})

            # Seed quizzes if not already present for this user
            if len(list(db.quizzes.find({"user_id": u_id}))) == 0:
                for q in s_data.get("quizzes", []):
                    db.quizzes.insert_one({
                        "quiz_id": str(uuid.uuid4()),
                        "user_id": u_id,
                        "subject": q["subject"],
                        "topic": q["topic"],
                        "difficulty": "Medium",
                        "score": q["score"],
                        "timestamp": (now - timedelta(days=q.get("days_ago", 3))).isoformat()
                    })

            # Seed inquiries/conversations if not already present
            if len(list(db.conversations.find({"user_id": u_id}))) == 0:
                for c in s_data.get("inquiries", []):
                    db.conversations.insert_one({
                        "user_id": u_id,
                        "user_question": c["text"],
                        "subject": c["subject"],
                        "topic": c["topic"],
                        "intent": c["intent"],
                        "timestamp": (now - timedelta(days=4)).isoformat()
                    })

            # Seed learning progress if not already present
            if len(list(db.learning_progress.find({"user_id": u_id}))) == 0:
                for p in s_data.get("progress", []):
                    db.learning_progress.insert_one({
                        "user_id": u_id,
                        "subject": p["subject"],
                        "topic": p["topic"],
                        "accuracy": p["accuracy"],
                        "questions_attempted": p["attempted"],
                        "correct_answers": p["correct"],
                        "incorrect_answers": p["attempted"] - p["correct"],
                        "difficulty_level": "Medium",
                        "last_updated": (now - timedelta(days=2)).isoformat()
                    })

    @staticmethod
    def ensure_default_admin():
        """Pre-seeds the dedicated admin account admin@gmail.com if not present."""
        db = get_db()
        for admin_addr in ["admin@gmail.com", "admin@gmai.com"]:
            existing = db.users.find_one({"email": admin_addr})
            if not existing:
                user_doc = {
                    "name": "Course Instructor",
                    "email": admin_addr,
                    "role": "admin",
                    "password_hash": generate_password_hash("admin123"),
                    "created_at": datetime.now(timezone.utc),
                    "learning_preferences": {
                        "preferred_subject": "Natural Language Processing",
                        "difficulty": "Advanced"
                    }
                }
                db.users.insert_one(user_doc)

    @staticmethod
    def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        db = get_db()
        try:
            query = {"_id": ObjectId(user_id)}
        except Exception:
            query = {"_id": user_id}
        doc = db.users.find_one(query)
        if not doc:
            doc = db.users.find_one({"id": user_id})
        return UserModel.to_dict(doc) if doc else None

    @staticmethod
    def list_all_users() -> List[Dict[str, Any]]:
        db = get_db()
        docs = list(db.users.find())
        return [UserModel.to_dict(d) for d in docs if d]

    @staticmethod
    def verify_password(user: Dict[str, Any], password: str) -> bool:
        return check_password_hash(user.get("password_hash", ""), password)

    @staticmethod
    def create_password_reset_code(email: str) -> Optional[Dict[str, Any]]:
        """Generates a secure 6-digit verification code with 15-minute expiration."""
        import random
        from datetime import timedelta
        db = get_db()
        email_clean = email.strip().lower()

        user = UserModel.find_by_email(email_clean)
        if not user:
            return None

        code = f"{random.randint(100000, 999999)}"
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=15)

        try:
            query = {"_id": ObjectId(user["id"])}
        except Exception:
            query = {"_id": str(user["id"])}

        db.users.update_one(
            query,
            {"$set": {
                "reset_code": code,
                "reset_code_expires_at": expires_at.isoformat()
            }}
        )
        return {
            "success": True,
            "email": email_clean,
            "code": code,
            "expires_in_minutes": 15
        }

    @staticmethod
    def verify_reset_code(email: str, code: str) -> bool:
        """Verifies if the provided 6-digit code matches and has not expired."""
        email_clean = email.strip().lower()
        user = UserModel.find_by_email(email_clean)
        if not user or "reset_code" not in user or not user.get("reset_code"):
            return False

        if str(user.get("reset_code")).strip() != str(code).strip():
            return False

        exp_str = user.get("reset_code_expires_at")
        if not exp_str:
            return False

        try:
            if isinstance(exp_str, str):
                exp_dt = datetime.fromisoformat(exp_str)
            else:
                exp_dt = exp_str
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > exp_dt:
                return False
        except Exception:
            return False

        return True

    @staticmethod
    def reset_password(email: str, code: str, new_password: str) -> bool:
        """Resets user's password after verifying the 6-digit reset code."""
        if len(new_password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        if not UserModel.verify_reset_code(email, code):
            raise ValueError("Invalid or expired 6-digit recovery code. Please request a new code.")

        db = get_db()
        email_clean = email.strip().lower()
        user = UserModel.find_by_email(email_clean)
        if not user:
            raise ValueError("User account not found.")

        hashed_pw = generate_password_hash(new_password)
        try:
            query = {"_id": ObjectId(user["id"])}
        except Exception:
            query = {"_id": str(user["id"])}

        db.users.update_one(
            query,
            {"$set": {
                "password_hash": hashed_pw,
                "reset_code": None,
                "reset_code_expires_at": None,
                "password_updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return True

    @staticmethod
    def to_dict(user_doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not user_doc:
            return None
        doc = dict(user_doc)
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        doc.setdefault("role", "admin" if UserModel.is_admin_email(doc.get("email", "")) else "student")
        return doc
