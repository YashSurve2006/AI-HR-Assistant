"""Resume analysis module — PDF extraction and skill extraction."""

import os
import re
# pyrefly: ignore [missing-import]
import pdfplumber

# A predefined dictionary of skills to extract
SKILLS_DB = [
    "Python", "Java", "JavaScript", "React", "Node.js", "Express", "SQL", "MySQL",
    "Oracle", "MongoDB", "HTML", "CSS", "Flask", "Django", "Pandas", "NumPy",
    "Scikit-learn", "Machine Learning", "NLP", "Git", "Docker", "AWS", "Azure",
    "Linux", "Networking", "Cisco", "Excel", "Power BI", "Tableau",
    "C++", "C#", "Ruby", "PHP", "Swift", "Kotlin", "Go", "Rust", "TypeScript"
]

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""
    return text

def preprocess_resume_text(text: str) -> str:
    """Clean and preprocess resume text."""
    # Convert to lowercase
    text = text.lower()
    # Replace newlines and multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_skills(text: str) -> list:
    """Extract technical and professional skills from text."""
    found_skills = set()
    
    for skill in SKILLS_DB:
        skill_lower = skill.lower()
        escaped_skill = re.escape(skill_lower)
        
        # Determine word boundaries depending on whether the skill starts/ends with alphanumeric
        prefix = r'\b' if re.match(r'^\w', skill_lower) else r'(?:\s|^)'
        suffix = r'\b' if re.match(r'\w$', skill_lower) else r'(?:\s|$|[.,;!?)])'
        
        pattern = f"{prefix}{escaped_skill}{suffix}"
        
        if re.search(pattern, text):
            found_skills.add(skill)
            
    return list(found_skills)

EXPERIENCE_KEYWORDS = ["experience", "work", "employment", "internship", "job", "career", "history", "years", "role"]
EDUCATION_KEYWORDS = ["education", "degree", "university", "college", "bachelor", "master", "phd", "btech", "mtech", "bs", "ms", "gpa", "academic", "institute"]
PROJECTS_KEYWORDS = ["project", "developed", "built", "created", "led", "managed", "achieved", "award", "accomplishment", "certification", "certified", "implemented"]

def count_keywords(text: str, keywords: list) -> int:
    """Count occurrences of keywords in text using word boundaries where possible."""
    count = 0
    for kw in keywords:
        # Simple count for ease of exact matching, 
        # though regex with word boundaries is more accurate.
        # To handle words properly, we can pad text with spaces:
        padded_text = f" {text} "
        count += padded_text.count(f" {kw} ")
    return count

def calculate_score(text: str, skills: list) -> dict:
    """Calculate resume score based on various components (0-100)."""
    # 1. Skills Score (max 25)
    # Give 3 points per skill, maxing out at 25
    skills_score = min(25, len(skills) * 3)
    
    # 2. Experience Score (max 25)
    exp_count = count_keywords(text, EXPERIENCE_KEYWORDS)
    experience_score = min(25, exp_count * 5)
    
    # 3. Education Score (max 20)
    edu_count = count_keywords(text, EDUCATION_KEYWORDS)
    education_score = min(20, edu_count * 5)
    
    # 4. Projects & Achievements Score (max 15)
    proj_count = count_keywords(text, PROJECTS_KEYWORDS)
    projects_score = min(15, proj_count * 3)
    
    # 5. Content Quality Score (max 15)
    # Base on text length - decent resume should have a good amount of text
    length = len(text)
    if length > 2000:
        content_quality = 15
    elif length > 1000:
        content_quality = 12
    elif length > 500:
        content_quality = 8
    elif length > 200:
        content_quality = 5
    else:
        content_quality = 2
        
    final_score = skills_score + experience_score + education_score + projects_score + content_quality
    
    return {
        "score": final_score,
        "breakdown": {
            "skills": skills_score,
            "experience": experience_score,
            "education": education_score,
            "projects": projects_score,
            "content_quality": content_quality
        }
    }

def analyze_resume(file_path: str) -> dict:
    """Analyze a resume PDF and return extracted text details, skills, and score."""
    text = extract_text_from_pdf(file_path)
    
    if not text.strip():
        return {
            "success": False,
            "error": "Could not extract text from the PDF. It might be an image-based PDF or corrupted."
        }
        
    cleaned_text = preprocess_resume_text(text)
    skills = extract_skills(cleaned_text)
    
    scoring = calculate_score(cleaned_text, skills)
    
    return {
        "success": True,
        "filename": os.path.basename(file_path),
        "text_length": len(text),
        "skills": sorted(skills),
        "skill_count": len(skills),
        "score": scoring["score"],
        "score_breakdown": scoring["breakdown"]
    }
