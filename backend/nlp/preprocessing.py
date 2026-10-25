import re
import logging
from typing import Dict, Any, List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy

logger = logging.getLogger(__name__)

# Ensure NLTK datasets are downloaded safely
try:
    nltk.data.find('corpora/stopwords')
except Exception:
    try:
        nltk.download('stopwords', quiet=True)
    except Exception:
        pass

try:
    nltk.data.find('corpora/wordnet')
except Exception:
    try:
        nltk.download('wordnet', quiet=True)
    except Exception:
        pass

try:
    nltk.data.find('tokenizers/punkt')
except Exception:
    try:
        nltk.download('punkt', quiet=True)
    except Exception:
        pass

# Singleton spaCy model loader
_spacy_nlp = None

def get_spacy_nlp():
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy en_core_web_sm model successfully.")
        except Exception as e:
            logger.warning(f"Could not load spaCy en_core_web_sm ({e}). Downloading model...")
            spacy.cli.download("en_core_web_sm")
            _spacy_nlp = spacy.load("en_core_web_sm")
    return _spacy_nlp


class NLPPipeline:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def clean_text(self, text: str) -> str:
        """Clean text by removing extra spaces and special noise characters."""
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive NLP analysis returning structured data suitable for
        academic presentation, debugging, and downstream classifiers.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return {
                "raw_text": text,
                "cleaned_text": "",
                "tokens": [],
                "lemmas": [],
                "pos_tags": [],
                "entities": [],
                "stopwords": [],
                "noun_chunks": []
            }

        nlp = get_spacy_nlp()
        doc = nlp(cleaned)

        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        pos_tags = [(token.text, token.pos_, token.tag_) for token in doc]
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        detected_stopwords = [token.text for token in doc if token.is_stop or token.text.lower() in self.stop_words]
        noun_chunks = [chunk.text for chunk in doc.noun_chunks]

        return {
            "raw_text": text,
            "cleaned_text": cleaned,
            "tokens": tokens,
            "lemmas": lemmas,
            "pos_tags": pos_tags,
            "entities": entities,
            "stopwords": detected_stopwords,
            "noun_chunks": noun_chunks,
            "word_count": len(tokens)
        }

_nlp_pipeline = NLPPipeline()

def analyze_text(text: str) -> Dict[str, Any]:
    return _nlp_pipeline.analyze(text)
