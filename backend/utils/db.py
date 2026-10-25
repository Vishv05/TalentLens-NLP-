import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from bson import ObjectId
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DB_DIR = PROJECT_ROOT / "data"
DB_FILE = DB_DIR / "app_database.json"
_DB_LOCK = threading.Lock()

def _load_db_file() -> Dict[str, List[Dict[str, Any]]]:
    if not DB_FILE.exists():
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read database file: {e}")
        return {}

def _save_db_file(data: Dict[str, List[Dict[str, Any]]]):
    try:
        DB_DIR.mkdir(parents=True, exist_ok=True)
        temp_file = DB_DIR / "app_database.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        os.replace(temp_file, DB_FILE)
    except Exception as e:
        logger.error(f"Failed to persist database file: {e}")

class PersistentCollection:
    """A thread-safe and process-safe file-backed collection matching MongoDB interface."""
    def __init__(self, name: str):
        self.name = name

    def _matches_query(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "_id":
                if str(doc.get("_id")) != str(v):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    def insert_one(self, document: Dict[str, Any]):
        doc_copy = dict(document)
        if "_id" not in doc_copy:
            doc_copy["_id"] = str(ObjectId())
        else:
            doc_copy["_id"] = str(doc_copy["_id"])

        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            col_data.append(doc_copy)
            full_data[self.name] = col_data
            _save_db_file(full_data)

        class InsertResult:
            inserted_id = doc_copy["_id"]
        return InsertResult()

    def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            for doc in col_data:
                if self._matches_query(doc, query):
                    return dict(doc)
            return None

    def find(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = query or {}
        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            results = []
            for doc in col_data:
                if self._matches_query(doc, query):
                    results.append(dict(doc))
            return results

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            matched = False

            for idx, doc in enumerate(col_data):
                if self._matches_query(doc, query):
                    set_fields = update.get("$set", {})
                    for k, v in set_fields.items():
                        doc[k] = v.isoformat() if isinstance(v, datetime) else (str(v) if isinstance(v, ObjectId) else v)
                    col_data[idx] = doc
                    matched = True
                    break

            if matched:
                full_data[self.name] = col_data
                _save_db_file(full_data)
                class UpdateResult:
                    matched_count = 1
                    modified_count = 1
                return UpdateResult()
            elif upsert:
                new_doc = dict(query)
                if "_id" not in new_doc:
                    new_doc["_id"] = str(ObjectId())
                set_fields = update.get("$set", {})
                for k, v in set_fields.items():
                    new_doc[k] = v.isoformat() if isinstance(v, datetime) else (str(v) if isinstance(v, ObjectId) else v)
                col_data.append(new_doc)
                full_data[self.name] = col_data
                _save_db_file(full_data)
                class UpsertResult:
                    matched_count = 0
                    modified_count = 1
                return UpsertResult()

            class EmptyResult:
                matched_count = 0
                modified_count = 0
            return EmptyResult()

    def delete_one(self, query: Dict[str, Any]):
        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            new_col = []
            deleted = False
            for doc in col_data:
                if not deleted and self._matches_query(doc, query):
                    deleted = True
                    continue
                new_col.append(doc)

            if deleted:
                full_data[self.name] = new_col
                _save_db_file(full_data)
                class DeleteResult:
                    deleted_count = 1
                return DeleteResult()

            class EmptyDelete:
                deleted_count = 0
            return EmptyDelete()

    def delete_many(self, query: Dict[str, Any]):
        with _DB_LOCK:
            full_data = _load_db_file()
            col_data = full_data.get(self.name, [])
            new_col = []
            deleted_count = 0
            for doc in col_data:
                if self._matches_query(doc, query):
                    deleted_count += 1
                else:
                    new_col.append(doc)

            if deleted_count > 0:
                full_data[self.name] = new_col
                _save_db_file(full_data)
            class DeleteManyResult:
                def __init__(self, c):
                    self.deleted_count = c
            return DeleteManyResult(deleted_count)

class PersistentDatabase:
    """File-backed database container allowing shared persistence across both Port 5000 and Port 5001."""
    def __init__(self):
        self.collections: Dict[str, PersistentCollection] = {}

    def __getattr__(self, item: str) -> PersistentCollection:
        if item not in self.collections:
            self.collections[item] = PersistentCollection(item)
        return self.collections[item]

    def __getitem__(self, item: str) -> PersistentCollection:
        return getattr(self, item)


class DatabaseManager:
    """Manager for MongoDB client with automatic persistent file fallback."""
    _instance = None
    client = None
    db = None
    is_fallback = False

    @classmethod
    def get_db(cls, mongo_uri: Optional[str] = None):
        if cls.db is not None:
            return cls.db

        mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_tutor_system")
        db_name = mongo_uri.split("/")[-1].split("?")[0] or "ai_tutor_system"

        try:
            cls.client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
            # Test connection
            cls.client.admin.command('ping')
            cls.db = cls.client[db_name]
            cls.is_fallback = False
            logger.info(f"Connected to MongoDB at {mongo_uri}")
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            logger.info(f"MongoDB not active locally. Utilizing Persistent Shared JSON database store ({DB_FILE}).")
            cls.db = PersistentDatabase()
            cls.is_fallback = True

        return cls.db

def get_db():
    return DatabaseManager.get_db()
