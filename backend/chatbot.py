"""HR chatbot module — Robust NLP-based Q&A (V2 Hybrid Architecture)."""

import numpy as np
import re
import random
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import data_processor

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# Global Initialization State
_faq_df = None
_word_vec = None
_char_vec = None
_sem_model = None

_word_mat = None
_char_mat = None
_sem_mat = None

# Session context memory: { session_id: {"last_category": str, "last_time": float, "last_question": str} }
_session_context = {}

# Conversational Intents (Strictly No HR Policy Knowledge)
_GREETING_PATTERNS = [
    r"^\b(hi|hello|hey|greetings|howdy)\b",
    r"^\b(good\s+(morning|afternoon|evening))\b",
]

_FAREWELL_PATTERNS = [
    r"^\b(bye|goodbye|see\s+you|cya|take\s+care)\b",
]

_THANKS_PATTERNS = [
    r"^\b(thanks|thank\s+you|appreciate\s+it|thankyou)\b",
]

_HOW_ARE_YOU_PATTERNS = [
    r"^\b(how\s+are\s+you|how\s+are\s+you\s+doing|whats\s+up|what\s+is\s+up|how\s+do\s+you\s+do)\b",
]

def _is_conversational(raw_message: str):
    """
    Check if the user input is a generic conversational greeting, farewell, or courtesy message.
    Uses normalized clean text to ensure insensitivity to case, punctuation, and whitespace.
    """
    clean_msg = data_processor.clean_text(raw_message)
    if not clean_msg:
        return None

    # Test Greetings
    for pat in _GREETING_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "Hello! How can I assist you with HR matters today?",
                "Hi there! What HR question can I answer for you?",
                "Greetings! How may I help you today?"
            ])

    # Test Farewells
    for pat in _FAREWELL_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "Goodbye! Have a great day.",
                "Take care! Feel free to reach out if you need anything else.",
                "Bye! Have a productive day."
            ])

    # Test Thanks
    for pat in _THANKS_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "You're very welcome!",
                "Happy to help!",
                "Anytime! Let me know if you have more HR questions."
            ])

    # Test How Are You
    for pat in _HOW_ARE_YOU_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "I'm just a virtual HR assistant, but I'm doing great! How can I help you today?",
                "Doing well, thank you! Ready to answer any HR policy questions you have."
            ])

    return None

def _initialize_models():
    """Load FAQ dataset and build Word TF-IDF, Char TF-IDF, and Dense Semantic embeddings."""
    global _faq_df, _word_vec, _char_vec, _sem_model
    global _word_mat, _char_mat, _sem_mat

    try:
        t0 = time.time()
        print("Initializing Chatbot NLP models...")
        _faq_df = data_processor.load_hr_faq(preprocess=True)
        questions_raw = _faq_df["question"].fillna("").tolist()
        questions_processed = _faq_df["question_processed"].fillna("").tolist()

        # 1. Word-Level TF-IDF (1-2 n-grams)
        _word_vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, lowercase=True)
        _word_mat = _word_vec.fit_transform(questions_processed)

        # 2. Character-Level TF-IDF (3-5 char n-grams) — robust to typos & spelling variations
        _char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True, lowercase=True)
        _char_mat = _char_vec.fit_transform(questions_processed)

        # 3. Dense Semantic Embeddings (Sentence Transformers)
        if SentenceTransformer:
            _sem_model = SentenceTransformer('all-MiniLM-L6-v2')
            _sem_mat = _sem_model.encode(questions_raw, convert_to_numpy=True)
        else:
            print("Warning: sentence_transformers not available. Semantic matching fallback active.")

        print(f"Chatbot initialized successfully with {len(_faq_df)} FAQs in {time.time() - t0:.2f}s")
    except Exception as e:
        print(f"Failed to initialize chatbot models: {e}")
        _faq_df = None

# Initialize models upon import
_initialize_models()

