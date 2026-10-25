import pytest
from backend.app import app
from backend.nlp.preprocessing import analyze_text
from backend.nlp.intent_classifier import detect_intent
from backend.nlp.topic_classifier import detect_topic
from backend.nlp.similarity import compute_cosine_similarity, compute_keyword_coverage
from backend.services.evaluation_service import get_answer_evaluator

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-key"
    with app.test_client() as client:
        yield client

def test_nlp_preprocessing():
    text = "Tokenization divides sentences into words."
    analysis = analyze_text(text)
    assert "tokens" in analysis
    assert "lemmas" in analysis
    assert "pos_tags" in analysis
    assert len(analysis["tokens"]) > 0

def test_intent_detection():
    intent_def = detect_intent("What is tokenization?")
    assert intent_def["intent"] == "ASK_DEFINITION"

    intent_exp = detect_intent("Explain TF-IDF step by step.")
    assert intent_exp["intent"] == "ASK_EXPLANATION"

    intent_quiz = detect_intent("Generate a quiz for me on DBMS.")
    assert intent_quiz["intent"] == "GENERATE_QUIZ"

def test_topic_detection():
    topic_nlp = detect_topic("Explain lemmatization in spaCy.")
    assert topic_nlp["subject"] == "Natural Language Processing"

    topic_ml = detect_topic("Why does my model overfit?")
    assert topic_ml["subject"] == "Machine Learning"

def test_semantic_similarity():
    sim = compute_keyword_coverage("Tokenization splits text into tokens", "Tokenization divides text into tokens")
    assert sim > 0.5

def test_short_answer_evaluation():
    evaluator = get_answer_evaluator()
    expected = "Tokenization is the process of dividing text into smaller units called tokens."
    student = "Tokenization breaks a sentence into smaller text units called tokens."

    res = evaluator.evaluate_short_answer(expected, student)
    assert res["is_correct"] is True
    assert res["score_percent"] > 70.0

def test_auth_and_tutor_api_flow(client):
    # 1. Register as Student
    reg_res = client.post("/register", data={
        "name": "Academic Student",
        "email": "student_test@example.com",
        "password": "password123"
    }, follow_redirects=True)
    assert reg_res.status_code == 200

    # Test Admin Auto-Detection on Login
    admin_login_res = client.post("/login", data={
        "email": "admin@gmail.com",
        "password": "admin123"
    }, follow_redirects=False)
    assert admin_login_res.status_code == 302
    assert "/admin" in admin_login_res.headers.get("Location", "")

    # 2. Ask Tutor API
    tutor_res = client.post("/api/tutor/ask", json={
        "question": "What is TF-IDF in Natural Language Processing?"
    })
    assert tutor_res.status_code == 200
    json_data = tutor_res.get_json()
    assert "answer" in json_data
    assert "nlp_analysis" in json_data
    assert json_data["nlp_analysis"]["intent"] in ["ASK_DEFINITION", "ASK_EXPLANATION"]

    # 3. Quiz Topics API
    topics_res = client.get("/api/quiz/topics?subject=Machine+Learning")
    assert topics_res.status_code == 200
    assert len(topics_res.get_json()["topics"]) > 0

    # 4. Generate Quiz API
    quiz_res = client.post("/api/quiz/generate", json={
        "subject": "Natural Language Processing",
        "topic": "TF-IDF"
    })
    assert quiz_res.status_code == 200
    quiz_json = quiz_res.get_json()
    assert "quiz_id" in quiz_json
    assert len(quiz_json["questions"]) > 0

    # 5. Dashboard Analytics API
    analytics_res = client.get("/api/analytics/dashboard")
    assert analytics_res.status_code == 200
    analytics_json = analytics_res.get_json()
    assert "metrics" in analytics_json
    assert "charts" in analytics_json

