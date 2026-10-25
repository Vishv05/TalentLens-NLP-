from typing import Dict, Any, List
from backend.services.knowledge_service import get_knowledge_service

class KnowledgeGraphEngine:
    """
    Generates node & edge topology for interactive D3 / Vis.js concept dependency graphs.
    """

    PREREQUISITES = [
        # NLP Track
        ("Tokenization", "Lemmatization"),
        ("Tokenization", "POS Tagging"),
        ("POS Tagging", "Named Entity Recognition"),
        ("Tokenization", "TF-IDF"),
        ("TF-IDF", "Word Embeddings"),
        ("Word Embeddings", "Transformers"),
        ("Transformers", "BERT"),

        # Machine Learning Track
        ("Supervised Learning", "Overfitting"),
        ("Supervised Learning", "Neural Networks"),
        ("Neural Networks", "Transformers"),
        ("Supervised Learning", "Evaluation Metrics"),

        # DBMS Track
        ("1NF", "2NF"),
        ("2NF", "3NF"),
        ("3NF", "BCNF"),
        ("Normalization", "SQL Querying"),
        ("ACID Properties", "SQL Querying"),

        # Python & Algorithms Track
        ("Data Structures", "OOP Concepts"),
        ("Data Structures", "Time & Space Complexity"),
        ("Time & Space Complexity", "Neural Networks")
    ]

    def get_knowledge_graph_topology(self) -> Dict[str, Any]:
        kb_service = get_knowledge_service()
        items = kb_service.knowledge_items

        nodes = []
        node_ids = set()

        for idx, item in enumerate(items):
            topic = item.get("topic", f"Topic_{idx}")
            subject = item.get("subject", "General")
            title = item.get("title", topic)
            definition = item.get("definition", "")
            if topic not in node_ids:
                node_ids.add(topic)
                nodes.append({
                    "id": topic,
                    "label": topic,
                    "title_full": title,
                    "definition": definition,
                    "subject": subject,
                    "group": subject
                })

        # Add granular normal forms
        extra_topics = [
            {"id": "1NF", "label": "1NF", "subject": "Database Management Systems", "title_full": "First Normal Form", "definition": "Ensures atomic attribute values and unique rows."},
            {"id": "2NF", "label": "2NF", "subject": "Database Management Systems", "title_full": "Second Normal Form", "definition": "In 1NF and no partial dependencies on composite keys."},
            {"id": "3NF", "label": "3NF", "subject": "Database Management Systems", "title_full": "Third Normal Form", "definition": "In 2NF and no transitive functional dependencies."},
            {"id": "BCNF", "label": "BCNF", "subject": "Database Management Systems", "title_full": "Boyce-Codd Normal Form", "definition": "Strict 3NF where every determinant is a candidate key."}
        ]
        for et in extra_topics:
            if et["id"] not in node_ids:
                node_ids.add(et["id"])
                nodes.append({
                    "id": et["id"],
                    "label": et["label"],
                    "title_full": et["title_full"],
                    "definition": et["definition"],
                    "subject": et["subject"],
                    "group": et["subject"]
                })

        edges = []
        for source, target in self.PREREQUISITES:
            if source in node_ids and target in node_ids:
                edges.append({
                    "from": source,
                    "to": target,
                    "arrows": "to",
                    "label": "prerequisite"
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }

_knowledge_graph_engine = KnowledgeGraphEngine()

def get_knowledge_graph_engine():
    return _knowledge_graph_engine
