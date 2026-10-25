from typing import List, Dict, Any
from backend.services.knowledge_service import get_knowledge_service

class FlashcardService:
    """
    Generates Q&A flip flashcards from knowledge base items and key takeaways.
    """

    def generate_flashcards(self, subject: str = "All") -> List[Dict[str, Any]]:
        kb_service = get_knowledge_service()
        items = kb_service.knowledge_items

        cards = []
        card_id = 1

        for item in items:
            item_subject = item.get("subject", "General")
            if subject != "All" and item_subject != subject:
                continue

            topic = item.get("topic", "Concept")
            title = item.get("title", topic)
            definition = item.get("definition", "")
            explanation = item.get("explanation", "")
            example = item.get("example", "")
            points = item.get("important_points", [])

            # Card 1: Definition Card
            cards.append({
                "id": card_id,
                "subject": item_subject,
                "topic": topic,
                "front": f"What is {title}?",
                "back": definition,
                "category": "Definition"
            })
            card_id += 1

            # Card 2: Practical Application / Example
            if example:
                cards.append({
                    "id": card_id,
                    "subject": item_subject,
                    "topic": topic,
                    "front": f"Give a practical example of {topic}.",
                    "back": example,
                    "category": "Practical Example"
                })
                card_id += 1

            # Card 3: Key Points
            if points:
                cards.append({
                    "id": card_id,
                    "subject": item_subject,
                    "topic": topic,
                    "front": f"What are the main key takeaways for {topic}?",
                    "back": " • " + "\n • ".join(points),
                    "category": "Key Points"
                })
                card_id += 1

        return cards

_flashcard_service = FlashcardService()

def get_flashcard_service():
    return _flashcard_service
