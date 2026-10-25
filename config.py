import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "ai-tutor-dev-secret-key-change-in-prod")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ai_tutor_system")
    
    # LLM Settings
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    
    # NLP Model Settings
    SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")
    SENTENCE_TRANSFORMER_MODEL = os.getenv("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
