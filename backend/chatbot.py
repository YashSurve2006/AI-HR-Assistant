"""HR chatbot module — Robust NLP-based Q&A (V2 Hybrid Architecture) with Resume Context Intelligence."""

import numpy as np
import re
import random
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import data_processor
import job_recommender

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

# Session context memory: { session_id: {"last_category": str, "last_time": float, "last_question": str, "resume": dict} }
_session_context = {}

def set_session_resume(session_id: str, resume_data: dict):
    """Store candidate's analyzed resume in the session context."""
    if session_id not in _session_context:
        _session_context[session_id] = {}
    _session_context[session_id]["resume"] = resume_data
    _session_context[session_id]["last_time"] = time.time()

def get_session_resume(session_id: str) -> dict:
    """Retrieve active resume data for a session."""
    return _session_context.get(session_id, {}).get("resume")

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
                "Hello! I am Lumina, your AI HR Assistant. You can ask me HR policy questions or upload your resume (PDF/DOCX) for instant ATS evaluation and job matching!",
                "Hi there! How can I assist you with HR policies, resume analysis, or career recommendations today?",
                "Greetings! Ready to help you with HR policies, resume scoring, or interview prep. What would you like to explore?"
            ])

    # Test Farewells
    for pat in _FAREWELL_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "Goodbye! Best of luck with your career goals.",
                "Take care! Feel free to upload updated resumes or ask more HR questions anytime.",
                "Bye! Have a wonderful and productive day."
            ])

    # Test Thanks
    for pat in _THANKS_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "You're very welcome! Let me know if you need more tips or policy info.",
                "Happy to help! Feel free to ask more questions.",
                "Anytime! I'm here whenever you need HR or career assistance."
            ])

    # Test How Are You
    for pat in _HOW_ARE_YOU_PATTERNS:
        if re.search(pat, clean_msg):
            return random.choice([
                "I'm running smoothly and ready to assist with your HR inquiries and resume analysis! How can I help today?",
                "Doing great, thank you! Ready to answer policy questions, check ATS scores, or recommend jobs."
            ])

    return None

