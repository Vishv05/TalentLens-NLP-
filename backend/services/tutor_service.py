from datetime import datetime, timezone
from typing import Dict, Any, Optional
from backend.nlp.preprocessing import analyze_text
from backend.nlp.intent_classifier import detect_intent
from backend.nlp.topic_classifier import detect_topic
from backend.services.knowledge_service import get_knowledge_service
from backend.services.pdf_rag_service import get_document_rag_service
from backend.services.llm_service import get_llm_service
from backend.utils.db import get_db

class TutorService:
    def process_student_question(self, user_id: str, question: str, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        # 1. NLP Preprocessing & Linguistic Analysis
        nlp_analysis = analyze_text(question)

        # 2. Intent Detection
        intent_res = detect_intent(question)
        intent = intent_res.get("intent", "GENERAL_QUERY")

        # 3. Topic Detection
        topic_res = detect_topic(question)
        subject = topic_res.get("subject", "Natural Language Processing")
        topic = topic_res.get("topic", "General")

        # 4. Semantic Search & Knowledge Retrieval from Knowledge Base
        kb_service = get_knowledge_service()
        search_results = kb_service.search(question, top_k=1)
        raw_kb = search_results[0] if search_results else None
        similarity_score = raw_kb.get("similarity_score", 0.0) if raw_kb else 0.0
        
        # Only use knowledge base item if vector similarity score >= 40.0%
        retrieved_kb = raw_kb if similarity_score >= 40.0 else None

        # 4b. Also search Student's Custom Uploaded Document Notes (RAG)
        doc_rag = get_document_rag_service()
        user_doc_matches = doc_rag.search_user_documents(user_id, question, top_k=1)
        top_user_doc = user_doc_matches[0] if user_doc_matches else None
        
        # If student's custom notes have strong similarity (>= 45%), blend it in
        if top_user_doc and top_user_doc.get("similarity_score", 0) >= 45.0:
            if not retrieved_kb:
                retrieved_kb = {
                    "title": f"Student Note: {top_user_doc.get('doc_title')}",
                    "definition": top_user_doc.get("chunk_text"),
                    "explanation": f"From your uploaded lecture note '{top_user_doc.get('doc_title')}': {top_user_doc.get('chunk_text')}",
                    "example": "",
                    "important_points": ["Referenced from student's indexed lecture notes."],
                    "similarity_score": top_user_doc.get("similarity_score", 0)
                }

        # 5. AI Response Generation
        llm_service = get_llm_service()
        ai_response = llm_service.generate_response(
            student_question=question,
            retrieved_knowledge=retrieved_kb,
            intent=intent,
            topic=topic
        )

        # Build complete NLP payload for demonstration panel & record saving
        full_nlp_payload = {
            "tokens": nlp_analysis.get("tokens", []),
            "lemmas": nlp_analysis.get("lemmas", []),
            "pos_tags": nlp_analysis.get("pos_tags", []),
            "entities": nlp_analysis.get("entities", []),
            "stopwords": nlp_analysis.get("stopwords", []),
            "intent": intent,
            "intent_confidence": intent_res.get("confidence", 0.0),
            "subject": subject,
            "topic": topic,
            "similarity_score": similarity_score,
            "retrieved_concept": retrieved_kb.get("title") if retrieved_kb else None,
            "user_notes_match": top_user_doc.get("doc_title") if (top_user_doc and top_user_doc.get("similarity_score", 0) >= 45.0) else None
        }

        # 6. Save Conversation to Database
        db = get_db()
        conv_doc = {
            "user_id": user_id,
            "conversation_id": conversation_id or "default_session",
            "user_question": question,
            "ai_response": ai_response,
            "subject": subject,
            "topic": topic,
            "intent": intent,
            "nlp_analysis": full_nlp_payload,
            "timestamp": datetime.now(timezone.utc)
        }
        db.conversations.insert_one(conv_doc)

        return {
            "question": question,
            "answer": ai_response,
            "subject": subject,
            "topic": topic,
            "intent": intent,
            "similarity_score": similarity_score,
            "nlp_analysis": full_nlp_payload
        }

_tutor_service = TutorService()

def get_tutor_service():
    return _tutor_service
