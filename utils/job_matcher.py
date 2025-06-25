"""
Optimized job matching module for resume analysis
"""
import logging
import re
import pandas as pd
from utils.ats_scorer import calculate_ats_score, calculate_resume_job_similarity
from utils.advanced_analyzer import calculate_job_match_scores

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TF-IDF is expensive, so try to import it but have a fallback
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    TFIDF_AVAILABLE = True
except ImportError:
    logger.warning("sklearn TfidfVectorizer not available, using fallback scoring only")
    TFIDF_AVAILABLE = False

def extract_skills_from_text(resume_text):
    """Extract potential skills from text using simple regex"""
    skills = re.findall(r'\b[A-Za-z][A-Za-z0-9\+\#\.]+\b', resume_text.lower())
    return list(set([s for s in skills if len(s) > 3]))[:100]  # Limit to 100 skills max

def find_matching_jobs(resume_text, job_df, skills=None, top_n=5):
    """Find jobs matching a resume based on ATS scoring and TF-IDF similarity - limited to 5 jobs maximum"""
    try:
        # Input validation with early return
        if not resume_text or job_df.empty:
            return []
            
        # Limit text size to prevent timeouts
        resume_text = resume_text[:5000]
        
        # Extract data from DataFrame
        # Normalize column names to match CSV
        job_df.columns = job_df.columns.str.lower()
        job_titles = job_df['job_title'].tolist()[:50]  # Limit to 50 jobs
        job_descriptions = job_df['description'].tolist()[:50]
        
        # Extract or use provided skills
        skills = skills or extract_skills_from_text(resume_text)
        
        # Calculate ATS scores for each job
        ats_scores = []
        ats_details = []
        
        for i, job_desc in enumerate(job_descriptions):
            # Limit description size
            job_desc = job_desc[:2000] if job_desc else ""
            result = calculate_ats_score(skills, job_desc)
            ats_scores.append(result['score'])
            ats_details.append(result)
            logger.info(f"Job '{job_titles[i]}' ATS Score: {result['score']}%")
        
        # Try to use TF-IDF for better matching if available
        combined_scores = ats_scores
        if TFIDF_AVAILABLE and len(job_descriptions) > 0:
            try:
                # Simple TF-IDF calculation with basic error handling
                vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
                tfidf_matrix = vectorizer.fit_transform([resume_text] + job_descriptions)
                resume_vector = tfidf_matrix[0]
                
                # Calculate similarities
                tfidf_scores = []
                for i in range(1, tfidf_matrix.shape[0]):
                    job_vector = tfidf_matrix[i]
                    # Calculate cosine similarity
                    similarity = float((resume_vector * job_vector.T).toarray()[0, 0])
                    # Normalize (avoid division by zero)
                    norm_product = float(resume_vector.sum() * job_vector.sum())
                    if norm_product > 0:
                        similarity /= norm_product
                    tfidf_scores.append(similarity * 100)  # Convert to percentage
                
                        # NEW ALGORITHM: More variable and resume-specific scores to differentiate job titles
                # This creates a wider spread between best matches and others for clearer recommendations
                # First step - calculate raw scores with minimal boosting to preserve job relevance order
                raw_ats_scores = [min(100, max(40, a * 5)) for a in ats_scores]
                raw_tfidf_scores = [min(100, max(40, t * 5)) for t in tfidf_scores]
                
                # Combine raw scores with original ratio, preserving true differences
                raw_combined = [(a * 0.7) + (t * 0.3) for a, t in zip(raw_ats_scores, raw_tfidf_scores)]
                
                # Create wider spacing between scores for better visual differentiation
                # Top score will be boosted highest, with progressively less boost for lower scores
                sorted_indices = sorted(range(len(raw_combined)), key=lambda i: raw_combined[i], reverse=True)
                
                # Create truly variable recommendation scores
                combined_scores = [0] * len(raw_combined)
                for rank, idx in enumerate(sorted_indices):
                    if rank == 0:  # Top match gets highest score (85-95%)
                        combined_scores[idx] = min(95, max(85, raw_combined[idx] * 1.2))
                    elif rank == 1:  # Second match (80-90%)
                        combined_scores[idx] = min(90, max(80, raw_combined[idx] * 1.1))
                    elif rank == 2:  # Third match (75-85%)
                        combined_scores[idx] = min(85, max(75, raw_combined[idx] * 1.0))
                    elif rank == 3:  # Fourth match (70-80%) 
                        combined_scores[idx] = min(80, max(70, raw_combined[idx] * 0.9))
                    else:  # Remaining matches (65-75%)
                        combined_scores[idx] = min(75, max(65, raw_combined[idx] * 0.8))
            except Exception as e:
                logger.warning(f"TF-IDF calculation failed: {str(e)}")
        
        # Build job score dictionary and deduplicate
        job_data = {}
        for i, title in enumerate(job_titles):
            score = combined_scores[i] if i < len(combined_scores) else 0
            if title not in job_data or score > job_data[title]['score']:
                job_data[title] = {
                    'score': score,
                    'description': job_descriptions[i],
                    'ats_details': ats_details[i] if i < len(ats_details) else {}
                }
        
        # Sort and return top matches
        ranked_jobs = sorted(job_data.items(), key=lambda x: x[1]['score'], reverse=True)[:top_n]
        return [(title, data['score'], data['description'], data['ats_details']) 
                for title, data in ranked_jobs]

    except Exception as e:
        logger.error(f"Job matching error: {str(e)}")
        # Simple fallback
        try:
            # Get job scores but boost them dramatically
            job_scores = calculate_job_match_scores(resume_text, None)
            
            # Create variable scores with better differentiation even in fallback
            raw_scores = {}
            for title, score in job_scores.items():
                # Preserve actual score differences but shift to higher range
                raw_scores[title] = 50 + min(50, score * 10)
                
            # Sort by raw scores to get ranking
            ranked_jobs = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Apply different score ranges based on rank position
            boosted_scores = {}
            for rank, (title, score) in enumerate(ranked_jobs):
                if rank == 0:  # Top match (85-95%)
                    boosted_scores[title] = min(95, max(85, score * 1.2))
                elif rank == 1:  # Second match (80-90%)
                    boosted_scores[title] = min(90, max(80, score * 1.1))
                elif rank == 2:  # Third match (75-85%)
                    boosted_scores[title] = min(85, max(75, score))
                elif rank == 3:  # Fourth match (70-80%)
                    boosted_scores[title] = min(80, max(70, score * 0.9))
                else:  # Remaining matches (65-75%)
                    boosted_scores[title] = min(75, max(65, score * 0.8))
            
            # Return top matches with the boosted scores
            top_jobs = sorted(boosted_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            return [(t, s, f"Role focusing on {t}", {'score': s}) for t, s in top_jobs]
        except:
            return []

def extract_job_requirements(job_description, max_req=5):
    """Extract key requirements from a job description"""
    if not job_description:
        return []

    # Limit text to process
    job_description = job_description[:1000]
    
    # Find requirements by looking for specific indicators
    indicators = ['required', 'must have', 'should have', 'experience in']
    sentences = job_description.split('.')
    requirements = []
    
    for sentence in sentences:
        if any(i in sentence.lower() for i in indicators):
            clean_sentence = sentence.strip()
            if clean_sentence and len(clean_sentence) > 10:
                requirements.append(clean_sentence[:100])  # Limit length
                
    return requirements[:max_req]  # Limit number of requirements

# ---------------------------------------------------------------------------
# Simple job-type recommender combining detected skills + distribution
# ---------------------------------------------------------------------------

CATEGORY_MAP = {
    "html": "Web Development",
    "css": "Web Development",
    "tailwind css": "Web Development",
    "react": "Web Development",
    "javascript": "Web Development",
    "python": "Programming",
    "java": "Programming",
    "c++": "Programming",
    "sql": "Database",
    "mongodb": "Database",
    "postgresql": "Database",
    "machine learning": "Data Science",
    "computer vision": "Data Science",
    "pandas": "Data Science",
}

ARCHETYPES = {
    "Web Development": ("Front-End / Full-Stack Web Developer", {"react", "html", "css", "tailwind css"}),
    "Programming": ("Full-Stack Developer (Python / Java)", {"python", "java", "sql"}),
    "Data Science": ("Data Scientist / ML Engineer", {"machine learning", "python", "sql"}),
    "Database": ("Backend API / DB Engineer", {"sql", "python", "java"}),
    "Others": ("Generalist Software Engineer", set()),
}

def _categorize_skills(skills: list[str]):
    buckets: dict[str, int] = {}
    for sk in skills:
        cat = CATEGORY_MAP.get(sk.lower(), "Others")
        buckets[cat] = buckets.get(cat, 0) + 1
    total = sum(buckets.values()) or 1
    return {cat: round(cnt * 100 / total) for cat, cnt in buckets.items()}

def suggest_job_types(detected: list[str], distribution: dict[str, int] | None = None, top_n: int = 5):
    """Return ranked job-type suggestions.
    Args:
        detected: list of skill strings
        distribution: optional pre-computed category percentage dict.
    """
    if distribution is None:
        distribution = _categorize_skills(detected)

    ranked_cats = sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:top_n]

    recommendations = []
    for rank, (cat, pct) in enumerate(ranked_cats, 1):
        title, core_skills = ARCHETYPES.get(cat, (f"{cat} Specialist", set()))
        matched = core_skills.intersection({s.lower() for s in detected})
        score = min(100, 60 + pct * 0.8 + len(matched) * 4)
        recommendations.append({
            "rank": rank,
            "title": title,
            "match_score": int(score),
            "matched_skills": sorted(matched),
            "keywords": " ".join(core_skills) if core_skills else " ".join(detected[:4])
        })
    return recommendations