def get_chatbot_response(question: str, session_id: str = "default") -> dict:
    """
    Process user query through a 4-layer hybrid NLP pipeline and return structured response metadata.
    """
    if _faq_df is None:
        return {
            "success": False,
            "answer": "Chatbot is currently unavailable due to an initialization error.",
            "category": "Error",
            "confidence": 0.0,
            "confidence_level": "low",
            "source": "system"
        }

    raw_query = str(question or "").strip()
    if not raw_query:
        return {
            "success": False,
            "answer": "Please provide a valid question.",
            "category": "Unknown",
            "confidence": 0.0,
            "confidence_level": "low",
            "source": "system"
        }

    # Layer 1: Conversational Intent Routing
    conv_response = _is_conversational(raw_query)
    if conv_response:
        return {
            "success": True,
            "answer": conv_response,
            "category": "conversation",
            "confidence": 1.0,
            "confidence_level": "high",
            "matched_question": None,
            "source": "conversation"
        }

    # Preprocess text
    processed_q = data_processor.preprocess_text(raw_query)
    cleaned_q = data_processor.clean_text(raw_query)

    if not processed_q and not cleaned_q:
        return {
            "success": True,
            "answer": "I couldn't understand your question. Could you rephrase?",
            "category": "Unknown",
            "confidence": 0.0,
            "confidence_level": "low",
            "matched_question": None,
            "source": "fallback"
        }

    # Layer 2: Hybrid Retrieval
    word_q = _word_vec.transform([processed_q])
    char_q = _char_vec.transform([processed_q])

    sim_word = cosine_similarity(word_q, _word_mat).flatten()
    sim_char = cosine_similarity(char_q, _char_mat).flatten()

    if _sem_model is not None:
        sem_q = _sem_model.encode([cleaned_q], convert_to_numpy=True)
        sim_sem = cosine_similarity(sem_q, _sem_mat).flatten()
    else:
        sim_sem = np.zeros_like(sim_word)

    # Hybrid weights (Semantic: 65%, Word: 20%, Char: 15%)
    w_sem = 0.65 if _sem_model is not None else 0.0
    w_word = 0.20 if _sem_model is not None else 0.60
    w_char = 0.15 if _sem_model is not None else 0.40

    hybrid_scores = (w_sem * sim_sem) + (w_word * sim_word) + (w_char * sim_char)

    # Layer 3: Contextual Session Memory Boost
    ctx = _session_context.get(session_id, {})
    last_cat = ctx.get("last_category")
    last_time = ctx.get("last_time", 0)

    # Apply 15% contextual boost if query is short (<= 6 words) and last interaction was < 5 mins ago
    query_word_count = len(cleaned_q.split())
    if last_cat and (time.time() - last_time < 300) and query_word_count <= 6:
        for i, cat in enumerate(_faq_df["category"]):
            if cat == last_cat:
                hybrid_scores[i] *= 1.15

    # Layer 4: Ranking & Top-K Gap Analysis
    top_indices = np.argsort(hybrid_scores)[::-1]
    best_idx = int(top_indices[0])
    second_idx = int(top_indices[1]) if len(top_indices) > 1 else best_idx

    best_score = float(hybrid_scores[best_idx])
    second_score = float(hybrid_scores[second_idx]) if len(top_indices) > 1 else 0.0
    score_gap = best_score - second_score

    matched_cat = _faq_df.loc[best_idx, "category"]
    matched_q = _faq_df.loc[best_idx, "question"]
    matched_ans = _faq_df.loc[best_idx, "answer"]

    # Update session context
    if best_score >= 0.35:
        _session_context[session_id] = {
            "last_category": matched_cat,
            "last_time": time.time(),
            "last_question": matched_q
        }

    # Layer 5: Calibrated Confidence Thresholding
    # High Confidence: strong score (>= 0.60) or moderate score with large gap
    if best_score >= 0.60 or (best_score >= 0.52 and score_gap >= 0.15):
        level = "high"
        answer = matched_ans
        source = "hr_faq"
    # Medium Confidence: moderate score (>= 0.35)
    elif best_score >= 0.35:
        level = "medium"
        answer = f"I'm not entirely sure, but here is what I found: {matched_ans}"
        source = "hr_faq"
    # Low Confidence: weak score (< 0.35) -> Safe Fallback
    else:
        level = "low"
        answer = "I'm sorry, I don't have an answer for that in my HR database. Please contact HR directly."
        matched_cat = "Unmatched"
        matched_q = None
        source = "fallback"

    return {
        "success": True,
        "answer": answer,
        "category": matched_cat,
        "confidence": round(best_score, 4),
        "confidence_level": level,
        "matched_question": matched_q,
        "source": source,
        "scores_detail": {
            "word": round(float(sim_word[best_idx]), 4),
            "char": round(float(sim_char[best_idx]), 4),
            "semantic": round(float(sim_sem[best_idx]), 4),
            "hybrid": round(best_score, 4),
            "gap": round(score_gap, 4)
        }
    }