def _handle_resume_intent(raw_message: str, resume: dict) -> dict:
    """Handle candidate queries regarding their uploaded resume or prompt to upload if none exists."""
    msg = raw_message.lower().strip()
    clean_msg = data_processor.clean_text(raw_message)

    # 1. Analyze / Upload Prompt (No resume uploaded yet)
    if any(k in msg for k in ["analyze my resume", "analyze resume", "upload resume", "check my ats score", "check ats score", "ats score", "rate my resume", "score my resume"]):
        if not resume:
            return {
                "success": True,
                "answer": "📄 **Upload Your Resume to Begin**\n\nTo analyze your resume and calculate your comprehensive ATS score, please upload your resume (**PDF or DOCX**) using the attachment button (📎) below or simply **drag & drop** it directly into this chat.\n\nI will instantly extract your skills, compute your ATS score breakdown, highlight your strengths & weaknesses, and match you with active job openings!",
                "category": "Resume Analysis",
                "confidence": 1.0,
                "confidence_level": "high",
                "source": "resume_guide"
            }
        else:
            score = resume.get("score", 0)
            skills = ", ".join(resume.get("skills", [])[:8])
            return {
                "success": True,
                "answer": f"📊 **Current Resume Analysis Overview for `{resume.get('filename', 'your file')}`**\n\n- **Overall ATS Score:** **{score}/100**\n- **Skills Detected ({resume.get('skill_count', 0)}):** {skills}\n- **Strengths:** {'; '.join(resume.get('strengths', ['Solid skillset']))}\n\n*Would you like to explore matching jobs, interview practice questions, or actionable suggestions to improve this score?*",
                "category": "Resume Analysis",
                "confidence": 1.0,
                "confidence_level": "high",
                "source": "resume_memory"
            }

    # 2. Strengths & Weaknesses
    if any(k in msg for k in ["strength", "weakness", "strong point", "weak point", "pros and cons", "areas of improvement", "where am i lacking"]):
        if resume:
            strengths_list = "\n".join([f"• ✅ **{s}**" for s in resume.get("strengths", ["Solid technical foundation"])])
            weaknesses_list = "\n".join([f"• ⚠️ **{w}**" for w in resume.get("weaknesses", ["Minor keyword optimization"])])
            suggestions_list = "\n".join([f"• 💡 {s}" for s in resume.get("suggestions", [])[:3]])
            
            ans = f"📋 **Profile Strengths & Growth Areas for `{resume.get('filename', 'your resume')}`**:\n\n**Top Strengths:**\n{strengths_list}\n\n**Areas for Enhancement:**\n{weaknesses_list}\n\n**Key Action Items:**\n{suggestions_list}"
            return {
                "success": True,
                "answer": ans,
                "category": "Resume Evaluation",
                "confidence": 0.98,
                "confidence_level": "high",
                "source": "resume_memory"
            }
        else:
            return {
                "success": True,
                "answer": "To evaluate your personalized strengths and weaknesses, please upload your resume (**PDF or DOCX**) using the attachment button (📎) or drag & drop it into the chat!",
                "category": "Resume Evaluation",
                "confidence": 0.95,
                "confidence_level": "high",
                "source": "resume_guide"
            }

    # 3. Improvement suggestions & ATS score boost
    if any(k in msg for k in ["improve my score", "improve score", "increase score", "how to improve ats", "boost score", "improve my resume", "how can i improve"]):
        if resume:
            suggestions = resume.get("suggestions", [])
            missing = resume.get("missing_skills", [])
            sug_text = "\n".join([f"{i+1}. **{s}**" for i, s in enumerate(suggestions)])
            missing_text = f"\n\n**In-Demand Market Skills to Consider Adding:**\n`{', '.join(missing)}`" if missing else ""
            ans = f"🚀 **Actionable Recommendations to Boost Your ATS Score ({resume.get('score', 0)}/100):**\n\n{sug_text}{missing_text}\n\n💡 *Tip: Quantifying results with percentages, time saved, or team sizes dramatically improves recruiter and ATS engagement!*"
            return {
                "success": True,
                "answer": ans,
                "category": "Resume Optimization",
                "confidence": 0.98,
                "confidence_level": "high",
                "source": "resume_memory"
            }
        else:
            return {
                "success": True,
                "answer": "To receive tailored tips on boosting your ATS score, please upload your resume (PDF/DOCX). Generally, ensuring clear standard section headers, including measurable achievements, and matching keywords to job postings will raise your score.",
                "category": "Resume Optimization",
                "confidence": 0.92,
                "confidence_level": "high",
                "source": "resume_guide"
            }

    # 4. Find suitable jobs
    if any(k in msg for k in ["find suitable jobs", "suitable jobs", "matching jobs", "jobs for me", "job matches", "find jobs", "recommend jobs", "job recommendations", "jobs match"]):
        if resume:
            recs = resume.get("recommendations")
            if not recs:
                skills = resume.get("skills", [])
                recs = job_recommender.recommend_jobs(" ".join(skills), skills, top_n=3)
            
            if recs:
                jobs_formatted = []
                for j in recs[:3]:
                    match_p = j.get("match_percentage", int(j.get("similarity", 0.5) * 100))
                    matched_s = ", ".join(j.get("matched_skills", [])[:4]) or "Core skills"
                    jobs_formatted.append(f"• 💼 **{j.get('title')}** ({j.get('department')} • {j.get('location')})\n  - **Match:** {match_p}% alignment\n  - **Matched Skills:** {matched_s}")
                
                ans = f"🎯 **Top Matching Positions Based on Your Profile:**\n\n" + "\n\n".join(jobs_formatted) + "\n\nExplore full details and live job applications in the Job Directory below!"
                return {
                    "success": True,
                    "answer": ans,
                    "category": "Job Recommendation",
                    "confidence": 0.98,
                    "confidence_level": "high",
                    "source": "resume_memory"
                }
            else:
                return {
                    "success": True,
                    "answer": "I analyzed your profile, but did not find an exact match in our current open positions. You can explore all available roles in the Job Directory section below.",
                    "category": "Job Recommendation",
                    "confidence": 0.90,
                    "confidence_level": "high",
                    "source": "resume_memory"
                }
        else:
            return {
                "success": True,
                "answer": "💼 **Find Your Ideal Role**\n\nPlease attach or drag & drop your resume (**PDF or DOCX**) so I can compare your specific technical skills against active listings using NLP matching! You can also search all active openings directly in the Job Directory section below.",
                "category": "Job Recommendation",
                "confidence": 0.95,
                "confidence_level": "high",
                "source": "resume_guide"
            }

    # 5. Interview preparation
    if any(k in msg for k in ["prepare for an interview", "prepare for interview", "interview prep", "interview questions", "mock interview", "interview practice"]):
        if resume:
            skills = resume.get("skills", [])
            primary_skills = skills[:4] if skills else ["General Software Engineering", "Problem Solving"]
            
            questions = [
                f"1. **Core Technical:** 'Can you describe an end-to-end project where you utilized **{primary_skills[0]}**? What architectural trade-offs did you make?'",
                f"2. **Problem Solving:** 'Tell me about a complex bug or performance bottleneck you resolved when working with **{primary_skills[min(1, len(primary_skills)-1)]}**.'",
                "3. **Collaboration & Impact:** 'How do you handle scope changes or tight deadlines when coordinating with cross-functional teams?'",
                "4. **System Design & Quality:** 'How do you ensure automated test coverage, maintainability, and security in your codebases?'"
            ]
            ans = f"🎤 **Personalized Interview Preparation for Your Skillset ({', '.join(primary_skills)}):**\n\n" + "\n\n".join(questions) + "\n\n💡 *Would you like sample answers or behavioral STAR-method coaching for any of these questions?*"
            return {
                "success": True,
                "answer": ans,
                "category": "Interview Preparation",
                "confidence": 0.98,
                "confidence_level": "high",
                "source": "resume_memory"
            }
        else:
            return {
                "success": True,
                "answer": "🎤 **Interview Preparation Guide**\n\nI can generate tailored technical and situational questions based on your specific skills! Please upload your resume for personalized practice questions.\n\n**Key General HR Questions to Practice:**\n1. *'Walk me through a challenging project and the quantifiable outcome you achieved.'*\n2. *'How do you prioritize competing deadlines under tight schedules?'*\n3. *'Why are you interested in this position and our organization?'*",
                "category": "Interview Preparation",
                "confidence": 0.95,
                "confidence_level": "high",
                "source": "interview_guide"
            }

    # 6. Skills to learn
    if any(k in msg for k in ["what skills should i learn", "skills to learn", "what skills to learn", "future skills", "which skill should i learn", "skill roadmap"]):
        if resume:
            missing = resume.get("missing_skills", [])
            if not missing:
                missing = ["Docker", "Kubernetes", "AWS", "CI/CD", "System Design"]
            
            ans = f"🚀 **Strategic Skills Roadmap for Your Profile:**\n\nBased on current market demands and your existing skillset, adding these high-leverage skills will significantly elevate your marketability:\n\n"
            for s in missing[:5]:
                ans += f"• 🔹 **{s}** — Highly requested across senior engineering and data roles.\n"
            ans += f"\n💡 *Mastering these skills will expand your job match percentage across top-tier listings!*"
            return {
                "success": True,
                "answer": ans,
                "category": "Skill Development",
                "confidence": 0.98,
                "confidence_level": "high",
                "source": "resume_memory"
            }
        else:
            return {
                "success": True,
                "answer": "🚀 **Top High-Demand Industry Skills in 2026:**\n\n1. **Cloud & DevOps:** AWS, Azure, Docker, Kubernetes, CI/CD pipelines\n2. **Modern Backend & APIs:** Python (FastAPI/Flask), Go, Node.js, GraphQL\n3. **Data & AI:** SQL, Machine Learning, NLP, Vector Embeddings, LLM Orchestration\n4. **Frontend:** React, Next.js, TypeScript, Tailwind CSS\n\n*Upload your resume to get a custom gap analysis showing exactly what you should learn next!*",
                "category": "Skill Development",
                "confidence": 0.95,
                "confidence_level": "high",
                "source": "skill_guide"
            }

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
            try:
                _sem_model = SentenceTransformer('all-MiniLM-L6-v2')
                _sem_mat = _sem_model.encode(questions_raw, convert_to_numpy=True)
            except Exception as e:
                print(f"Notice: SentenceTransformer offline/disabled: {e}")
                _sem_model = None
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
    Process user query through conversational intents, resume intelligence, and hybrid NLP FAQ pipeline.
    """
    raw_query = str(question or "").strip()
    if not raw_query:
        return {
            "success": False,
            "answer": "Please provide a valid question or upload a resume to analyze.",
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

    # Layer 2: Active Session Resume Context & Specialized Intent Routing
    resume_ctx = get_session_resume(session_id)
    resume_response = _handle_resume_intent(raw_query, resume_ctx)
    if resume_response:
        return resume_response

    if _faq_df is None:
        return {
            "success": False,
            "answer": "Chatbot is currently unavailable due to an initialization error.",
            "category": "Error",
            "confidence": 0.0,
            "confidence_level": "low",
            "source": "system"
        }

    # Preprocess text
    processed_q = data_processor.preprocess_text(raw_query)
    cleaned_q = data_processor.clean_text(raw_query)

    if not processed_q and not cleaned_q:
        return {
            "success": True,
            "answer": "I couldn't understand your question. Could you rephrase it or upload your resume?",
            "category": "Unknown",
            "confidence": 0.0,
            "confidence_level": "low",
            "matched_question": None,
            "source": "fallback"
        }

    # Layer 3: Hybrid Retrieval (Word TF-IDF, Char TF-IDF, Semantic)
    word_q = _word_vec.transform([processed_q])
    char_q = _char_vec.transform([processed_q])

    sim_word = cosine_similarity(word_q, _word_mat).flatten()
    sim_char = cosine_similarity(char_q, _char_mat).flatten()

    if _sem_model is not None:
        sem_q = _sem_model.encode([cleaned_q], convert_to_numpy=True)
        sim_sem = cosine_similarity(sem_q, _sem_mat).flatten()
    else:
        sim_sem = np.zeros_like(sim_word)

    # Hybrid weights
    w_sem = 0.65 if _sem_model is not None else 0.0
    w_word = 0.20 if _sem_model is not None else 0.60
    w_char = 0.15 if _sem_model is not None else 0.40

    hybrid_scores = (w_sem * sim_sem) + (w_word * sim_word) + (w_char * sim_char)

    # Layer 4: Contextual Session Memory Boost
    ctx = _session_context.get(session_id, {})
    last_cat = ctx.get("last_category")
    last_time = ctx.get("last_time", 0)

    # Apply 15% contextual boost if query is short (<= 6 words) and last interaction was < 5 mins ago
    query_word_count = len(cleaned_q.split())
    if last_cat and (time.time() - last_time < 300) and query_word_count <= 6:
        for i, cat in enumerate(_faq_df["category"]):
            if cat == last_cat:
                hybrid_scores[i] *= 1.15

    # Layer 5: Ranking & Top-K Gap Analysis
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
        if session_id not in _session_context:
            _session_context[session_id] = {}
        _session_context[session_id]["last_category"] = matched_cat
        _session_context[session_id]["last_time"] = time.time()
        _session_context[session_id]["last_question"] = matched_q

    # Layer 6: Calibrated Confidence Thresholding
    if best_score >= 0.60 or (best_score >= 0.52 and score_gap >= 0.15):
        level = "high"
        answer = matched_ans
        source = "hr_faq"
    elif best_score >= 0.35:
        level = "medium"
        answer = f"I'm not entirely sure, but here is what I found: {matched_ans}"
        source = "hr_faq"
    else:
        level = "low"
        answer = "I'm sorry, I don't have an exact policy match for that in my HR database. You can rephrase, ask about leaves, payroll, or benefits, or contact HR directly."
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

