import re
import logging
from typing import Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)

# Training data for educational intent classification
TRAINING_DATA = [
    ("What is tokenization?", "ASK_DEFINITION"),
    ("Define normalization in DBMS.", "ASK_DEFINITION"),
    ("What does TF-IDF mean?", "ASK_DEFINITION"),
    ("What is overfitting?", "ASK_DEFINITION"),
    ("Can you define word embeddings?", "ASK_DEFINITION"),
    ("What is the meaning of lemmatization?", "ASK_DEFINITION"),

    ("Explain TF-IDF step by step.", "ASK_EXPLANATION"),
    ("How does self-attention work in Transformers?", "ASK_EXPLANATION"),
    ("Explain overfitting and why it occurs.", "ASK_EXPLANATION"),
    ("Why is normalization important in database design?", "ASK_EXPLANATION"),
    ("Explain the difference between stemming and lemmatization.", "ASK_EXPLANATION"),
    ("Elaborate on how Word2Vec works.", "ASK_EXPLANATION"),

    ("Give me an example of tokenization.", "ASK_EXAMPLE"),
    ("Show an example of 3NF in DBMS.", "ASK_EXAMPLE"),
    ("Can you provide a code example for Python list comprehension?", "ASK_EXAMPLE"),
    ("Demonstrate an example of overfitting.", "ASK_EXAMPLE"),
    ("Give me a practical example of TF-IDF calculation.", "ASK_EXAMPLE"),

    ("Compare stemming vs lemmatization.", "ASK_COMPARISON"),
    ("What is the difference between supervised and unsupervised learning?", "ASK_COMPARISON"),
    ("Compare 3NF and BCNF.", "ASK_COMPARISON"),
    ("Difference between list and tuple in Python.", "ASK_COMPARISON"),
    ("How does Word2Vec compare to GloVe?", "ASK_COMPARISON"),

    ("What is the formula for TF-IDF?", "ASK_FORMULA"),
    ("Give me the formula for Inverse Document Frequency.", "ASK_FORMULA"),
    ("What is the mathematical equation for attention mechanism?", "ASK_FORMULA"),

    ("Give me 5 questions about NLP tokenization.", "GENERATE_QUIZ"),
    ("Quiz me on Machine Learning overfitting.", "GENERATE_QUIZ"),
    ("Generate a quiz for DBMS normalization.", "GENERATE_QUIZ"),
    ("Test my knowledge on Python data structures.", "GENERATE_QUIZ"),
    ("Create a 10 question quiz on Transformers.", "GENERATE_QUIZ"),

    ("Here is my answer to the question.", "SUBMIT_ANSWER"),
    ("My answer is tokenization divides sentences into words.", "SUBMIT_ANSWER"),
    ("Option B is the correct answer.", "SUBMIT_ANSWER"),

    ("Summarize Transformers architecture.", "ASK_SUMMARY"),
    ("Give me a summary of normalization forms.", "ASK_SUMMARY"),
    ("Briefly summarize overfitting remedies.", "ASK_SUMMARY"),

    ("Hello", "GREETING"),
    ("Hi tutor", "GREETING"),
    ("Hey there", "GREETING"),
    ("Good morning", "GREETING"),
]

class IntentClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self.classifier = LogisticRegression(C=5.0, max_iter=200)
        self.is_trained = False
        self._train()

    def _train(self):
        X_train = [text for text, intent in TRAINING_DATA]
        y_train = [intent for text, intent in TRAINING_DATA]
        X_vec = self.vectorizer.fit_transform(X_train)
        self.classifier.fit(X_vec, y_train)
        self.is_trained = True
        logger.info("IntentClassifier trained on educational intent dataset.")

    def predict(self, text: str) -> Dict[str, Any]:
        cleaned = text.strip().lower()
        if not cleaned:
            return {"intent": "GENERAL_QUERY", "confidence": 1.0}

        # Rule-based regex overrides for canonical commands
        if re.search(r'\b(quiz|test|generate questions|test me)\b', cleaned):
            return {"intent": "GENERATE_QUIZ", "confidence": 0.98}
        if re.search(r'\b(hi|hello|hey|greetings|good morning)\b', cleaned) and len(cleaned.split()) <= 3:
            return {"intent": "GREETING", "confidence": 0.99}
        if re.search(r'\b(compare|difference between|vs|versus)\b', cleaned):
            return {"intent": "ASK_COMPARISON", "confidence": 0.95}
        if re.search(r'\b(example|sample|instance|code example)\b', cleaned):
            return {"intent": "ASK_EXAMPLE", "confidence": 0.95}
        if re.search(r'\b(formula|equation|mathematical)\b', cleaned):
            return {"intent": "ASK_FORMULA", "confidence": 0.95}

        # ML Model Inference
        vec = self.vectorizer.transform([cleaned])
        probs = self.classifier.predict_proba(vec)[0]
        max_idx = probs.argmax()
        intent = self.classifier.classes_[max_idx]
        confidence = float(probs[max_idx])

        return {
            "intent": intent,
            "confidence": round(confidence, 3)
        }

_intent_classifier = IntentClassifier()

def detect_intent(text: str) -> Dict[str, Any]:
    return _intent_classifier.predict(text)
