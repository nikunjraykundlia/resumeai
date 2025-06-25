"""
API Module for Resume Analysis - Optimized version
Provides functions for text extraction, skills identification, and ATS scoring
"""
import pdfplumber
import logging
import re
from difflib import SequenceMatcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to load spaCy
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
    except Exception as e:
        logger.warning(f"Error loading spaCy model: {e}")
        logger.warning("Try running: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
except ImportError:
    logger.warning("spaCy not available, using fallback functionality")
    SPACY_AVAILABLE = False

# Default skills list for matching
SKILLS_LIST = [
    "python", "java", "javascript", "html", "css", "react", "angular", "vue", 
    "node.js", "express", "django", "flask", "spring", "mysql", "postgresql", 
    "mongodb", "firebase", "aws", "azure", "docker", "git", "github", 
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", 
    "machine learning", "deep learning", "rest api", "flutter", "sql", 
    "cybersecurity", "junit", "wiremock", "apache httpclient", 
    "reinforcement learning", "openai gym", "rllib", "xgboost", "lightgbm", "fastai"
]

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_skills_regex(text, skills_list=None):
    """
    Extract skills by directly matching against the skills list.
    
    Args:
        text (str): Text to extract skills from
        skills_list (list): Optional custom skills list
        
    Returns:
        list: Extracted skills
    """
    if not text:
        return []
        
    # Use provided skills list or default
    skills_to_check = skills_list or SKILLS_LIST
    extracted_skills = set()
    text_lower = text.lower()
    
    # Match skills using regex with word boundaries
    for skill in skills_to_check:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            extracted_skills.add(skill)
    
    return list(extracted_skills)

def fuzzy_match(keyword, text_word, threshold=0.8):
    """
    Return True if keyword and text_word are similar above threshold.
    
    Args:
        keyword (str): Keyword to match
        text_word (str): Word to match against
        threshold (float): Similarity threshold (0.0-1.0)
        
    Returns:
        bool: True if match found
    """
    try:
        # Quick exact match check
        if keyword.lower() == text_word.lower():
            return True
            
        # Quick contains check for longer keywords
        if len(keyword) > 3 and (keyword.lower() in text_word.lower() or text_word.lower() in keyword.lower()):
            return True
            
        # Skip sequence matcher for very long strings to prevent timeouts
        if len(keyword) > 20 or len(text_word) > 20:
            return False
            
        # Use sequence matcher for closer matches
        ratio = SequenceMatcher(None, keyword.lower(), text_word.lower()).ratio()
        return ratio >= threshold
    except Exception as e:
        logger.error(f"Error in fuzzy matching: {e}")
        return False

def calculate_ats_score(resume_skills, job_description, threshold=0.8):
    """
    Compute ATS score by comparing resume skills to keywords from the job description.
    Returns the score and detailed matching information.
    
    Args:
        resume_skills (list): List of skills extracted from resume
        job_description (str): Job description text
        threshold (float): Similarity matching threshold
        
    Returns:
        dict: Contains score, matched keywords count, and total keywords count
    """
    try:
        # Safety checks
        if not resume_skills or not job_description:
            return {"score": 0, "matched": 0, "total": 0, "matched_keywords": []}
            
        # Ensure resume_skills is a list
        if isinstance(resume_skills, str):
            resume_skills = [resume_skills]
            
        # Limit input size
        job_description = job_description[:3000] if job_description else ""
        
        # Process job tokens based on spaCy availability
        if SPACY_AVAILABLE:
            # Get tokens using spaCy
            job_doc = nlp(job_description.lower())
            job_tokens = [token.text for token in job_doc if token.is_alpha and len(token.text) > 2]
        else:
            # Fallback method using regex
            job_tokens = re.findall(r'\b[a-z][a-z0-9]{2,19}\b', job_description.lower())
        
        # Remove duplicates and limit token count
        job_tokens = list(set(job_tokens))[:200]
        
        if not job_tokens:
            return {"score": 0, "matched": 0, "total": 0, "matched_keywords": []}
        
        # Count matches and track matched keywords
        match_count = 0
        matched_keywords = []
        
        for job_token in job_tokens:
            for skill in resume_skills:
                if fuzzy_match(job_token, skill, threshold):
                    match_count += 1
                    matched_keywords.append(job_token)
                    break  # Count one match per job token
        
        # Calculate score
        ats_score = (match_count / len(job_tokens)) * 100
        
        return {
            "score": round(ats_score, 2),
            "matched": match_count,  # M value
            "total": len(job_tokens),  # T value
            "matched_keywords": matched_keywords
        }
    
    except Exception as e:
        logger.error(f"Error calculating ATS score: {e}")
        return {"score": 0, "matched": 0, "total": 0, "matched_keywords": []}
        
def get_role_specific_ats_scores(resume_text, job_titles, job_descriptions):
    """
    Calculate role-specific ATS scores for multiple job descriptions.
    
    Args:
        resume_text (str): The resume text
        job_titles (list): List of job titles
        job_descriptions (list): List of job descriptions
        
    Returns:
        dict: Job titles mapped to ATS scores
    """
    # Extract skills from resume
    skills = extract_skills_regex(resume_text)
    
    # Calculate scores for each job
    role_scores = {}
    
    for i, (title, description) in enumerate(zip(job_titles, job_descriptions)):
        if i >= len(job_titles) or i >= len(job_descriptions):
            break
            
        # Calculate ATS score
        score_result = calculate_ats_score(skills, description)
        role_scores[title] = score_result["score"]
        
    return role_scores

def analyze_resume(pdf_path=None, resume_text=None):
    """
    Analyze a resume from either PDF path or text.
    
    Args:
        pdf_path (str): Path to PDF file (optional)
        resume_text (str): Resume text (optional)
        
    Returns:
        dict: Analysis results including skills, education, experience, etc.
    """
    # Get resume text
    if pdf_path and not resume_text:
        resume_text = extract_text_from_pdf(pdf_path)
    elif not resume_text:
        return {"error": "No resume provided"}
        
    # Extract skills
    skills = extract_skills_regex(resume_text)
    
    # Basic sections extraction
    sections = {}
    
    # Try to extract education
    education_pattern = r'(?i)(education|academics).*?(experience|skills|projects|achievements)'
    education_match = re.search(education_pattern, resume_text, re.DOTALL)
    if education_match:
        sections["education"] = education_match.group(0).strip()
        
    # Try to extract experience
    experience_pattern = r'(?i)(experience|work).*?(education|skills|projects|achievements)'
    experience_match = re.search(experience_pattern, resume_text, re.DOTALL)
    if experience_match:
        sections["experience"] = experience_match.group(0).strip()
        
    # Try to extract projects
    projects_pattern = r'(?i)(projects|personal projects).*?(experience|education|skills|achievements)'
    projects_match = re.search(projects_pattern, resume_text, re.DOTALL)
    if projects_match:
        sections["projects"] = projects_match.group(0).strip()
    
    # Result dictionary
    result = {
        "skills": skills,
        "num_skills": len(skills),
        "sections": sections,
        "text_length": len(resume_text)
    }
    
    return result

# Test function
def test_ats_scoring():
    """Run a test ATS scoring"""
    resume_text = """
    Experienced full stack developer with expertise in React, Node.js, and MongoDB.
    I have worked with RESTful APIs, Docker, and Git version control.
    Experience with AWS cloud services.
    """
    
    job_description = """
    We are looking for a Full Stack Developer experienced in React, Node.js, and MongoDB. 
    The candidate should also have working knowledge of RESTful APIs, Docker, Git, 
    and be familiar with cloud platforms like AWS.
    """
    
    # Extract skills
    skills = extract_skills_regex(resume_text)
    print(f"Extracted skills: {skills}")
    
    # Calculate ATS score
    score_result = calculate_ats_score(skills, job_description)
    print(f"ATS Score: {score_result['score']}%")
    print(f"Matched Keywords: {score_result['matched']}/{score_result['total']}")
    
    return score_result

if __name__ == "__main__":
    # Run test
    test_ats_scoring()