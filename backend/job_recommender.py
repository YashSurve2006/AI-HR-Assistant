"""Job recommendation module — TF-IDF based matching and skill gap analysis."""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import data_processor as dp
import job_platforms

# Cache for loaded data and models
_jobs_df = None
_vectorizer = None
_tfidf_matrix = None

def load_job_data():
    """Load job dataset and prepare TF-IDF matrix."""
    global _jobs_df, _vectorizer, _tfidf_matrix
    if _jobs_df is None:
        _jobs_df = dp.load_jobs(preprocess=True)
        
        def combine_text(row):
            title = str(row.get('title', ''))
            desc = str(row.get('description_processed', row.get('description', '')))
            skills = str(row.get('required_skills_processed', row.get('required_skills', '')))
            return f"{title} {desc} {skills}".lower()
            
        _jobs_df['combined_text'] = _jobs_df.apply(combine_text, axis=1)
        
        _vectorizer = TfidfVectorizer(stop_words='english')
        _tfidf_matrix = _vectorizer.fit_transform(_jobs_df['combined_text'])
        
    return _jobs_df, _vectorizer, _tfidf_matrix

def calculate_skill_gap(resume_skills: list, required_skills_str: str) -> dict:
    """Compare resume skills with required skills to find gaps."""
    if not required_skills_str or pd.isna(required_skills_str) or str(required_skills_str).lower() == "nan":
        return {"matched_skills": [], "missing_skills": [], "match_percentage": 0}
        
    req_skills = [s.strip() for s in str(required_skills_str).split(",") if s.strip()]
    res_skills_lower = [s.lower() for s in resume_skills]
    
    matched = []
    missing = []
    
    for rs in req_skills:
        rs_lower = rs.lower()
        found = False
        for ms in res_skills_lower:
            if rs_lower == ms or rs_lower in ms or ms in rs_lower:
                found = True
                break
        if found:
            matched.append(rs)
        else:
            missing.append(rs)
            
    match_percentage = int((len(matched) / len(req_skills)) * 100) if req_skills else 0
    
    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_percentage
    }

def recommend_jobs(resume_text: str, resume_skills: list, top_n: int = 5) -> list:
    """Recommend job roles based on candidate resume text and skills using TF-IDF."""
    df, vectorizer, tfidf_matrix = load_job_data()
    
    # Preprocess resume text using the data_processor logic
    resume_processed = dp.preprocess_text(resume_text)
    
    # Vectorize resume
    resume_vec = vectorizer.transform([resume_processed])
    
    # Calculate similarity
    sim_scores = cosine_similarity(resume_vec, tfidf_matrix).flatten()
    
    # Get top indices
    top_indices = sim_scores.argsort()[::-1][:top_n]
    
    recommendations = []
    for idx in top_indices:
        job = df.iloc[idx]
        sim = float(sim_scores[idx])
        req_skills_str = str(job['required_skills'])
        
        gap = calculate_skill_gap(resume_skills, req_skills_str)
        
        links = job_platforms.generate_job_platform_links(str(job['title']), str(job['location']))
        
        recommendations.append({
            "job_id": int(job['job_id']),
            "title": str(job['title']),
            "department": str(job['department']),
            "location": str(job['location']),
            "similarity": round(sim, 4),
            "required_skills": req_skills_str,
            "matched_skills": gap["matched_skills"],
            "missing_skills": gap["missing_skills"],
            "match_percentage": gap["match_percentage"],
            "platform_links": links
        })
        
    return recommendations
