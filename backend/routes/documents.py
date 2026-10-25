import os
from flask import Blueprint, request, jsonify, session
from backend.services.pdf_rag_service import get_document_rag_service

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")

@documents_bp.route("/upload", methods=["POST"])
def upload_document():
    user_id = session.get("user_id", "guest_user")
    rag_service = get_document_rag_service()

    # Support both JSON payload and multipart form / file upload
    if request.is_json:
        data = request.get_json() or {}
        title = data.get("title", "My Class Notes").strip()
        raw_text = data.get("text", "").strip()
    else:
        title = request.form.get("title", "My Class Notes").strip()
        raw_text = request.form.get("text", "").strip()
        
        # Check if a file was uploaded
        if "file" in request.files:
            uploaded_file = request.files["file"]
            if uploaded_file and uploaded_file.filename:
                file_title = uploaded_file.filename
                if not title:
                    title = file_title
                try:
                    file_bytes = uploaded_file.read()
                    if uploaded_file.filename.lower().endswith(".pdf"):
                        import io
                        import pypdf
                        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                        pages_text = []
                        for i, page in enumerate(reader.pages):
                            txt = page.extract_text() or ""
                            if txt.strip():
                                pages_text.append(f"[Page {i+1}]\n{txt.strip()}")
                        extracted_text = "\n\n".join(pages_text)
                    else:
                        try:
                            extracted_text = file_bytes.decode("utf-8")
                        except UnicodeDecodeError:
                            extracted_text = file_bytes.decode("latin-1", errors="ignore")

                    if extracted_text.strip():
                        raw_text = (raw_text + "\n" + extracted_text).strip() if raw_text else extracted_text.strip()
                except Exception as e:
                    return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

    if not raw_text:
        return jsonify({"error": "Document text or valid file content cannot be empty."}), 400

    try:
        result = rag_service.process_and_index_text(user_id, title, raw_text)
        return jsonify({
            "message": "Document indexed successfully into continuous vector store!",
            "doc": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@documents_bp.route("/search", methods=["POST"])
def search_documents():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty."}), 400

    user_id = session.get("user_id", "guest_user")
    rag_service = get_document_rag_service()
    results = rag_service.search_user_documents(user_id, query, top_k=5)
    return jsonify({"query": query, "results": results, "total_matches": len(results)})

@documents_bp.route("/list", methods=["GET"])
def list_documents():
    user_id = session.get("user_id", "guest_user")
    rag_service = get_document_rag_service()
    docs = rag_service.list_user_documents(user_id)
    return jsonify({"documents": docs, "total": len(docs)})

@documents_bp.route("/delete/<doc_id>", methods=["DELETE", "POST"])
def delete_document(doc_id):
    user_id = session.get("user_id", "guest_user")
    rag_service = get_document_rag_service()
    success = rag_service.delete_user_document(user_id, doc_id)
    if success:
        return jsonify({"message": "Document deleted successfully."})
    return jsonify({"error": "Document not found or already deleted."}), 404
