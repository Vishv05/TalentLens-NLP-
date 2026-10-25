import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from backend.utils.db import get_db

SUBJECT_TOPIC_MAPPING = {
    "Natural Language Processing": [
        "Tokenization", "Lemmatization", "TF-IDF", "POS Tagging", "Named Entity Recognition", "Word Embeddings", "Transformers", "BERT"
    ],
    "Machine Learning": [
        "Overfitting", "Supervised Learning", "Neural Networks", "Evaluation Metrics"
    ],
    "Database Management Systems": [
        "Normalization", "ACID Properties", "SQL Querying"
    ],
    "Python Programming": [
        "Data Structures", "OOP Concepts", "Time & Space Complexity"
    ]
}

QUIZ_QUESTION_BANK = {
    "Tokenization": [
        {
            "id": "q_tok_1",
            "type": "mcq",
            "question": "What is the primary objective of tokenization in an NLP pipeline?",
            "options": [
                "To translate text into another language",
                "To break raw text into smaller units like words or subwords",
                "To remove all verbs from a sentence",
                "To convert audio signals to text"
            ],
            "correct_answer": "To break raw text into smaller units like words or subwords",
            "explanation": "Tokenization breaks a sequence of text into pieces called tokens."
        },
        {
            "id": "q_tok_2",
            "type": "true_false",
            "question": "True or False: Lemmatization always produces valid dictionary words, whereas stemming may produce non-words.",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Lemmatization uses vocabulary dictionaries and morphological context to generate valid lemmas."
        },
        {
            "id": "q_tok_3",
            "type": "short_answer",
            "question": "Define what a token is in natural language processing.",
            "correct_answer": "A token is a meaningful unit of text, such as a word, character, or subword, generated during tokenization.",
            "explanation": "Tokens serve as the fundamental input units for subsequent vectorization and modeling."
        }
    ],
    "Lemmatization": [
        {
            "id": "q_lem_1",
            "type": "mcq",
            "question": "How does lemmatization differ fundamentally from stemming?",
            "options": [
                "Lemmatization uses morphological dictionaries to produce valid dictionary words, while stemming uses rule heuristics.",
                "Stemming is slower and requires POS tagging.",
                "Lemmatization only works on numbers.",
                "Stemming always yields valid dictionary root words."
            ],
            "correct_answer": "Lemmatization uses morphological dictionaries to produce valid dictionary words, while stemming uses rule heuristics.",
            "explanation": "Lemmatization considers vocabulary lookup and Part-of-Speech context."
        },
        {
            "id": "q_lem_2",
            "type": "true_false",
            "question": "True or False: The lemma of 'better' when tagged as an adjective is 'good'.",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "Lemmatization correctly resolves irregular adjective comparative forms to their dictionary base."
        },
        {
            "id": "q_lem_3",
            "type": "short_answer",
            "question": "What is the lemma of the inflected word 'running' when tagged as a verb?",
            "correct_answer": "The lemma of 'running' as a verb is 'run'.",
            "explanation": "Lemmatization converts inflected verb forms back to their base infinitive form."
        }
    ],
    "TF-IDF": [
        {
            "id": "q_tfidf_1",
            "type": "mcq",
            "question": "In TF-IDF, what does Inverse Document Frequency (IDF) measure?",
            "options": [
                "How often a word appears in a single document",
                "How rare or common a word is across the entire corpus",
                "The total character length of a document",
                "The grammatical correct weight of a word"
            ],
            "correct_answer": "How rare or common a word is across the entire corpus",
            "explanation": "IDF penalizes common stop words and rewards unique topical terms."
        },
        {
            "id": "q_tfidf_2",
            "type": "true_false",
            "question": "True or False: If a word appears in every single document in a corpus, its IDF value will be close to 0.",
            "options": ["True", "False"],
            "correct_answer": "True",
            "explanation": "log(N/N) = log(1) = 0, giving no weight to ubiquitous terms."
        },
        {
            "id": "q_tfidf_3",
            "type": "short_answer",
            "question": "Why are common words like 'the' or 'is' given a low weight in TF-IDF?",
            "correct_answer": "Common words appear in almost every document, resulting in a low IDF score near zero.",
            "explanation": "Words appearing in all documents carry low informative power."
        }
    ],
    "POS Tagging": [
        {
            "id": "q_pos_1",
            "type": "mcq",
            "question": "In Penn Treebank POS tagging, what does the tag 'NN' represent?",
            "options": [
                "Noun, singular or mass",
                "Personal Pronoun",
                "Adjective",
                "Verb base form"
            ],
            "correct_answer": "Noun, singular or mass",
            "explanation": "NN represents singular nouns, NNS represents plural nouns, and NNP represents proper nouns."
        },
        {
            "id": "q_pos_2",
            "type": "short_answer",
            "question": "Explain why Part-of-Speech tagging is necessary for accurate lemmatization.",
            "correct_answer": "POS tagging determines whether a word is used as a noun, verb, or adjective, allowing the lemmatizer to choose the correct dictionary base form.",
            "explanation": "For example, 'meeting' can be a noun (lemma: meeting) or a verb (lemma: meet)."
        }
    ],
    "Named Entity Recognition": [
        {
            "id": "q_ner_1",
            "type": "mcq",
            "question": "Which of the following is NOT a standard named entity category in NLP?",
            "options": [
                "Prepositional Phrase (PP)",
                "Geopolitical Entity (GPE)",
                "Person (PERSON)",
                "Organization (ORG)"
            ],
            "correct_answer": "Prepositional Phrase (PP)",
            "explanation": "Prepositional phrase is a syntactic phrase constituent, not a named entity category."
        },
        {
            "id": "q_ner_2",
            "type": "short_answer",
            "question": "What is the primary role of Named Entity Recognition (NER) in information extraction?",
            "correct_answer": "NER identifies and categorizes key real-world entities such as people, organizations, locations, and dates from unstructured text.",
            "explanation": "NER converts unstructured text into structured facts for knowledge graphs and search engines."
        }
    ],
    "Word Embeddings": [
        {
            "id": "q_we_1",
            "type": "mcq",
            "question": "Which of the following is a main advantage of dense Word Embeddings over One-Hot Encoding?",
            "options": [
                "Word embeddings capture semantic similarities between words in continuous vector space.",
                "Word embeddings increase vector dimensions to infinity.",
                "One-Hot encoding represents semantic context better.",
                "Word embeddings cannot handle synonyms."
            ],
            "correct_answer": "Word embeddings capture semantic similarities between words in continuous vector space.",
            "explanation": "Dense embeddings map semantically similar terms close together in vector space."
        },
        {
            "id": "q_we_2",
            "type": "short_answer",
            "question": "Explain the famous semantic vector arithmetic equation: Vector('King') - Vector('Man') + Vector('Woman').",
            "correct_answer": "In dense embedding spaces like Word2Vec, this vector arithmetic yields a vector closest to Vector('Queen'), demonstrating semantic gender analogies.",
            "explanation": "Continuous word vectors capture relational and semantic concepts."
        }
    ],
    "Transformers": [
        {
            "id": "q_trans_1",
            "type": "mcq",
            "question": "What core mechanism enables Transformer models to process input text in parallel?",
            "options": [
                "Multi-Head Self-Attention",
                "Recurrent Hidden State Loops",
                "Convolutional Stride Pooling",
                "Manual Token Filtering"
            ],
            "correct_answer": "Multi-Head Self-Attention",
            "explanation": "Self-attention computes dynamic weights between all word pairs simultaneously."
        },
        {
            "id": "q_trans_2",
            "type": "short_answer",
            "question": "Why did Transformers replace traditional RNNs and LSTMs for large language modeling?",
            "correct_answer": "Transformers eliminate sequential token-by-token recurrence, allowing full parallelization across GPUs and effectively capturing long-range dependencies.",
            "explanation": "Self-attention processes all tokens simultaneously, overcoming vanishing gradient and bottleneck issues of RNNs."
        }
    ],
    "BERT": [
        {
            "id": "q_bert_1",
            "type": "mcq",
            "question": "What pre-training objective in BERT involves hiding random words and training the model to predict them?",
            "options": [
                "Masked Language Modeling (MLM)",
                "Causal Language Modeling",
                "Next Sentence Prediction",
                "Contrastive Representation Learning"
            ],
            "correct_answer": "Masked Language Modeling (MLM)",
            "explanation": "BERT masks 15% of tokens in the input and uses bidirectional context to predict the masked tokens."
        },
        {
            "id": "q_bert_2",
            "type": "short_answer",
            "question": "How do contextual embeddings from BERT differ from static embeddings like Word2Vec?",
            "correct_answer": "BERT generates dynamic embeddings where the same word has different vector representations depending on surrounding sentence context, whereas Word2Vec assigns a single static vector per word.",
            "explanation": "BERT disambiguates polysemous words like 'bank' (river bank vs financial bank)."
        }
    ],
    "Overfitting": [
        {
            "id": "q_of_1",
            "type": "mcq",
            "question": "What is a common symptom of model overfitting in Machine Learning?",
            "options": [
                "High training accuracy but low validation/testing accuracy",
                "Low training accuracy and high validation accuracy",
                "Equal performance across training and validation data",
                "Inability to train for more than 1 epoch"
            ],
            "correct_answer": "High training accuracy but low validation/testing accuracy",
            "explanation": "Overfitting occurs when a model memorizes training noise and fails to generalize."
        },
        {
            "id": "q_of_2",
            "type": "short_answer",
            "question": "Name two techniques used to prevent overfitting in machine learning models.",
            "correct_answer": "Regularization (L1/L2), Cross-validation, Dropout, Early stopping, or simplifying the model architecture.",
            "explanation": "Regularization penalizes large weights and cross-validation evaluates generalization."
        }
    ],
    "Supervised Learning": [
        {
            "id": "q_sup_1",
            "type": "mcq",
            "question": "Which of the following is an example of an Unsupervised Learning task?",
            "options": [
                "K-Means Customer Segmentation",
                "House price prediction using Linear Regression",
                "Email Spam Detection with Logistic Regression",
                "Image classification into Cat or Dog"
            ],
            "correct_answer": "K-Means Customer Segmentation",
            "explanation": "K-Means clusters unlabeled data points without predefined ground-truth target labels."
        },
        {
            "id": "q_sup_2",
            "type": "short_answer",
            "question": "What is the primary difference between Classification and Regression in Supervised Learning?",
            "correct_answer": "Classification predicts discrete categorical labels, whereas Regression predicts continuous numerical values.",
            "explanation": "Classification answers 'which category' while Regression answers 'how much'."
        }
    ],
    "Neural Networks": [
        {
            "id": "q_nn_1",
            "type": "mcq",
            "question": "Why are non-linear activation functions (like ReLU) essential in deep neural networks?",
            "options": [
                "Without non-linear activation, multi-layer networks collapse mathematically into a single linear transformation.",
                "They prevent inputs from being converted to floating point numbers.",
                "They force all weights to remain zero during backpropagation.",
                "They double the dataset size."
            ],
            "correct_answer": "Without non-linear activation, multi-layer networks collapse mathematically into a single linear transformation.",
            "explanation": "Non-linearities allow neural networks to approximate complex non-linear functions."
        },
        {
            "id": "q_nn_2",
            "type": "short_answer",
            "question": "What is the purpose of Backpropagation in neural network training?",
            "correct_answer": "Backpropagation computes the gradient of the loss function with respect to each weight using the chain rule, enabling gradient descent to update weights and minimize error.",
            "explanation": "Backprop efficiently propagates errors backwards through network layers."
        }
    ],
    "Evaluation Metrics": [
        {
            "id": "q_met_1",
            "type": "mcq",
            "question": "What is the formula for Precision in binary classification?",
            "options": [
                "True Positives / (True Positives + False Positives)",
                "True Positives / (True Positives + False Negatives)",
                "(True Positives + True Negatives) / Total Samples",
                "True Negatives / (True Negatives + False Positives)"
            ],
            "correct_answer": "True Positives / (True Positives + False Positives)",
            "explanation": "Precision measures the proportion of positive identifications that were actually correct."
        },
        {
            "id": "q_met_2",
            "type": "short_answer",
            "question": "Why is F1-Score preferred over simple Accuracy when evaluating imbalanced datasets?",
            "correct_answer": "Accuracy can appear deceptively high by predicting only the majority class, while F1-Score calculates the harmonic mean of Precision and Recall, balancing both false positives and false negatives.",
            "explanation": "In rare disease detection (1% positive), a naive model predicting 100% negative has 99% accuracy but 0 F1-score."
        }
    ],
    "Normalization": [
        {
            "id": "q_norm_1",
            "type": "mcq",
            "question": "Which Normal Form requires attributes to hold atomic values and row uniqueness?",
            "options": ["First Normal Form (1NF)", "Second Normal Form (2NF)", "Third Normal Form (3NF)", "BCNF"],
            "correct_answer": "First Normal Form (1NF)",
            "explanation": "1NF enforces atomicity of data fields."
        },
        {
            "id": "q_norm_2",
            "type": "short_answer",
            "question": "What primary database problems does normalization resolve?",
            "correct_answer": "Normalization eliminates data redundancy and prevents insertion, update, and deletion anomalies.",
            "explanation": "Organizing data into structured relational tables protects data integrity."
        }
    ],
    "ACID Properties": [
        {
            "id": "q_acid_1",
            "type": "mcq",
            "question": "Which ACID property guarantees that if a system crashes after a transaction commits, the changes remain permanent?",
            "options": [
                "Durability",
                "Atomicity",
                "Consistency",
                "Isolation"
            ],
            "correct_answer": "Durability",
            "explanation": "Durability guarantees committed transactions survive system failures via logs on non-volatile storage."
        },
        {
            "id": "q_acid_2",
            "type": "short_answer",
            "question": "Explain the Atomicity property of database transactions with an example.",
            "correct_answer": "Atomicity ensures all operations in a transaction either completely succeed or completely roll back, such as ensuring a bank transfer debits the sender and credits the recipient together.",
            "explanation": "Transactions cannot exist in a partial state."
        }
    ],
    "SQL Querying": [
        {
            "id": "q_sql_1",
            "type": "mcq",
            "question": "What is the key difference between the WHERE clause and the HAVING clause in SQL?",
            "options": [
                "WHERE filters rows before grouping; HAVING filters aggregated groups after GROUP BY.",
                "HAVING filters individual rows before grouping; WHERE filters groups.",
                "WHERE can only be used with numeric data.",
                "HAVING cannot be used with aggregate functions like COUNT() or SUM()."
            ],
            "correct_answer": "WHERE filters rows before grouping; HAVING filters aggregated groups after GROUP BY.",
            "explanation": "WHERE filters source rows, while HAVING evaluates aggregate group criteria."
        },
        {
            "id": "q_sql_2",
            "type": "short_answer",
            "question": "How does an INNER JOIN differ from a LEFT OUTER JOIN?",
            "correct_answer": "An INNER JOIN returns only records with matching keys in both tables, whereas a LEFT JOIN returns all rows from the left table and matching rows or NULLs from the right table.",
            "explanation": "LEFT JOIN preserves all left-side rows regardless of right-side matches."
        }
    ],
    "Data Structures": [
        {
            "id": "q_ds_1",
            "type": "mcq",
            "question": "What is the primary difference between a Python List and a Python Tuple?",
            "options": [
                "Lists are mutable, whereas Tuples are immutable.",
                "Tuples can hold elements, but Lists cannot.",
                "Lists use key-value pairs, whereas Tuples use indices.",
                "Tuples are always slower than Lists."
            ],
            "correct_answer": "Lists are mutable, whereas Tuples are immutable.",
            "explanation": "Lists allow in-place modification (append, remove) while tuples cannot be modified once created."
        },
        {
            "id": "q_ds_2",
            "type": "short_answer",
            "question": "Why do Python Dictionaries provide average O(1) time complexity for key lookups?",
            "correct_answer": "Python dictionaries are implemented using Hash Tables, which compute a hash index from the key to access memory directly in constant average time.",
            "explanation": "Hash mapping provides near-instantaneous key retrieval."
        }
    ],
    "OOP Concepts": [
        {
            "id": "q_oop_1",
            "type": "mcq",
            "question": "Which OOP principle allows a subclass to provide a specific implementation of a method already provided by its parent class?",
            "options": [
                "Polymorphism (Method Overriding)",
                "Encapsulation",
                "Multiple Inheritance",
                "Data Hiding"
            ],
            "correct_answer": "Polymorphism (Method Overriding)",
            "explanation": "Polymorphism allows child classes to override methods to specialize behavior."
        },
        {
            "id": "q_oop_2",
            "type": "short_answer",
            "question": "What is the purpose of the `super().__init__()` call in a Python subclass?",
            "correct_answer": "It invokes the constructor of the parent superclass, ensuring base class attributes are properly initialized before child attributes are assigned.",
            "explanation": "`super()` delegates method calls to the parent class hierarchy."
        }
    ],
    "Time & Space Complexity": [
        {
            "id": "q_comp_1",
            "type": "mcq",
            "question": "What is the worst-case time complexity of Binary Search on a sorted array of size n?",
            "options": [
                "O(log n)",
                "O(n)",
                "O(n log n)",
                "O(1)"
            ],
            "correct_answer": "O(log n)",
            "explanation": "Binary search halves the search space at every comparison step, giving logarithmic time."
        },
        {
            "id": "q_comp_2",
            "type": "short_answer",
            "question": "Why is MergeSort guaranteed to run in O(n log n) time in all cases (best, average, worst)?",
            "correct_answer": "MergeSort always divides the array in half at log(n) levels of recursion and requires linear O(n) work to merge the sorted halves at each level.",
            "explanation": "The recursion tree always has height log(n) and width n work."
        }
    ]
}

