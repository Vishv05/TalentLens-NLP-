# TalentLens — NLP-Powered Intelligent Learning & Academic Assessment System

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.0+](https://img.shields.io/badge/Backend-Flask_3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![spaCy](https://img.shields.io/badge/NLP-spaCy_en__core__web__sm-09A3D5?style=for-the-badge&logo=spacy&logoColor=white)](https://spacy.io/)
[![Sentence-Transformers](https://img.shields.io/badge/Embeddings-all--MiniLM--L6--v2-FFA500?style=for-the-badge&logo=huggingface&logoColor=white)](https://www.sbert.net/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Bootstrap 5](https://img.shields.io/badge/UI-Bootstrap_5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

---

## 📌 Overview

**TalentLens** is an end-to-end, intelligent Natural Language Processing (NLP) educational platform and automated academic assessment assistant. While conventional learning platforms (LMS) rely on static multiple-choice questions and generic chatbot wrappers hallucinate ungrounded responses, **TalentLens** bridges deterministic, rigorous **Natural Language Processing** with modern **Generative LLM reasoning**.

The platform features a **Dual-Portal Architecture**:
1. **Student Learning Portal (`Port 5000`)**: Interactive AI tutoring with real-time NLP inspection, Feynman teach-back challenges, adaptive quizzes, mock viva voce defense simulations, SM-2 spaced repetition flashcards, and student lecture notes RAG search.
2. **Instructor & Admin Portal (`Port 5001`)**: Live cohort analytics, misconception and blind-spot detection, dynamic rubric calibration sliders (weighting semantic vector similarity vs. keyword coverage), and curriculum knowledge management.

---

## 🏛️ System Architecture

```
                                      ┌─────────────────────────────────┐
                                      │       Student & Instructor      │
                                      │        Web Client (UI)          │
                                      └────────────────┬────────────────┘
                                                       │
                           ┌───────────────────────────┴───────────────────────────┐
                           ▼                                                       ▼
         ┌───────────────────────────────────┐                   ┌───────────────────────────────────┐
         │       Student Learning Portal     │                   │     Instructor / Admin Portal     │
         │       http://127.0.0.1:5000       │                   │       http://127.0.0.1:5001       │
         └─────────────────┬─────────────────┘                   └─────────────────┬─────────────────┘
                           │                                                       │
                           └───────────────────────────┬───────────────────────────┘
                                                       │  REST API Calls & Sessions
                                                       ▼
                                   ┌───────────────────────────────────────┐
                                   │   Flask Modular Application Factory   │
                                   └───────────────────┬───────────────────┘
                                                       │
         ┌─────────────────────────┬───────────────────┼───────────────────┬─────────────────────────┐
         ▼                         ▼                   ▼                   ▼                         ▼
┌─────────────────┐       ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐       ┌─────────────────┐
│  NLP Preprocess │       │  Intent & Topic │ │ Semantic Vector │ │ Hybrid Grading  │       │  Pedagogical    │
│  & Tokenization │       │ Classification  │ │ Cosine Search   │ │ Evaluation      │       │  Synthesis      │
├─────────────────┤       ├─────────────────┤ ├─────────────────┤ ├─────────────────┤       ├─────────────────┤
│ • spaCy (sm)    │       │ • TF-IDF Vector │ │ • Sentence-     │ │ • 60% Semantic  │       │ • Gemini 1.5    │
│ • Lemmatization │       │ • Logistic Reg. │ │   Transformers  │ │   Similarity    │       │ • OpenAI /      │
│ • POS Tagging   │       │ • Multi-class   │ │ • all-MiniLM-   │ │ • 40% Lemmatized│       │   Ollama Local  │
│ • NER Detection │       │   Confidence    │ │   L6-v2 (384-d) │ │   Keyword Match │       │ • Fallback Mode │
└────────┬────────┘       └────────┬────────┘ └────────┬────────┘ └────────┬────────┘       └────────┬────────┘
         │                         │                   │                   │                         │
         └─────────────────────────┴───────────────────┼───────────────────┴─────────────────────────┘
                                                       │
                                                       ▼
                                      ┌─────────────────────────────────┐
                                      │    Resilient Data Persistence   │
                                      │  MongoDB with File-Backed JSON  │
                                      │  (Thread-Safe In-Memory Store)  │
                                      └─────────────────────────────────┘
```

---

## 🧠 Traditional NLP vs. LLM Responsibility Separation

To guarantee mathematical explainability, low latency, and zero hallucination in evaluation, TalentLens strictly segregates traditional NLP techniques from generative language model synthesis:

| Pipeline Stage | Subsystem / Task | Technology Used | Responsibility |
|---|---|---|---|
| **Text Preprocessing** | Cleaning, tokenization, lemmatization, stopword removal | `spaCy` (`en_core_web_sm`), `NLTK` | Converts raw student input into linguistic tokens and canonical lemma representations. |
| **Linguistic Analysis** | POS Tagging, NER, Noun Chunks | `spaCy` | Identifies syntactic parts of speech (nouns, verbs, adjectives) and extracts domain entities (e.g., TF-IDF, BERT). |
| **Intent Classification** | Intent detection (`ASK_DEFINITION`, `ASK_EXPLANATION`, etc.) | Scikit-Learn `TfidfVectorizer` + `LogisticRegression` | Detects pedagogical intention and query goal deterministically without LLM API overhead. |
| **Topic Detection** | Domain mapping (`NLP`, `Machine Learning`, `DBMS`, `Python`) | Scikit-Learn + Topic Matcher | Maps queries to subjects and curriculum topics with confidence percentages. |
| **Continuous Vector Space** | Dense embedding generation (384 dimensions) | `sentence-transformers` (`all-MiniLM-L6-v2`) | Encodes queries, canonical concepts, and student submissions into dense semantic vectors. |
| **Knowledge Retrieval** | Semantic similarity search | Scikit-Learn `cosine_similarity` | Matches input queries to curated curriculum knowledge nodes using vector dot products. |
| **Short-Answer Grading** | Composite multi-criteria scoring | Vector Cosine Similarity + Lemmatized Set Intersection | Computes weighted score (60% semantic similarity + 40% keyword recall) with threshold checks. |
| **Teach-Back & Viva Scoring** | Jargon penalty, analogy detection, circularity check | Regex patterns + Vector Orthogonality | Evaluates student explanations using the Feynman technique and simulated viva defense rubrics. |
| **Response Generation** | Pedagogical 5-part answer synthesis | Multi-Provider LLM Adapter (`Gemini`, `OpenAI`, `Ollama`) | Synthesizes personalized pedagogical explanations with structured breakdowns and follow-ups. |

---

## ✨ Key Features

### 🎓 1. Student Learning Hub
- **AI Tutor Chat with Live NLP Inspector**: Ask any technical question and see both the pedagogical answer and the live linguistic parsing pipeline (tokens, lemmas, POS tags, NER entities, intent confidence, and cosine similarity).
- **Interactive Practice Quizzes**: Adaptive quizzes categorized across subjects (`NLP`, `Machine Learning`, `DBMS`, `Python`) with automatic evaluation of both multiple-choice and open-ended short-answer questions.
- **The Feynman "Teach-Back" Arena**: Test conceptual clarity by explaining topics in simple language. The NLP engine detects real-world analogies, penalizes verbatim circular definitions, flags jargon over-reliance, and provides constructive feedback.
- **Mock Viva Voce Defense Simulator**: Prepare for academic defenses and oral examinations. The system poses probing technical questions, evaluates student responses against expected keywords and semantic benchmarks, and simulates examiner personas (*Lenient*, *Balanced*, *Strict*).
- **Smart Flashcards (SuperMemo-2 Spaced Repetition)**: Optimized study intervals using the SM-2 / Leitner algorithm to combat the Ebbinghaus forgetting curve.
- **Interactive Concept Knowledge Graph**: Explore topological subject trees, node relationships, and prerequisite concepts visually.
- **Personal Notes Semantic RAG**: Upload lecture notes, syllabi, or PDF slides. The engine chunks text at the sentence boundary with spaCy, generates vector embeddings, and enables context-grounded Q&A.
- **Academic Transcript & Certificate Generator**: Generates an official, printable academic performance transcript detailing mastery across modules, average accuracy, viva defense scores, and earned honors.
- **Gamified Profile & Telemetry**: Track level progression (e.g., *Knowledge Architect*), XP points, active streaks, and milestone badges.

### 🧑‍🏫 2. Instructor & Admin Portal
- **Cohort Analytics**: Real-time telemetry monitoring student enrollment, average quiz accuracy, questions asked, and topic-level mastery.
- **Blind-Spot & Misconception Radar**: Automatically flags topics where student cohort accuracy falls below acceptable thresholds.
- **Dynamic Rubric Calibration**: Interactive sliders to adjust grading weights in real time:
  - Semantic Vector Similarity Weight (default: `65%`)
  - Keyword Coverage Weight (default: `35%`)
  - Pass Threshold (default: `50.0%`)
  - Distinction Threshold (default: `85.0%`)
  - Circularity Penalty & Analogy Bonus values
- **Knowledge Base CMS**: Add, edit, and organize curriculum items, canonical definitions, and reference keywords directly from the browser.
- **Question Studio**: Author, inspect, and calibrate practice quiz questions and expected answers.

---

## 📂 Project Structure

```
TalentLens (NLP)/
├── backend/
│   ├── app.py                      # Student Portal application entrypoint (Port 5000)
│   ├── admin_app.py                # Instructor Portal application entrypoint (Port 5001)
│   ├── __init__.py
│   ├── models/
│   │   ├── user.py                 # User authentication model & session persistence
│   │   └── __init__.py
│   ├── nlp/
│   │   ├── preprocessing.py        # spaCy tokenization, lemmatization, POS tagging, NER
│   │   ├── intent_classifier.py    # TF-IDF + Logistic Regression intent classifier
│   │   ├── topic_classifier.py     # Domain subject & topic classifier
│   │   ├── embeddings.py           # Sentence-Transformers all-MiniLM-L6-v2 vectorizer
│   │   ├── similarity.py           # Cosine similarity & lemmatized keyword coverage
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py                 # Registration, login, logout, password recovery
│   │   ├── tutor.py                # AI Tutor chat & NLP inspection endpoints
│   │   ├── quiz.py                 # Quiz generation & short-answer evaluation endpoints
│   │   ├── viva.py                 # Oral viva voce defense & evaluation endpoints
│   │   ├── feynman.py              # Feynman teach-back challenge endpoints
│   │   ├── pipeline.py             # Step-by-step NLP pipeline visualization endpoint
│   │   ├── documents.py            # Notes upload & RAG retrieval endpoints
│   │   ├── flashcards.py           # Spaced repetition flashcards endpoints
│   │   ├── spaced_repetition.py    # SM-2 Leitner scheduling endpoints
│   │   ├── knowledge_graph.py      # Knowledge graph concept node/edge data
│   │   ├── progress.py             # Learning progress & mastery tracking
│   │   ├── analytics.py            # Student dashboard analytics endpoint
│   │   ├── admin.py                # Instructor dashboard & grading configuration endpoints
│   │   └── __init__.py
│   ├── services/
│   │   ├── tutor_service.py        # Tutor workflow orchestration
│   │   ├── evaluation_service.py   # Hybrid short-answer grading engine
│   │   ├── viva_service.py         # Mock oral defense simulation & rubric scoring
│   │   ├── feynman_service.py      # Feynman teach-back analyzer
│   │   ├── pipeline_service.py     # Text analysis pipeline breakdown
│   │   ├── knowledge_service.py    # Knowledge base vector index & lookup
│   │   ├── knowledge_graph_service.py # Prerequisite topological graph builder
│   │   ├── pdf_rag_service.py      # Document chunking & semantic search
│   │   ├── quiz_service.py         # Dynamic quiz questions & validation
│   │   ├── spaced_repetition_service.py # SuperMemo-2 interval scheduler
│   │   ├── flashcard_service.py    # Curriculum flashcard sets
│   │   ├── gamification_service.py # XP, streaks, levels, and badge awards
│   │   ├── recommendation_service.py # Weak-topic study recommendations
│   │   ├── admin_service.py        # Instructor cohort aggregation & CMS
│   │   ├── llm_service.py          # Multi-provider LLM adapter (Gemini, OpenAI, Ollama)
│   │   └── __init__.py
│   └── utils/
│       ├── db.py                   # MongoDB driver with resilient thread-safe file fallback
│       └── __init__.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css           # Core layout styling & custom utilities
│   │   │   ├── theme.css           # Dark/Light theme system variables
│   │   │   └── companion.css       # Floating AI companion styling
│   │   ├── js/
│   │   │   ├── theme.js            # Theme toggle & persistence logic
│   │   │   └── companion.js        # AI companion interactive behavior
│   │   └── images/
│   │       └── favicon.svg         # Platform brand favicon
│   └── templates/
│       ├── index.html              # Landing page & feature showcase
│       ├── navbar.html             # Global navigation bar with gamified level badge
│       ├── chat.html               # AI Tutor chat with live Academic NLP Inspection Panel
│       ├── dashboard.html          # Student learning telemetry & Chart.js analytics
│       ├── quiz.html               # Practice quizzes with automated short-answer grading
│       ├── viva.html               # Mock Viva Voce Oral Defense Arena
│       ├── teach_back.html         # Feynman Technique Teach-Back Studio
│       ├── pipeline.html           # Interactive step-by-step NLP Pipeline Lab
│       ├── knowledge_graph.html    # Interactive 2D/3D concept topology graph
│       ├── flashcards.html         # SM-2 spaced repetition flashcards
│       ├── documents.html          # My Notes (Lecture Document Upload & RAG Q&A)
│       ├── profile.html            # Student profile, badge showcases, and XP logs
│       ├── transcript.html         # Official Academic Transcript & Certificate generator
│       ├── admin.html              # Instructor & Administrator Control Center
│       ├── login.html              # Authentication login view
│       ├── register.html           # Student registration view
│       ├── forgot_password.html    # Password reset view
│       ├── subjects.html           # Curriculum subject catalog
│       ├── blueprint_modal.html    # Architecture & system blueprint inspection modal
│       └── error.html              # 404 & 500 error views
├── data/
│   ├── knowledge_base/
│   │   └── knowledge_base.json     # Curriculum concepts, canonical definitions, & keywords
│   ├── app_database.json           # File-backed persistence store for 100% offline execution
│   └── grading_config.json         # Calibrated grading weights & rubric thresholds
├── tests/
│   ├── test_system.py              # End-to-end integration test suite
│   └── __init__.py
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules
├── config.py                       # Application configuration loader
├── requirements.txt                # Python package dependencies
├── start_demo.bat                  # One-click dual-portal Windows demo launcher
└── README.md                       # Comprehensive documentation
```

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Backend Framework** | [Flask 3.0+](https://flask.palletsprojects.com/) | Modular application factory with Blueprints |
| **Natural Language Processing** | [spaCy 3.7+](https://spacy.io/) (`en_core_web_sm`) | Sentence segmentation, tokenization, lemmatization, POS tagging, NER |
| **Classical NLP & Corpora** | [NLTK 3.8+](https://www.nltk.org/) | Preprocessing, token extraction, WordNet corpora, stopwords |
| **Dense Vector Embeddings** | [Sentence-Transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) | 384-dimensional dense semantic sentence representations |
| **Machine Learning** | [Scikit-Learn 1.4+](https://scikit-learn.org/) | TF-IDF vectorization, Cosine similarity, Logistic Regression intent classifier |
| **Deep Learning Backend** | [PyTorch 2.2+](https://pytorch.org/) | Tensor compute backend powering Sentence-Transformers |
| **Generative LLM Adapter** | Google Gemini / OpenAI / Ollama | Pedagogical answer synthesis with resilient fallback engine |
| **Database & Storage** | MongoDB + Thread-Safe JSON Store | Dual-mode persistence: MongoDB client with automatic local JSON fallback |
| **Frontend Styling** | [Bootstrap 5.3](https://getbootstrap.com/) + Custom CSS | Responsive, accessible modern EdTech interface with Dark/Light modes |
| **Data Visualization** | [Chart.js 4.4+](https://www.chartjs.org/) | Radar charts, mastery breakdown bars, and learning trajectory curves |
| **Iconography** | [FontAwesome 6.4](https://fontawesome.com/) | Academic and developer UI iconography |
| **Testing** | [pytest 8.0+](https://docs.pytest.org/) | Comprehensive integration and regression test suite |

---

## ⚡ Quickstart & Installation

### 1. Prerequisites
- **Python 3.11** or higher installed.
- **Git** installed on your system.

### 2. Clone the Repository
```bash
git clone https://github.com/Vishv05/TalentLens-NLP-.git
cd TalentLens-NLP-
```

### 3. Set Up a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Download the spaCy Model & NLTK Data
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt'); nltk.download('punkt_tab')"
```

### 6. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```

Open `.env` and configure your preferences:
```env
# Database Settings (MongoDB is optional; the app seamlessly uses local JSON fallback if offline)
MONGO_URI=mongodb://localhost:27017/ai_tutor_system
SECRET_KEY=talentlens-secret-key-replace-in-production

# Generative AI Provider (gemini | openai | ollama | fallback)
LLM_PROVIDER=gemini
LLM_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash

# NLP Model Configuration
SPACY_MODEL=en_core_web_sm
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```
> [!NOTE]
> Even without an external LLM API key, TalentLens functions out-of-the-box using its built-in rule-based and knowledge-base fallback synthesizer!

---

## 🚀 Running the Application

### Option A: One-Click Demo Launcher (Windows)
Double-click `start_demo.bat` or run:
```cmd
.\start_demo.bat
```
This automatically boots both portals in separate, configured console windows:
- 🎓 **Student Portal**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- 🧑‍🏫 **Instructor / Admin Portal**: [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

### Option B: Manual Command-Line Launch

**Launch the Student Portal:**
```bash
# Terminal 1
python backend/app.py --port 5000
```
Navigate to: **`http://127.0.0.1:5000`**

**Launch the Instructor / Admin Portal:**
```bash
# Terminal 2
python backend/admin_app.py --port 5001
```
Navigate to: **`http://127.0.0.1:5001`**

---

## 🔐 Default Demo Accounts

The database comes pre-seeded with sample users for academic demonstrations:

| Portal | Role | Email | Password | Access Scope |
|---|---|---|---|---|
| **Student Hub** (`:5000`) | Student | `student@gmail.com` | `password123` | AI Chat, Quizzes, Viva, Feynman, Notes RAG, Transcript |
| **Instructor Hub** (`:5001`) | Administrator / Instructor | `admin@gmail.com` | `admin123` | Cohort Telemetry, Rubric Sliders, Knowledge CMS, Question Studio |

*(You can also register any new student account via `/register` at any time.)*

---

## 📡 RESTful API Reference

TalentLens provides a modular, RESTful API across its functional subsystems:

### 1. Natural Language Processing & Tutoring
- `POST /api/tutor/ask` — Ask the AI Tutor a question; returns pedagogical answer and full NLP inspection metadata.
- `POST /api/tutor/nlp-analysis` — Standalone endpoint returning tokenization, lemmatization, POS tags, and NER entities for any arbitrary text.
- `GET /api/pipeline/analyze?text=...` — Returns step-by-step pipeline transformations for the visualizer.

### 2. Practice Quizzes & Short Answer Evaluation
- `GET /api/quiz/topics?subject=...` — Retrieve available quiz topics for a subject.
- `POST /api/quiz/generate` — Generate an adaptive quiz for a subject and topic.
- `POST /api/quiz/submit` — Submit an answer for hybrid multi-criteria grading (semantic similarity + keyword coverage).
- `GET /api/quiz/results/<quiz_id>` — Fetch comprehensive scorecard and diagnostic feedback.

### 3. Oral Viva Voce & Feynman Teach-Back
- `GET /api/viva/topics` — List topics available for mock oral defense.
- `POST /api/viva/question` — Generate an oral defense question by difficulty and topic.
- `POST /api/viva/evaluate` — Evaluate the student's defense against expected keywords and semantic standards.
- `GET /api/feynman/topics` — List available topics for the Feynman Teach-Back challenge.
- `POST /api/feynman/evaluate` — Analyze a student explanation for analogies, circularity, and technical jargon.

### 4. Spaced Repetition & Flashcards
- `GET /api/flashcards/decks` — Fetch curriculum flashcard decks.
- `GET /api/spaced-repetition/cards/due` — Get cards scheduled for review via the SM-2 algorithm.
- `POST /api/spaced-repetition/review` — Record user review quality (`0-5`) and update repetition intervals.

### 5. Document Notes RAG
- `POST /api/documents/upload` — Upload lecture notes or PDFs for sentence chunking and vector indexing.
- `GET /api/documents/list` — Retrieve indexed documents for the active student.
- `POST /api/documents/search` — Perform dense cosine similarity search over personal uploaded notes.

### 6. Instructor Telemetry & Configuration
- `GET /api/admin/cohort-stats` — Fetch aggregate student performance metrics and mastery averages.
- `GET /api/admin/grading-config` — Retrieve current hybrid grading weights and thresholds.
- `POST /api/admin/grading-config` — Dynamically update semantic vs. keyword weights and pass/distinction thresholds.

---

## 🧪 Automated Testing

TalentLens includes an automated test suite verifying linguistic preprocessing, intent classification, topic detection, semantic similarity, short-answer grading, and end-to-end API flows:

```bash
pytest tests/test_system.py -v
```

**Test Coverage Areas:**
- `test_nlp_preprocessing`: spaCy tokenization, lemmatization, and POS tagging.
- `test_intent_detection`: TF-IDF classifier verification across definition, explanation, and quiz generation intents.
- `test_topic_detection`: Accurate subject mapping across NLP and Machine Learning queries.
- `test_semantic_similarity`: Cosine distance and keyword coverage calculations.
- `test_short_answer_evaluation`: Evaluation of student responses against expected benchmarks.
- `test_auth_and_tutor_api_flow`: Complete authentication, tutor interaction, and quiz submission lifecycle.

---

## 🔬 Academic Viva Voce & Presentation Guide

When presenting this project during an academic viva or evaluation:

1. **Demonstrate the Academic NLP Inspection Panel**:
   - Open `/chat`, ask: *"What is the difference between stemming and lemmatization?"*
   - Direct attention to the right-hand panel displaying detected intent (`ASK_COMPARISON`), POS tags, extracted noun chunks, and vector cosine match percentage.
2. **Demonstrate Hybrid Short Answer Grading**:
   - Open `/quiz`, take an NLP quiz, and provide a short-answer response.
   - Show how the system rewards semantic equivalence rather than requiring verbatim phrase copying.
3. **Showcase the Feynman Teach-Back Studio**:
   - Open `/teach-back`, pick a topic (e.g., *Overfitting*), and explain it using an analogy (*"It's like a student memorizing practice exam answers instead of learning principles"*).
   - Point out how the NLP analyzer detects the analogy marker and awards an analogy bonus while checking for circular definitions.
4. **Demonstrate Live Rubric Calibration**:
   - Open the Instructor Portal at `:5001`, navigate to **Rubrics & Models**, adjust the **Semantic Weight** slider from `65%` to `80%`, and show how changes persist to `data/grading_config.json` in real time.

---

## 📄 License & Attribution

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details. Developed for academic research, personalized education, and computational linguistics demonstration.