def calculate_match_details(resume_text, job_description):
    """Calculate detailed matching metrics using efficient keyword matching"""
    # Default empty response
    empty_result = {
        'requirement_matches': [],
        'match_percentage': 0,
        'matched_count': 0,
        'total_count': 0
    }
    
    try:
        # Input validation
        if not resume_text or not job_description:
            return empty_result
            
        # Extract and limit requirements
        resume_text = resume_text[:3000].lower()
        requirements = extract_job_requirements(job_description, max_req=5)
        
        if not requirements:
            return empty_result
        
        # Calculate matches using keyword approach
        matches = []
        for req in requirements:
            # Find keywords in the requirement
            keywords = [w for w in re.findall(r'\b\w+\b', req.lower()) if len(w) > 3]
            if not keywords:
                continue
                
            # Check how many keywords appear in resume
            found = sum(1 for k in keywords if k in resume_text)
            score = found / len(keywords) if keywords else 0
            
            matches.append({
                'requirement': req,
                'match_score': score,
                'has_match': score > 0.3
            })
        
        # Overall statistics
        if not matches:
            return empty_result
            
        matched_count = sum(1 for m in matches if m['has_match'])
        
        return {
            'requirement_matches': matches,
            'match_percentage': (matched_count / len(matches)) * 100,
            'matched_count': matched_count,
            'total_count': len(matches)
        }
    except Exception as e:
        logger.error(f"Match calculation error: {str(e)}")
        return empty_result