class QuizService:
    def get_topics_for_subject(self, subject: str) -> List[str]:
        return SUBJECT_TOPIC_MAPPING.get(subject, SUBJECT_TOPIC_MAPPING["Natural Language Processing"])

    def generate_quiz(self, user_id: str, subject: str, topic: str, difficulty: str = "Medium", count: int = 3) -> Dict[str, Any]:
        # Topic lookup or fallback to first topic of the subject
        bank = QUIZ_QUESTION_BANK.get(topic)
        if not bank:
            topics_in_subj = self.get_topics_for_subject(subject)
            for t in topics_in_subj:
                if t in QUIZ_QUESTION_BANK:
                    bank = QUIZ_QUESTION_BANK[t]
                    topic = t
                    break
        if not bank:
            bank = QUIZ_QUESTION_BANK["Tokenization"]
            topic = "Tokenization"

        selected_questions = bank[:count]

        quiz_id = str(uuid.uuid4())
        quiz_doc = {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "questions": selected_questions,
            "user_answers": [],
            "score": 0.0,
            "timestamp": datetime.now(timezone.utc)
        }

        db = get_db()
        db.quizzes.insert_one(quiz_doc)

        return {
            "quiz_id": quiz_id,
            "subject": subject,
            "topic": topic,
            "difficulty": difficulty,
            "questions": [
                {
                    "id": q["id"],
                    "type": q["type"],
                    "question": q["question"],
                    "options": q.get("options", [])
                }
                for q in selected_questions
            ]
        }

_quiz_service = QuizService()

def get_quiz_service():
    return _quiz_service