def test_nlp_standalone_analysis_endpoint(client):
    res = client.post("/api/tutor/nlp-analysis", json={
        "text": "Overfitting occurs when a machine learning model memorizes training noise."
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["subject"] == "Machine Learning"
    assert data["topic"] == "Overfitting"
    assert "tokens" in data
    assert "lemmas" in data
    assert "pos_tags" in data

def test_quiz_submission_and_lookup_flow(client):
    # Generate quiz
    gen_res = client.post("/api/quiz/generate", json={
        "subject": "Natural Language Processing",
        "topic": "Tokenization"
    })
    assert gen_res.status_code == 200
    quiz_data = gen_res.get_json()
    quiz_id = quiz_data["quiz_id"]

    # Submit quiz
    sub_res = client.post("/api/quiz/submit", json={
        "quiz_id": quiz_id,
        "answers": {
            "q_tok_1": "To break raw text into smaller units like words or subwords",
            "q_tok_2": "True",
            "q_tok_3": "A token is a meaningful unit of text generated during tokenization."
        }
    })
    assert sub_res.status_code == 200
    sub_data = sub_res.get_json()
    assert sub_data["overall_score_percent"] > 50.0

    # Get Quiz Details
    detail_res = client.get(f"/api/quiz/{quiz_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.get_json()
    assert detail_data["quiz_id"] == quiz_id
    assert detail_data["score"] > 50.0

def test_error_handling_routes(client):
    # Empty question
    res_empty_q = client.post("/api/tutor/ask", json={"question": ""})
    assert res_empty_q.status_code == 400

    # Invalid quiz ID submission
    res_invalid_quiz = client.post("/api/quiz/submit", json={"quiz_id": "non-existent-id"})
    assert res_invalid_quiz.status_code == 404

def test_extended_features_and_rag_suite(client):
    # 1. Gamification Profile & Status
    gam_res = client.get("/api/gamification/profile")
    assert gam_res.status_code == 200
    gam_data = gam_res.get_json()
    assert "total_xp" in gam_data
    assert "level" in gam_data

    gam_status_res = client.get("/api/gamification/status")
    assert gam_status_res.status_code == 200

    # 2. Spaced Repetition APIs (Record, Due, Flashcard-Rate)
    sr_rec_res = client.post("/api/spaced-repetition/record", json={"topic": "Tokenization", "score_percent": 95.0})
    assert sr_rec_res.status_code == 200
    sr_due_res = client.get("/api/spaced-repetition/due")
    assert sr_due_res.status_code == 200
    sr_rate_res = client.post("/api/spaced-repetition/flashcard-rate", json={"topic": "Tokenization", "rating": "easy"})
    assert sr_rate_res.status_code == 200

    # 3. Knowledge Graph Topology API
    kg_res = client.get("/api/knowledge-graph/topology")
    assert kg_res.status_code == 200
    kg_data = kg_res.get_json()
    assert "nodes" in kg_data
    assert "edges" in kg_data
    assert len(kg_data["nodes"]) >= 10

    # 4. Flashcards API
    fc_res = client.get("/api/flashcards/list?subject=All")
    assert fc_res.status_code == 200
    fc_data = fc_res.get_json()
    assert "flashcards" in fc_data
    assert fc_data["total"] >= 10

    # 5. Document RAG Upload, Search, List, and Delete API
    doc_up_res = client.post("/api/documents/upload", json={
        "title": "Unit 1 Lecture Notes",
        "text": "Tokenization is essential. Lemmatization groups inflected forms of words into dictionary lemmas. Transformers use multi-head self-attention."
    })
    assert doc_up_res.status_code == 200
    doc_id = doc_up_res.get_json()["doc"]["doc_id"]

    doc_search_res = client.post("/api/documents/search", json={"query": "What is lemmatization?"})
    assert doc_search_res.status_code == 200
    assert len(doc_search_res.get_json()["results"]) > 0

    doc_list_res = client.get("/api/documents/list")
    assert doc_list_res.status_code == 200
    assert len(doc_list_res.get_json()["documents"]) > 0

    doc_del_res = client.post(f"/api/documents/delete/{doc_id}")
    assert doc_del_res.status_code == 200

def test_admin_portal_apis(client):
    # 1. Admin Dashboard Metrics
    adm_dash_res = client.get("/api/admin/dashboard")
    assert adm_dash_res.status_code == 200
    adm_data = adm_dash_res.get_json()
    assert "metrics" in adm_data
    assert "intent_distribution" in adm_data
    assert "topic_analytics" in adm_data

    # 2. Students List
    students_res = client.get("/api/admin/students")
    assert students_res.status_code == 200
    assert "students" in students_res.get_json()

    # 3. Knowledge Base List & Add & Delete
    kb_list_res = client.get("/api/admin/knowledge/list")
    assert kb_list_res.status_code == 200
    assert "concepts" in kb_list_res.get_json()

    add_kb_res = client.post("/api/admin/knowledge/add", json={
        "subject": "Natural Language Processing",
        "topic": "Self Attention",
        "title": "Self Attention in NLP",
        "definition": "Self attention allows tokens to weigh importance of other tokens in a sequence.",
        "explanation": "Self attention computes Query, Key, and Value matrices to determine contextual relevance across all sequence tokens.",
        "example": "In 'The animal didn't cross the street because it was too tired', 'it' links to 'animal'."
    })
    assert add_kb_res.status_code == 200
    assert "published" in add_kb_res.get_json()["message"]

    # 4. Add Quiz Question
    add_q_res = client.post("/api/admin/quiz/add-question", json={
        "subject": "Natural Language Processing",
        "topic": "Self Attention",
        "question": {
            "type": "short_answer",
            "question": "What is the role of the Query, Key, and Value matrices in self-attention?",
            "correct_answer": "Query, Key, and Value matrices compute attention weights to capture token context dependencies.",
            "explanation": "Q and K calculate dot-product attention scores which weight the V matrix."
        }
    })
    assert add_q_res.status_code == 200

    # 5. Clean up added concept
    del_kb_res = client.post("/api/admin/knowledge/delete/natural_language_processing_self_attention")
    assert del_kb_res.status_code == 200

def test_viva_engine(client):
    """Test Reverse Viva question generation and oral defense evaluation."""
    q_res = client.post("/api/viva/question", json={
        "subject": "Natural Language Processing",
        "topic": "Tokenization",
        "difficulty": "Medium"
    })
    assert q_res.status_code == 200
    q_data = q_res.get_json()
    assert "question" in q_data
    assert "expected_keywords" in q_data

    eval_res = client.post("/api/viva/evaluate", json={
        "topic": "Tokenization",
        "question": q_data["question"],
        "student_answer": "Tokenization breaks a sequence of raw text down into individual tokens or subwords to enable text vectorization.",
        "expected_keywords": q_data["expected_keywords"]
    })
    assert eval_res.status_code == 200
    eval_data = eval_res.get_json()
    assert eval_data["score_percent"] > 50.0
    assert "verdict" in eval_data
    assert "followup_probe" in eval_data

def test_feynman_engine(client):
    """Test Feynman Teach-Back evaluation, readability and metaphor detection."""
    res = client.post("/api/feynman/evaluate", json={
        "topic": "Tokenization",
        "explanation": "Imagine a giant sentence made of Lego blocks. Tokenization is like pulling the Lego pieces apart into individual single bricks so we can count and color them.",
        "audience_level": "child"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["feynman_score"] > 50.0
    assert "specs_dialogue" in data
    assert len(data["analogies_found"]) > 0

def test_nlp_pipeline_stepper(client):
    """Test 6-stage NLP pipeline execution."""
    res = client.post("/api/pipeline/process", json={
        "text": "The quick brown foxes were jumping over 10 lazy dogs!"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "step1_raw" in data
    assert "step2_tokens" in data
    assert "step3_stopwords" in data
    assert "step4_pos" in data
    assert "step5_lemma_stem" in data
    assert "step6_vector" in data
    assert data["step2_tokens"]["total_tokens"] > 0
    assert data["step6_vector"]["vector_dimension"] == 384

def test_admin_curriculum_blind_spots(client):
    """Test Admin Curriculum Blind-Spot and Misconception Heatmap."""
    res = client.get("/api/admin/blind-spots")
    assert res.status_code == 200
    data = res.get_json()
    assert "summary" in data
    assert "heatmap" in data
    assert "misconception_clusters" in data
    assert "lecture_interventions" in data
    assert len(data["heatmap"]) > 0
    assert len(data["misconception_clusters"]) > 0

def test_admin_rubric_hyperparameter_studio(client):
    """Test Admin Rubric Hyperparameter Config and Simulation Sandbox."""
    cfg_get = client.get("/api/admin/rubric/config")
    assert cfg_get.status_code == 200
    assert "config" in cfg_get.get_json()

    cfg_post = client.post("/api/admin/rubric/config", json={
        "semantic_weight": 0.65,
        "keyword_weight": 0.35,
        "pass_threshold": 50.0,
        "distinction_threshold": 85.0
    })
    assert cfg_post.status_code == 200
    assert cfg_post.get_json()["config"]["semantic_weight"] == 0.65

    sim_res = client.post("/api/admin/rubric/simulate", json={
        "expected_answer": "Tokenization divides raw text into smaller tokens such as words or subwords.",
        "student_answer": "Tokenization splits text into small words or tokens."
    })
    assert sim_res.status_code == 200
    sim_data = sim_res.get_json()
    assert sim_data["final_score"] > 60.0
    assert "math_trace" in sim_data

def test_admin_student_cognitive_dna(client):
    """Test Student Cognitive DNA Profile Dossier."""
    res = client.get("/api/admin/student/test_user_id/cognitive-dna")
    assert res.status_code == 200
    data = res.get_json()
    assert "domain_mastery" in data
    assert "viva_metrics" in data
    assert "feynman_metrics" in data
    assert "memory_decay" in data
    assert len(data["memory_decay"]) > 0

def test_forgot_password_flow(client):
    """Test Forgot Password request, 6-digit OTP verification, and subsequent sign in."""
    # 1. Non-existent email should return 404
    req_bad = client.post("/api/auth/forgot-password/request", json={"email": "nonexistent_student@gmail.com"})
    assert req_bad.status_code == 404

    # 2. Existing student request code
    req_good = client.post("/api/auth/forgot-password/request", json={"email": "student@gmail.com"})
    assert req_good.status_code == 200
    res_data = req_good.get_json()
    assert res_data["success"] is True
    assert "demo_code" in res_data
    code = res_data["demo_code"]
    assert len(code) == 6

    # 3. Invalid code should fail
    verify_bad = client.post("/api/auth/forgot-password/verify-reset", json={
        "email": "student@gmail.com",
        "code": "000000",
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    })
    assert verify_bad.status_code == 400

    # 4. Mismatched passwords should fail
    verify_mismatch = client.post("/api/auth/forgot-password/verify-reset", json={
        "email": "student@gmail.com",
        "code": code,
        "new_password": "newpassword123",
        "confirm_password": "mismatchpassword123"
    })
    assert verify_mismatch.status_code == 400

    # 5. Valid code & matching password resets successfully
    verify_good = client.post("/api/auth/forgot-password/verify-reset", json={
        "email": "student@gmail.com",
        "code": code,
        "new_password": "studentresetpass123",
        "confirm_password": "studentresetpass123"
    })
    assert verify_good.status_code == 200
    assert verify_good.get_json()["success"] is True

    # 6. Verify logging in with the newly reset password
    login_res = client.post("/login", data={
        "email": "student@gmail.com",
        "password": "studentresetpass123"
    }, follow_redirects=False)
    assert login_res.status_code == 302
    assert "/dashboard" in login_res.headers.get("Location", "")

def test_favicon_endpoint(client):
    res = client.get("/favicon.ico")
    assert res.status_code == 200
    assert "image/svg+xml" in res.content_type

def test_branded_404_error_handler(client):
    res = client.get("/non-existent-page-url-xyz")
    assert res.status_code == 404
    assert b"Academic Resource Not Found" in res.data or b"404" in res.data

def test_progress_reset_endpoint(client):
    # Log in first
    client.post("/login", data={
        "email": "student@gmail.com",
        "password": "studentresetpass123"
    })
    res = client.post("/api/progress/reset")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["success"] is True
    assert "reset successfully" in json_data["message"]



